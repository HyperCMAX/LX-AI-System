# src/core/registry.py

from .models import CommandDefinition
from typing import Optional, Dict, List

class CommandRegistry:
    def __init__(self):
        # 公开 commands 属性
        self.commands: Dict[str, CommandDefinition] = {}
        self._handlers: Dict[str, callable] = {}
        
        # 系统命令（如 back, help 等）
        self._system_commands: Dict[str, CommandDefinition] = {}

    def register(self, command: CommandDefinition):
        """注册命令"""
        self.commands[command.id.lower()] = command

    def get_command(self, command_id: str) -> Optional[CommandDefinition]:
        """获取命令定义"""
        return self.commands.get(command_id.lower())

    def list_commands(self) -> List[CommandDefinition]:
        """列出所有命令"""
        return list(self.commands.values())

    # =============================================================
    # 【新增】根据命令 ID 列表获取命令定义
    # =============================================================
    def get_disclosed_commands(self, command_ids: List[str]) -> List[CommandDefinition]:
        """
        根据命令 ID 列表获取命令定义
        - command_ids: 命令 ID 列表
        - 返回：命令定义列表
        """
        disclosed = []
        for cmd_id in command_ids:
            cmd = self.commands.get(cmd_id.lower())
            if cmd:
                disclosed.append(cmd)
        return disclosed

    # =============================================================
    # 【新增】获取系统命令
    # =============================================================
    def get_system_commands(self) -> List[CommandDefinition]:
        """
        获取系统命令（如 back, help 等）
        - 返回：系统命令定义列表
        """
        return list(self._system_commands.values())

    def register_handler(self, command_id: str, handler: callable):
        """注册命令处理器"""
        self._handlers[command_id.lower()] = handler

    def get_handler(self, command_id: str) -> Optional[callable]:
        """获取命令处理器"""
        return self._handlers.get(command_id.lower())

    def has_command(self, command_id: str) -> bool:
        """检查命令是否存在"""
        return command_id.lower() in self.commands

    # =============================================================
    # 【新增】注册系统命令
    # =============================================================
    def register_system_command(self, command: CommandDefinition):
        """注册系统命令"""
        self._system_commands[command.id.lower()] = command
