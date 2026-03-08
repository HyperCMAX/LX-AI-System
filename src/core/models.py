# src/core/models.py

# =============================================================================
# 【关键修复】常量直接定义在此文件中，不依赖 config.py
# =============================================================================

# 命令 ID 的正则表达式模式
COMMAND_ID_PATTERN = r"^[a-z][a-z0-9_-]*$"

# 自由模式下的最大状态嵌套层级限制
FREE_MODE_MAX_DEPTH = 5

# 系统事件历史的最大保留条数
MAX_EVENT_HISTORY_SIZE = 100

# =============================================================================
# 正常导入
# =============================================================================
from datetime import datetime
from enum import Enum
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, field_validator, model_validator

# =============================================================================
# 数据模型
# =============================================================================

class ReturnStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"

class EventType(str, Enum):
    SYSTEM_SUCCESS = "system_success"
    SYSTEM_ERROR = "system_error"
    STATE_CHANGE = "state_change"

class CommandDefinition(BaseModel):
    # 含义：命令的唯一标识符
    id: str = Field(...)
    # 含义：命令的描述信息
    description: str
    # 含义：命令所需的参数结构定义
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)
    # 含义：标记该命令执行后是否有返回值
    has_return: bool = False
    # 含义：标记系统是否需要等待该命令的返回值才能继续
    wait_for_return: bool = False

    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        # 含义：放宽验证，自动转换小写
        if not v:
            raise ValueError("Command ID cannot be empty")
        if not v[0].isalpha():
            raise ValueError("Command ID must start with a letter")
        # 含义：允许字母、数字、下划线、连字符
        if not all(c.isalnum() or c in ['_', '-'] for c in v):
            raise ValueError("Command ID can only contain letters, numbers, underscores, and hyphens")
        # 含义：自动转换为小写
        return v.lower()

class StateNode(BaseModel):
    # 含义：状态节点的唯一标识符
    id: str
    # 含义：状态节点的描述信息
    description: str
    # 含义：父状态节点的 ID，用于构建状态层次结构
    parent_id: Optional[str] = None
    # 含义：在该状态下可用的命令 ID 列表
    available_command_ids: List[str] = Field(default_factory=list)
    # 含义：状态模式（stable=稳定流程，free=自由探索）
    mode: str = Field(default="stable")
    # 含义：状态嵌套深度，用于防止无限递归
    depth: int = 0

    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v):
        if v not in ["stable", "free"]:
            raise ValueError("Mode must be 'stable' or 'free'")
        return v

class SystemEvent(BaseModel):
    # 含义：事件发生的时间戳
    timestamp: datetime = Field(default_factory=datetime.now)
    # 含义：事件类型
    event_type: EventType
    # 含义：事件的描述信息
    message: str
    # 含义：相关命令的 ID（如果有）
    related_command_id: Optional[str] = None

class SystemFeedback(BaseModel):
    # 含义：当前系统状态
    current_state: StateNode
    # 含义：系统事件历史记录
    event_history: List[SystemEvent] = Field(default_factory=list)
    # 含义：数据负载，用于传递额外信息
    data_payload: Optional[Any] = None
    # 含义：已披露的命令列表
    disclosed_commands: List[CommandDefinition] = Field(default_factory=list)

    @field_validator('event_history')
    @classmethod
    def limit_history(cls, v):
        if len(v) > MAX_EVENT_HISTORY_SIZE:
            return v[-MAX_EVENT_HISTORY_SIZE:]
        return v

class DynamicCommandDefinition(BaseModel):
    # 含义：动态命令的唯一标识符
    id: str = Field(...)
    # 含义：动态命令的描述信息
    description: str
    # 含义：动态命令的参数结构定义
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        # 含义：自动转换为小写
        if not v:
            raise ValueError("Command ID cannot be empty")
        if not v[0].isalpha():
            raise ValueError("Command ID must start with a letter")
        if not all(c.isalnum() or c in ['_', '-'] for c in v):
            raise ValueError("Command ID can only contain letters, numbers, underscores, and hyphens")
        return v.lower()

class ArchitectOutput(BaseModel):
    # 含义：架构师 AI 的思考过程
    thought: str
    # 含义：当前状态描述
    current_state_description: str
    # 含义：可用命令列表
    available_commands: List[DynamicCommandDefinition]
    # 含义：建议的状态转换目标（如果有）
    suggest_state_change: Optional[str] = None
