# src/core/logger.py

# 导入之前定义的系统事件模型
try:
    from .models import SystemEvent, EventType
except ImportError:
    from models import SystemEvent, EventType
# 导入配置中的最大历史长度
try:
    from .config import MAX_EVENT_HISTORY_SIZE
except ImportError:
    from config import MAX_EVENT_HISTORY_SIZE
# 导入 datetime 用于时间戳
from datetime import datetime
# 导入 typing 用于列表类型
from typing import List

# 定义事件日志类
class EventLogger:
    # 含义：初始化方法
    def __init__(self):
        # 含义：创建一个列表，存储系统事件历史
        self._history: List[SystemEvent] = []

    # 含义：记录一个新事件的方法
    def log(self, event_type: EventType, message: str, command_id: str = None):
        # 含义：创建一个新的系统事件对象
        event = SystemEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            message=message,
            related_command_id=command_id
        )
        # 含义：将事件添加到历史列表
        self._history.append(event)
        # 含义：检查历史长度是否超出限制
        if len(self._history) > MAX_EVENT_HISTORY_SIZE:
            # 含义：如果超出，移除最旧的事件（保留最新的 N 条）
            self._history.pop(0)

    # 含义：获取当前事件历史的方法
    def get_history(self) -> List[SystemEvent]:
        # 含义：返回历史列表的拷贝，防止外部修改
        return self._history.copy()

    # 含义：清空历史的方法（用于重置会话）
    def clear(self):
        # 含义：清空列表
        self._history = []