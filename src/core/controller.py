# src/core/controller.py

# 导入之前定义的所有核心组件
from .models import SystemFeedback, EventType, StateNode, ArchitectOutput, DynamicCommandDefinition
from .registry import CommandRegistry
from .state_machine import StateMachine
from .parser import ResponseParser, ParserError
from .executor import CommandExecutor
from .logger import EventLogger
from .message_protocol import ModelAction, ModelActionType, LLMRequest
from .prompt_templates import SYSTEM_PROMPT_TEMPLATE, ARCHITECT_PROMPT_TEMPLATE, ARCHITECT_FORMAT_EXAMPLE, \
    format_commands, format_events
# 导入 typing 用于类型提示
from typing import Optional, List, Dict, Any
# 导入 json 用于解析
import json


# 定义系统控制器类
class SystemController:
    # 含义：初始化方法，组装所有组件
    def __init__(self, initial_state_id: str):
        # 含义：初始化命令注册中心
        self.registry = CommandRegistry()
        # 含义：初始化状态机，传入注册中心
        self.state_machine = StateMachine(self.registry)
        # 含义：初始化命令执行器
        self.executor = CommandExecutor()
        # 含义：初始化事件日志器
        self.logger = EventLogger()
        # 含义：初始化响应解析器
        self.parser = ResponseParser()
        # 含义：记录初始状态 ID
        self.initial_state_id = initial_state_id
        # 含义：初始化对话历史列表（仅摘要，非系统事件）
        self.conversation_history: List[str] = []
        # 含义：保存上一次模型动作，用于提取给用户的回复
        self.last_action: Optional[ModelAction] = None
        # 含义：缓存架构师生成的动态命令 ID 列表
        self.dynamic_command_ids: List[str] = []
        # 含义：保存上一次命令输出数据（供外部执行器使用）
        self.last_output: Optional[Dict[str, Any]] = None

    # 含义：启动系统，初始化状态
    def start(self):
        # 含义：切换到初始状态
        self.state_machine.transition_to(self.initial_state_id)
        # 含义：记录系统启动事件
        self.logger.log(EventType.STATE_CHANGE, f"System started at {self.initial_state_id}")

    # 含义：获取上下文摘要（限制 Token 消耗）
    def _get_context_summary(self) -> str:
        # 含义：只保留最近 5 轮对话作为摘要
        recent_history = self.conversation_history[-5:]
        # 含义：拼接为字符串
        return "\n".join(recent_history)

    # 含义：调用架构师 AI (自由模式专用)
    def _call_architect(self, user_input: str) -> Optional[ArchitectOutput]:
        # 含义：导入配置管理器
        from .config_manager import ConfigManager
        # 含义：导入 requests
        import requests

        # 含义：创建配置管理器实例
        config_mgr = ConfigManager()
        # 含义：获取 API 配置
        api_config = config_mgr.get_api_config()

        # 含义：如果未配置 API，返回 None
        if not config_mgr.is_configured():
            return None

        # 含义：构建提示词
        prompt = ARCHITECT_PROMPT_TEMPLATE.format(
            context_summary=self._get_context_summary(),
            user_input=user_input,
            format_example=ARCHITECT_FORMAT_EXAMPLE
        )

        # 含义：构建 API 请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_config.get('key')}"
        }
        payload = {
            "model": api_config.get("model"),
            "messages": [
                {"role": "system", "content": "你是系统架构师，负责规划状态和命令。输出严格 JSON。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        }

        # 含义：发送请求
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
            # 含义：解析为 ArchitectOutput
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                json_str = content[start:end + 1]
                return ArchitectOutput(**json.loads(json_str))
            return None
        except Exception as e:
            # 含义：记录错误但不中断
            self.logger.log(EventType.SYSTEM_ERROR, f"Architect Error: {str(e)}")
            return None

    # 含义：处理用户输入的核心方法
    def process_user_input(self, user_input: str) -> SystemFeedback:
        # 含义：获取当前状态
        current_state = self.state_machine.get_current_state()

        # 含义：重置输出数据
        self.last_output = None

        # 含义：如果是自由模式，先调用架构师更新状态和命令
        if current_state and current_state.mode == "free":
            # 含义：调用架构师
            architect_output = self._call_architect(user_input)
            if architect_output:
                # 含义：更新当前状态描述
                current_state.description = architect_output.current_state_description
                # 含义：注册动态命令
                self.dynamic_command_ids = []
                for cmd_def in architect_output.available_commands:
                    # 含义：转换为正式 CommandDefinition
                    full_cmd = CommandDefinition(
                        id=cmd_def.id,
                        description=cmd_def.description,
                        parameters_schema=cmd_def.parameters_schema
                    )
                    # 含义：注册到临时池（这里简化为直接注册到 registry）
                    self.registry.register(full_cmd)
                    self.dynamic_command_ids.append(cmd_def.id)
                # 含义：更新状态可用命令列表
                current_state.available_command_ids = self.dynamic_command_ids
                # 含义：记录架构师工作事件
                self.logger.log(EventType.SYSTEM_SUCCESS, f"Architect updated state: {current_state.description}")
            else:
                # 含义：如果架构师失败，保留原有命令或降级
                self.logger.log(EventType.SYSTEM_ERROR, "Architect failed, using fallback")

        # 含义：1. 构建系统反馈数据包
        feedback = self._build_feedback()

        # 含义：2. 调用执行者 LLM
        llm_response_text = self._call_llm(feedback, user_input)

        # 含义：3. 解析 LLM 输出
        try:
            action = self.parser.parse(llm_response_text)
        except ParserError as e:
            self.logger.log(EventType.SYSTEM_ERROR, f"Parser Error: {e.message}")
            return self._build_feedback(error_only=True)

        # 含义：保存当前动作
        self.last_action = action

        # 含义：4. 执行动作
        if action.action_type == ModelActionType.CALL_COMMAND:
            cmd = self.registry.get_command(action.command_id)
            if cmd:
                status, data = self.executor.execute(cmd, action.command_params)
                if status.value == "success":
                    self.logger.log(EventType.SYSTEM_SUCCESS, f"Command {cmd.id} executed", cmd.id)
                    # 含义：检查是否为输出数据
                    if isinstance(data, dict) and data.get("output_key"):
                        self.last_output = data
                else:
                    self.logger.log(EventType.SYSTEM_ERROR, f"Command {cmd.id} failed: {data}", cmd.id)
            else:
                self.logger.log(EventType.SYSTEM_ERROR, f"Command {action.command_id} not found")

        elif action.action_type == ModelActionType.PROPOSE_COMMAND:
            self.logger.log(EventType.SYSTEM_SUCCESS, f"New command proposed: {action.proposed_command.id}")

        # 含义：5. 更新对话历史
        self.conversation_history.append(f"User: {user_input}")
        if action.response_to_user:
            self.conversation_history.append(f"Assistant: {action.response_to_user}")

        # 含义：6. 返回最终系统反馈
        return self._build_feedback()

    # 含义：构建系统反馈数据包的辅助方法
    def _build_feedback(self, error_only: bool = False) -> SystemFeedback:
        # 含义：获取当前状态
        current_state = self.state_machine.get_current_state()
        # 含义：获取当前可用命令
        disclosed_cmds = self.state_machine.get_disclosed_commands()
        # 含义：获取事件历史
        history = self.logger.get_history()
        # 含义：如果仅报错模式，数据 payload 为空
        data = None
        if error_only:
            pass
            # 含义：构建并返回反馈对象
        return SystemFeedback(
            current_state=current_state,
            event_history=history,
            data_payload=data,
            disclosed_commands=disclosed_cmds
        )

    # 含义：获取模型上一次给用户的自然语言回复
    def get_last_response(self) -> Optional[str]:
        # 含义：如果存在上一次动作
        if self.last_action:
            # 含义：返回给用户看的回复内容
            return self.last_action.response_to_user
        # 含义：否则返回 None
        return None

    # 含义：获取上一次命令的输出数据（供外部执行器使用）
    def get_last_output(self) -> Optional[Dict[str, Any]]:
        # 含义：返回输出数据
        return self.last_output

    # 含义：调用真实 LLM API 的方法 (执行者)
    def _call_llm(self, feedback: SystemFeedback, user_input: str) -> str:
        # 含义：导入配置管理器
        from .config_manager import ConfigManager
        # 含义：导入 requests
        import requests

        # 含义：创建配置管理器实例
        config_mgr = ConfigManager()
        # 含义：获取 API 配置
        api_config = config_mgr.get_api_config()

        # 含义：如果未配置 API，返回错误提示 JSON
        if not config_mgr.is_configured():
            return json.dumps({
                "thought": "系统未配置 API",
                "action_type": "reply_only",
                "response_to_user": "错误：请先在 CLI 中配置 API Key 和地址。"
            })

        # 含义：构建提示词内容
        cmd_text = format_commands(feedback.disclosed_commands)
        evt_text = format_events(feedback.event_history)
        prompt = SYSTEM_PROMPT_TEMPLATE.format(
            state_description=feedback.current_state.description,
            state_mode=feedback.current_state.mode,
            commands_list=cmd_text,
            event_history=evt_text,
            user_input=user_input
        )

        # 含义：构建 API 请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_config.get('key')}"
        }

        # 含义：构建 API 请求体
        payload = {
            "model": api_config.get("model"),
            "messages": [
                {"role": "system", "content": "你是一个状态驱动的智能助手。输出必须是严格的 JSON 格式。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        # 含义：发送 POST 请求
        try:
            # 含义：调用 API 端点
            response = requests.post(
                f"{api_config.get('base_url')}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            # 含义：检查 HTTP 状态码
            response.raise_for_status()
            # 含义：解析响应 JSON
            data = response.json()
            # 含义：提取模型生成的内容
            content = data['choices'][0]['message']['content']
            # 含义：返回原始内容（解析器会处理 JSON 提取）
            return content
        except Exception as e:
            # 含义：如果请求失败，返回错误 JSON
            return json.dumps({
                "thought": "API 调用失败",
                "action_type": "reply_only",
                "response_to_user": f"系统错误：{str(e)}"
            })