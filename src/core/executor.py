# src/core/executor.py

# 导入之前定义的命令模型
try:
    from .models import CommandDefinition, ReturnStatus
except ImportError:
    from models import CommandDefinition, ReturnStatus
# 导入 typing 模块用于类型提示
from typing import Any, Dict, Tuple

# 定义命令执行器类
class CommandExecutor:
    # 含义：初始化方法
    def __init__(self):
        # 含义：创建一个字典，用于注册具体的命令处理函数
        # 键为命令 ID，值为处理函数
        self._handlers: Dict[str, callable] = {}

    # 含义：注册一个命令的具体执行逻辑
    def register_handler(self, command_id: str, handler: callable):
        # 含义：将命令 ID 与处理函数绑定
        self._handlers[command_id] = handler

    # 含义：执行命令的核心方法
    def execute(self, command: CommandDefinition, params: Dict[str, Any]) -> Tuple[ReturnStatus, Any]:
        # 含义：检查该命令是否有注册的处理函数
        if command.id in self._handlers:
            # 含义：获取对应的处理函数
            handler = self._handlers[command.id]
            try:
                # 含义：尝试执行处理函数，传入参数
                result = handler(**params)
                # 含义：如果成功，返回成功状态和结果数据
                return ReturnStatus.SUCCESS, result
            except Exception as e:
                # 含义：如果执行抛出异常，返回错误状态和异常信息
                return ReturnStatus.ERROR, str(e)
        else:
            # 含义：如果未找到处理函数，返回错误状态
            return ReturnStatus.ERROR, f"Handler not found for {command.id}"