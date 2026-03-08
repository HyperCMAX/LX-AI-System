# src/core/registry.py

# 导入 typing 模块用于类型提示
from typing import Dict, List, Optional, Any
# 导入之前定义的命令模型
from .models import CommandDefinition
# 导入配置中的正则 pattern
from .config import COMMAND_ID_PATTERN
# 导入 re 模块用于正则匹配
import re

# 定义命令注册中心类
class CommandRegistry:
    # 含义：初始化方法，构建命令存储容器
    def __init__(self):
        # 含义：创建一个字典，用于存储所有注册的命令，Key 为命令 ID
        self._commands: Dict[str, CommandDefinition] = {}
        # 含义：创建一个列表，存储系统保留的逻辑命令 ID（如返回上一级）
        self._system_command_ids: List[str] = []

    # 含义：注册一个新命令的方法
    def register(self, command: CommandDefinition, is_system: bool = False) -> bool:
        # 含义：首先验证命令 ID 是否符合正则规范
        if not re.match(COMMAND_ID_PATTERN, command.id):
            # 含义：如果不符合，返回 False 表示注册失败
            return False
        # 含义：如果 ID 已存在，覆盖前通常应警告，此处直接覆盖
        self._commands[command.id] = command
        # 含义：如果是系统逻辑命令，加入保留列表
        if is_system:
            if command.id not in self._system_command_ids:
                self._system_command_ids.append(command.id)
        # 含义：返回 True 表示注册成功
        return True

    # 含义：根据 ID 获取命令定义的方法
    def get_command(self, command_id: str) -> Optional[CommandDefinition]:
        # 含义：从字典中返回命令对象，若不存在则返回 None
        return self._commands.get(command_id)

    # 含义：获取所有可用命令的方法（用于披露）
    def get_all_commands(self) -> List[CommandDefinition]:
        # 含义：返回注册表中所有命令的列表
        return list(self._commands.values())

    # 含义：获取当前状态可披露的命令列表（核心逻辑）
    def get_disclosed_commands(self, allowed_ids: List[str]) -> List[CommandDefinition]:
        # 含义：创建一个空列表用于存放结果
        disclosed = []
        # 含义：遍历允许的命令 ID 列表
        for cmd_id in allowed_ids:
            # 含义：从注册表中查找对应的命令定义
            cmd = self._commands.get(cmd_id)
            # 含义：如果命令存在，加入结果列表
            if cmd:
                disclosed.append(cmd)
        # 含义：返回过滤后的命令列表
        return disclosed

    # 含义：获取系统保留的逻辑命令列表（如导航命令）
    def get_system_commands(self) -> List[CommandDefinition]:
        # 含义：创建一个空列表
        system_cmds = []
        # 含义：遍历系统命令 ID 列表
        for cmd_id in self._system_command_ids:
            # 含义：获取命令定义
            cmd = self._commands.get(cmd_id)
            # 含义：如果存在，加入列表
            if cmd:
                system_cmds.append(cmd)
        # 含义：返回系统命令列表
        return system_cmds