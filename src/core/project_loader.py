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
        # 1. 注册所有命令（ID 转小写，兼容旧数据）
        # =============================================================
        commands = self.config.get("commands", [])
        registered_cmd_ids = []
        
        for cmd_data in commands:
            # 转小写（兼容旧数据）
            cmd_id = cmd_data["id"].lower()
            
            # 获取返回值设置
            return_settings = cmd_data.get("return_settings")
            if return_settings is None:
                return_settings = {}
            if not return_settings:
                return_settings = {
                    "has_return": cmd_data.get("has_return", False),
                    "wait_for_return": cmd_data.get("wait_for_return", False)
                }
            
            has_return = return_settings.get("has_return", False)
            wait_for_return = return_settings.get("wait_for_return", False)
            
            cmd = CommandDefinition(
                id=cmd_id,
                description=cmd_data.get("description", "无描述"),
                parameters_schema=cmd_data.get("parameters_schema", {}),
                has_return=has_return,
                wait_for_return=wait_for_return
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
        # 2. 注册所有状态（可用命令 ID 转小写）
        # =============================================================
        states = self.config.get("states", [])
        for state_data in states:
            available_cmds = state_data.get("available_commands", [])
            if not available_cmds:
                available_cmds = state_data.get("available_command_ids", [])
            
            # 转小写（兼容旧数据）
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
        # 3. 注册命令跳转（优先使用 command_transitions，其次自动注册）
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
        """
        注册状态跳转处理器（三层优先级）：
        1. 显式的 command_transitions 配置（最高优先级）
        2. state_jump 处理器的 target 参数（自动注册，中等优先级）
        3. 其他命令保持默认行为（无跳转）
        """
        # 记录已注册的跳转命令，避免重复注册
        registered_transitions = set()
        
        # 第一层：处理显式的 command_transitions 配置
        for state_data in self.config.get("states", []):
            transitions = state_data.get("command_transitions", {})
            for cmd_id, target_state in transitions.items():
                if target_state and target_state != "(无跳转)":
                    cmd_id_lower = cmd_id.lower()
                    registered_transitions.add(cmd_id_lower)
                    
                    def make_handler(target):
                        def handler(**kwargs):
                            success, msg = controller.state_machine.transition_to(target)
                            if success:
                                return f"已切换到 {target}"
                            else:
                                raise Exception(msg)
                        return handler
                    controller.executor.register_handler(cmd_id_lower, make_handler(target_state))
        
        # 第二层：为未配置的 state_jump 命令自动注册跳转
        commands = self.config.get("commands", [])
        for cmd_data in commands:
            cmd_id = cmd_data["id"].lower()
            
            # 跳过已显式配置的命令
            if cmd_id in registered_transitions:
                continue
            
            # 检查是否为 state_jump 处理器
            handler_config = cmd_data.get("handler", {})
            if handler_config and handler_config.get("type") == "state_jump":
                target_state = handler_config.get("config", {}).get("target")
                
                if target_state:
                    # 自动注册跳转处理器
                    def make_auto_handler(target):
                        def handler(**kwargs):
                            success, msg = controller.state_machine.transition_to(target)
                            if success:
                                return f"自动跳转到 {target}"
                            else:
                                raise Exception(msg)
                        return handler
                    
                    controller.executor.register_handler(cmd_id, make_auto_handler(target_state))
