# src/core/project_loader.py

import sys
from pathlib import Path

try:
    from controller import SystemController
    from models import StateNode, CommandDefinition
    from command_handlers import HandlerRegistry
except ImportError:
    from .controller import SystemController
    from .models import StateNode, CommandDefinition
    from .command_handlers import HandlerRegistry

import yaml
import json

class ProjectLoader:
    def __init__(self, project_path: str):
        self.path = Path(project_path)
        if self.path.is_dir():
            self.path = self.path / "project.yaml"
        self.project_dir = self.path.parent
        self.config: dict = {}
        self.handler_registry = HandlerRegistry()
        self._load()

    def _load(self):
        if not self.path.exists():
            raise FileNotFoundError(f"Project file not found: {self.path}")
        with open(self.path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        config_file = self.project_dir / "config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                project_config = json.load(f)
            if "api" in project_config:
                self.config["api"] = project_config["api"]

    def apply_to(self, controller: SystemController):
        self.handler_registry.load_project_plugins(str(self.project_dir))
        
        # =============================================================
        # 1. 注册所有命令
        # =============================================================
        commands = self.config.get("commands", [])
        registered_cmd_ids = []
        
        for cmd_data in commands:
            cmd_id = cmd_data["id"].lower()
            
            # 获取返回值设置（从 return_settings 或旧格式）
            return_settings = cmd_data.get("return_settings", {})
            if not return_settings:
                # 兼容旧格式
                return_settings = {
                    "has_return": cmd_data.get("has_return", False),
                    "wait_for_return": cmd_data.get("wait_for_return", False)
                }
            
            has_return = return_settings.get("has_return", False)
            wait_for_return = return_settings.get("wait_for_return", False)
            
            # =============================================================
            # 【关键修复】只传递 CommandDefinition 有的字段
            # =============================================================
            cmd = CommandDefinition(
                id=cmd_id,
                description=cmd_data["description"],
                parameters_schema=cmd_data.get("parameters_schema", {}),
                has_return=has_return,
                wait_for_return=wait_for_return
                # 注意：不要传递 processor_category，这个字段不存在于模型中
            )
            controller.registry.register(cmd)
            registered_cmd_ids.append(cmd_id)
            
            # 绑定处理器
            handler_config = cmd_data.get("handler", {})
            if handler_config:
                handler_type = handler_config.get("type")
                if handler_type:
                    function_name = handler_config.get("config", {}).get("function")
                    handler_func = self.handler_registry.get_handler(handler_type, function_name)
                    
                    if handler_func:
                        handler_config_params = handler_config.get("config", {})
                        def make_wrapper(func, config_params):
                            def wrapper(**cmd_params):
                                all_params = {**config_params, **cmd_params}
                                return func(**all_params)
                            return wrapper
                        controller.executor.register_handler(cmd_id, make_wrapper(handler_func, handler_config_params))
        
        # =============================================================
        # 2. 注册所有状态
        # =============================================================
        states = self.config.get("states", [])
        for state_data in states:
            available_cmds = state_data.get("available_commands", [])
            if not available_cmds:
                available_cmds = state_data.get("available_command_ids", [])
            
            # 统一转小写
            available_cmds = [cmd.lower() for cmd in available_cmds]
            valid_cmds = [cmd_id for cmd_id in available_cmds if cmd_id in registered_cmd_ids]
            
            state = StateNode(
                id=state_data["id"],
                description=state_data["description"],
                mode=state_data.get("mode", "stable"),
                parent_id=state_data.get("parent_id"),
                available_command_ids=valid_cmds
            )
            controller.state_machine.register_state(state)
        
        # =============================================================
        # 3. 注册命令跳转
        # =============================================================
        self._register_transitions(controller)
        
        # =============================================================
        # 4. 传递 API 配置
        # =============================================================
        controller.project_api_config = self.config.get("api", {})
        
        # =============================================================
        # 5. 启动系统
        # =============================================================
        initial_state = self.config.get("initial_state", "root")
        controller.start()
        
        return {
            "project_name": self.config.get("project", {}).get("name", "Unknown"),
            "initial_state": initial_state
        }

    def _register_transitions(self, controller: SystemController):
        for state_data in self.config.get("states", []):
            transitions = state_data.get("command_transitions", {})
            for cmd_id, target_state in transitions.items():
                cmd_id_lower = cmd_id.lower()
                def make_handler(target):
                    def handler(**kwargs):
                        success, msg = controller.state_machine.transition_to(target)
                        if success:
                            return f"已切换到 {target}"
                        else:
                            raise Exception(msg)
                    return handler
                controller.executor.register_handler(cmd_id_lower, make_handler(target_state))
