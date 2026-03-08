# src/core/models.py

# src/core/models.py 顶部

from datetime import datetime
from enum import Enum
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, field_validator, model_validator
# 含义：确保从 config 导入模式
try:
    from .config import COMMAND_ID_PATTERN, FREE_MODE_MAX_DEPTH, MAX_EVENT_HISTORY_SIZE
except ImportError:
    from config import COMMAND_ID_PATTERN, FREE_MODE_MAX_DEPTH, MAX_EVENT_HISTORY_SIZE

# 定义命令执行后的返回值类型枚举
class ReturnStatus(str, Enum):
    # 含义：表示命令执行成功
    SUCCESS = "success"
    # 含义：表示命令执行失败
    ERROR = "error"
    # 含义：表示命令正在等待异步结果
    PENDING = "pending"

# 定义系统事件的类型枚举
class EventType(str, Enum):
    # 含义：表示系统内部执行成功的事件
    SYSTEM_SUCCESS = "system_success"
    # 含义：表示系统内部执行报错的事件
    SYSTEM_ERROR = "system_error"
    # 含义：表示状态发生切换的事件
    STATE_CHANGE = "state_change"

# 定义命令的数据模型
class CommandDefinition(BaseModel):
    # 含义：命令的唯一标识符，必须符合 config 中定义的正则
    id: str = Field(..., pattern=COMMAND_ID_PATTERN)
    # 含义：命令的描述信息，用于提示模型该命令的作用
    description: str
    # 含义：命令所需的参数结构定义，默认为空字典
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)
    # 含义：标记该命令执行后是否有返回值
    has_return: bool = False
    # 含义：标记系统是否需要等待该命令的返回值才能继续
    wait_for_return: bool = False

    # 含义：验证器，确保命令 ID 符合命名规范
    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        # 含义：如果不符合正则，抛出错误
        if not v or not v[0].isalpha():
            raise ValueError("Command ID must start with a letter")
        return v

# 定义状态节点的数据模型
class StateNode(BaseModel):
    # 含义：状态的唯一标识符
    id: str
    # 含义：状态的简短描述，用于披露给模型
    description: str
    # 含义：父级状态 ID，用于实现嵌套逻辑（支持无限嵌套）
    parent_id: Optional[str] = None
    # 含义：当前状态下可用的命令 ID 列表
    available_command_ids: List[str] = Field(default_factory=list)
    # 含义：标记该状态属于稳定模式还是自由模式
    mode: str = Field(default="stable", pattern="^(stable|free)$")
    # 含义：记录当前状态的嵌套深度，用于自由模式限制
    depth: int = 0

# 定义系统事件记录的数据模型
class SystemEvent(BaseModel):
    # 含义：事件发生的时间戳
    timestamp: datetime = Field(default_factory=datetime.now)
    # 含义：事件类型（成功、报错、状态切换）
    event_type: EventType
    # 含义：事件的具体内容描述
    message: str
    # 含义：关联的命令 ID（如果是命令执行产生的事件）
    related_command_id: Optional[str] = None

# 定义系统反馈给模型的整体数据包模型
class SystemFeedback(BaseModel):
    # 含义：当前系统所处的状态节点信息
    current_state: StateNode
    # 含义：系统事件历史记录列表（仅包含系统事件）
    event_history: List[SystemEvent] = Field(default_factory=list)
    # 含义：命令执行后的返回数据 payload（如有）
    data_payload: Optional[Any] = None
    # 含义：当前可用的完整命令定义列表（基于状态披露）
    disclosed_commands: List[CommandDefinition] = Field(default_factory=list)

    # 含义：验证器，确保事件历史不超过配置的最大长度
    @field_validator('event_history')
    @classmethod
    def limit_history(cls, v):
        # 含义：如果历史记录超出限制，只保留最新的 N 条
        if len(v) > MAX_EVENT_HISTORY_SIZE:
            return v[-MAX_EVENT_HISTORY_SIZE:]
        return v

# =============================================================================
# 以下是自由模式架构师专用模型（新增部分）
# =============================================================================

# 定义架构师生成的命令结构（简化版，用于动态生成）
class DynamicCommandDefinition(BaseModel):
    # 含义：动态生成的命令 ID
    id: str = Field(..., pattern=COMMAND_ID_PATTERN)
    # 含义：命令描述
    description: str
    # 含义：参数 schema 示例
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)

# 定义架构师的输出模型
class ArchitectOutput(BaseModel):
    # 含义：架构师思考过程
    thought: str
    # 含义：当前上下文的状态描述（动态生成）
    current_state_description: str
    # 含义：基于上下文推荐的可用命令列表
    available_commands: List[DynamicCommandDefinition]
    # 含义：是否需要切换状态（如进入子任务）
    suggest_state_change: Optional[str] = None