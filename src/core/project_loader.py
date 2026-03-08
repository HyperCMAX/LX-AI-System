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

        # 含义：加载 config.json
        config_file = self.project_dir / "config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                api_config = json.load(f)
            self.config["api"] = api_config.get("api", {})

    def apply_to(self, controller: SystemController):
        self.handler_registry.load_project_plugins(str(self.project_dir))

        commands = self.config.get("commands", [])
        for cmd_data in commands:
            cmd = CommandDefinition(
                id=cmd_data["id"],
                description=cmd_data["description"],
                parameters_schema=cmd_data.get("parameters_schema", {})
            )
            controller.registry.register(cmd)

            handler_config = cmd_data.get("handler", {})
            if handler_config:
                handler_type = handler_config.get("type", "echo")
                function_name = handler_config.get("config", {}).get("function")
                handler_func = self.handler_registry.get_handler(handler_type, function_name)

                if handler_func:
                    handler_config_params = handler_config.get("config", {})

                    def make_wrapper(func, config_params):
                        def wrapper(**cmd_params):
                            all_params = {**config_params, **cmd_params}
                            return func(**all_params)

                        return wrapper

                    controller.executor.register_handler(cmd_data["id"],
                                                         make_wrapper(handler_func, handler_config_params))

        states = self.config.get("states", [])
        for state_data in states:
            state = StateNode(
                id=state_data["id"],
                description=state_data["description"],
                mode=state_data.get("mode", "stable"),
                parent_id=state_data.get("parent_id"),
                available_command_ids=state_data.get("available_commands", [])
            )
            controller.state_machine.register_state(state)

        self._register_transitions(controller)

        # =====================================================================
        # 修复：将项目级 API 配置传递给控制器
        # =====================================================================
        controller.project_api_config = self.config.get("api", {})

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
                def make_handler(target):
                    def handler(**kwargs):
                        success, msg = controller.state_machine.transition_to(target)
                        if success:
                            return f"已切换到 {target}"
                        else:
                            raise Exception(msg)

                    return handler

                controller.executor.register_handler(cmd_id, make_handler(target_state))