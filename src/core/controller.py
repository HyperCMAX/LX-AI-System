# src/core/controller.py

from .models import (
    SystemFeedback, EventType, StateNode, 
    ArchitectOutput, DynamicCommandDefinition,
    CommandDefinition,
    MAX_EVENT_HISTORY_SIZE
)
from .registry import CommandRegistry
from .state_machine import StateMachine
from .parser import ResponseParser, ParserError
from .executor import CommandExecutor
from .logger import EventLogger
from .message_protocol import ModelAction, ModelActionType
from .prompt_templates import (
    SYSTEM_PROMPT_TEMPLATE, ARCHITECT_PROMPT_TEMPLATE,
    ARCHITECT_FORMAT_EXAMPLE, format_commands, format_events
)

from typing import Optional, List, Dict, Any
from datetime import datetime
import json

class SystemController:
    def __init__(self, initial_state_id: str):
        self.registry = CommandRegistry()
        self.state_machine = StateMachine(self.registry)
        self.executor = CommandExecutor()
        self.logger = EventLogger()
        self.parser = ResponseParser()
        self.initial_state_id = initial_state_id
        self.conversation_history: List[str] = []
        self.last_action: Optional[ModelAction] = None
        self.dynamic_command_ids: List[str] = []
        self.last_output: Optional[Dict[str, Any]] = None
        
        # 返回值追踪
        self.pending_returns: Dict[str, Dict] = {}
        self.return_counter: int = 0
        self.notified_returns: List[str] = []
        self.return_history: Dict[str, Dict] = {}

    def start(self):
        self.state_machine.transition_to(self.initial_state_id)
        self.logger.log(EventType.STATE_CHANGE, f"System started at {self.initial_state_id}")

    def _get_context_summary(self) -> str:
        from .project_manager import ProjectManager
        pm = ProjectManager()
        context_length = pm.get_context_length()
        recent_history = self.conversation_history[-context_length:]
        return "\n".join(recent_history)

    def _call_architect(self, user_input: str, all_commands: List[CommandDefinition]) -> Optional[ArchitectOutput]:
        from .config_manager import ConfigManager
        import requests
        
        config_mgr = ConfigManager()
        api_config = config_mgr.get_api_config()
        
        if not config_mgr.is_configured():
            return None
        
        all_commands_text = "\n".join([
            f"  - {cmd.id}: {cmd.description}"
            for cmd in all_commands
        ])
        
        current_state = self.state_machine.get_current_state()
        
        prompt = ARCHITECT_PROMPT_TEMPLATE.format(
            state_description=current_state.description if current_state else "未知",
            state_mode=current_state.mode if current_state else "stable",
            all_commands=all_commands_text,
            context_summary=self._get_context_summary(),
            user_input=user_input,
            format_example=ARCHITECT_FORMAT_EXAMPLE
        )
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_config.get('key')}"
        }
        payload = {
            "model": api_config.get("model"),
            "messages": [
                {"role": "system", "content": "你是系统架构师，负责从现有命令中选择和状态管理。输出严格 JSON。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        }
        
        try:
            response = requests.post(
                f"{api_config.get('base_url')}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            content = data['choices'][0]['message']['content']
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                json_str = content[start:end+1]
                return ArchitectOutput(**json.loads(json_str))
            return None
        except Exception as e:
            self.logger.log(EventType.SYSTEM_ERROR, f"Architect Error: {str(e)}")
            return None

    def process_user_input(self, user_input: str) -> SystemFeedback:
        current_state = self.state_machine.get_current_state()
        self.last_output = None
        
        if user_input.startswith("[RETURN]"):
            return self._process_return_submission(user_input)
        
        # 自由模式：调用架构师 AI
        if current_state and current_state.mode == "free":
            all_commands = list(self.registry.commands.values())
            
            architect_output = self._call_architect(user_input, all_commands)
            if architect_output:
                current_state.description = architect_output.current_state_description
                
                selected_cmd_ids = []
                for cmd_id in architect_output.selected_command_ids:
                    cmd = self.registry.get_command(cmd_id.lower())
                    if cmd:
                        selected_cmd_ids.append(cmd.id)
                
                current_state.available_command_ids = selected_cmd_ids
                
                if architect_output.suggest_new_state:
                    new_state_id = architect_output.suggest_new_state.lower()
                    if new_state_id not in self.state_machine.states:
                        new_state = StateNode(
                            id=new_state_id,
                            description=architect_output.current_state_description,
                            mode="free",
                            parent_id=current_state.id,
                            available_command_ids=selected_cmd_ids
                        )
                        self.state_machine.register_state(new_state)
                        self.logger.log(EventType.STATE_CHANGE, f"Architect created new state: {new_state_id}")
                
                if architect_output.suggest_state_change:
                    target_state = architect_output.suggest_state_change.lower()
                    if target_state in self.state_machine.states:
                        self.state_machine.transition_to(target_state)
                        self.logger.log(EventType.STATE_CHANGE, f"Architect transitioned to: {target_state}")
        
        # 构建系统反馈
        feedback = self._build_feedback()
        
        return_status = self._get_return_status_message()
        if return_status:
            user_input_with_status = f"{user_input}\n\n[系统返回值状态]\n{return_status}"
        else:
            user_input_with_status = user_input
        
        llm_response_text = self._call_llm(feedback, user_input_with_status)
        
        try:
            action = self.parser.parse(llm_response_text)
        except ParserError as e:
            self.logger.log(EventType.SYSTEM_ERROR, f"Parser Error: {e.message}")
            return self._build_feedback(error_only=True)
        
        self.last_action = action
        
        if action.action_type == ModelActionType.CALL_COMMAND:
            cmd = self.registry.get_command(action.command_id)
            if cmd:
                has_return = action.has_return if hasattr(action, 'has_return') else cmd.has_return
                wait_for_return = action.wait_for_return if hasattr(action, 'wait_for_return') else cmd.wait_for_return
                
                status, data = self.executor.execute(cmd, action.command_params)
                
                if status.value == "success":
                    self.logger.log(EventType.SYSTEM_SUCCESS, f"Command {cmd.id} executed", cmd.id)
                    
                    if isinstance(data, dict) and data.get("output_key"):
                        self.last_output = data
                    
                    if has_return:
                        self.return_counter += 1
                        return_id = f"ret_{self.return_counter}_{cmd.id}"
                        
                        from .project_manager import ProjectManager
                        pm = ProjectManager()
                        timeout = pm.get_command_timeout()
                        
                        if isinstance(data, dict) and data.get("auto_return", False):
                            return_info = {
                                "return_id": return_id,
                                "command_id": cmd.id,
                                "status": "completed",
                                "value": data,
                                "created": datetime.now().isoformat(),
                                "completed": datetime.now().isoformat(),
                                "timeout": timeout
                            }
                            self.pending_returns[cmd.id] = return_info
                            self.return_history[cmd.id] = return_info.copy()
                        elif wait_for_return:
                            return_info = {
                                "return_id": return_id,
                                "command_id": cmd.id,
                                "status": "waiting",
                                "value": None,
                                "created": datetime.now().isoformat(),
                                "completed": None,
                                "timeout": timeout
                            }
                            self.pending_returns[cmd.id] = return_info
                            self.return_history[cmd.id] = return_info.copy()
                        else:
                            return_info = {
                                "return_id": return_id,
                                "command_id": cmd.id,
                                "status": "pending",
                                "value": None,
                                "created": datetime.now().isoformat(),
                                "completed": None,
                                "timeout": timeout
                            }
                            self.pending_returns[cmd.id] = return_info
                            self.return_history[cmd.id] = return_info.copy()
                else:
                    self.logger.log(EventType.SYSTEM_ERROR, f"Command {cmd.id} failed: {data}", cmd.id)
            else:
                self.logger.log(EventType.SYSTEM_ERROR, f"Command {action.command_id} not found")
        
        elif action.action_type == ModelActionType.PROPOSE_COMMAND:
            self.logger.log(EventType.SYSTEM_SUCCESS, f"New command proposed: {action.proposed_command.id}")
        
        self.conversation_history.append(f"User: {user_input}")
        if action.response_to_user:
            self.conversation_history.append(f"Assistant: {action.response_to_user}")
        
        return self._build_feedback()

    def _get_return_status_message(self) -> str:
        if not self.pending_returns:
            return ""
        
        from .project_manager import ProjectManager
        pm = ProjectManager()
        current_time = datetime.now()
        timeout = pm.get_command_timeout()
        
        status_lines = []
        to_cleanup = []
        
        for cmd_id, info in self.pending_returns.items():
            if cmd_id in self.notified_returns:
                continue
            
            created = datetime.fromisoformat(info["created"])
            elapsed = (current_time - created).total_seconds()
            
            if info["status"] == "completed":
                value = info.get("value", {})
                if isinstance(value, dict):
                    if value.get("return_type") == "http_response":
                        summary = f"HTTP {value.get('status_code')}: {value.get('response_body', '')[:100]}"
                    elif value.get("return_type") == "command_output":
                        summary = f"输出：{value.get('stdout', '')[:100]}"
                    else:
                        summary = str(value)[:100]
                else:
                    summary = str(value)[:100]
                status_lines.append(f"  [已返回] {cmd_id}: {summary}")
                to_cleanup.append(cmd_id)
                
            elif info["status"] == "waiting":
                if elapsed >= timeout:
                    status_lines.append(f"  [等待超时] {cmd_id}: 超过{timeout}秒无返回值")
                    to_cleanup.append(cmd_id)
                else:
                    status_lines.append(f"  [等待中] {cmd_id}: 已等待{int(elapsed)}秒/{timeout}秒")
                    
            elif info["status"] == "pending":
                if elapsed >= timeout:
                    status_lines.append(f"  [已超时] {cmd_id}: 超过{timeout}秒无返回值")
                    to_cleanup.append(cmd_id)
                else:
                    status_lines.append(f"  [等待中] {cmd_id}: 已等待{int(elapsed)}秒/{timeout}秒")
        
        for cmd_id in to_cleanup:
            self.notified_returns.append(cmd_id)
            del self.pending_returns[cmd_id]
        
        if status_lines:
            return "\n".join(status_lines)
        return ""

    def _process_return_submission(self, user_input: str) -> SystemFeedback:
        try:
            parts = user_input[8:].split(":", 1)
            cmd_id = parts[0]
            return_value = parts[1] if len(parts) > 1 else None
            
            if cmd_id in self.pending_returns:
                self._submit_return(cmd_id, return_value)
                self.conversation_history.append(f"System: 已收到命令返回值：{cmd_id}")
                return self._build_feedback()
            else:
                self.logger.log(EventType.SYSTEM_ERROR, f"未知的命令 ID: {cmd_id}")
                return self._build_feedback(error_only=True)
        except Exception as e:
            self.logger.log(EventType.SYSTEM_ERROR, f"返回值提交失败：{e}")
            return self._build_feedback(error_only=True)

    def _submit_return(self, cmd_id: str, return_value: Any):
        if cmd_id not in self.pending_returns:
            return
        
        self.pending_returns[cmd_id]["status"] = "completed"
        self.pending_returns[cmd_id]["value"] = return_value
        self.pending_returns[cmd_id]["completed"] = datetime.now().isoformat()
        
        self.return_history[cmd_id] = self.pending_returns[cmd_id].copy()
        
        self.logger.log(EventType.SYSTEM_SUCCESS, f"收到返回值：{cmd_id}")

    def get_pending_returns(self) -> List[Dict]:
        return list(self.pending_returns.values())

    def get_return_history(self) -> List[Dict]:
        all_returns = {}
        all_returns.update(self.return_history)
        all_returns.update(self.pending_returns)
        return list(all_returns.values())

    def clear_completed_returns(self):
        completed = [cmd_id for cmd_id, info in self.pending_returns.items() 
                     if info["status"] == "completed"]
        for cmd_id in completed:
            if cmd_id in self.notified_returns:
                del self.pending_returns[cmd_id]
                self.notified_returns.remove(cmd_id)

    def get_last_response(self) -> Optional[str]:
        if self.last_action:
            return self.last_action.response_to_user
        return None

    def get_last_output(self) -> Optional[Dict[str, Any]]:
        return self.last_output

    def _call_llm(self, feedback: SystemFeedback, user_input: str) -> str:
        from .config_manager import ConfigManager
        import requests
        
        config_mgr = ConfigManager()
        api_config = config_mgr.get_api_config()
        
        if not config_mgr.is_configured():
            return json.dumps({
                "thought": "系统未配置 API",
                "action_type": "reply_only",
                "response_to_user": "错误：请先在 CLI 中配置 API Key 和地址。"
            })
        
        cmd_text = format_commands(feedback.disclosed_commands)
        evt_text = format_events(feedback.event_history)
        prompt = SYSTEM_PROMPT_TEMPLATE.format(
            state_description=feedback.current_state.description,
            state_mode=feedback.current_state.mode,
            commands_list=cmd_text,
            event_history=evt_text,
            user_input=user_input
        )
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_config.get('key')}"
        }
        
        payload = {
            "model": api_config.get("model"),
            "messages": [
                {"role": "system", "content": "你是一个状态驱动的智能助手。输出必须是严格的 JSON 格式。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{api_config.get('base_url')}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            content = data['choices'][0]['message']['content']
            return content
        except Exception as e:
            return json.dumps({
                "thought": "API 调用失败",
                "action_type": "reply_only",
                "response_to_user": f"系统错误：{str(e)}"
            })

    def _build_feedback(self, error_only: bool = False) -> SystemFeedback:
        """
        【关键修复】确保从 state_machine 获取披露的命令
        """
        current_state = self.state_machine.get_current_state()
        
        # ✅ 从 state_machine 获取，不是 registry
        disclosed_cmds = self.state_machine.get_disclosed_commands()
        
        history = self.logger.get_history()
        data = None
        
        return SystemFeedback(
            current_state=current_state,
            event_history=history,
            data_payload=data,
            disclosed_commands=disclosed_cmds
        )
