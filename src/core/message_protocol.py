# src/core/message_protocol.py

# 导入 Pydantic 的 BaseModel 用于数据验证
from pydantic import BaseModel, Field
# 导入 model_validator 用于模型级验证
from pydantic import model_validator
# 导入 typing 模块用于类型提示
from typing import Optional, Dict, Any, List
# 导入之前定义的命令模型
from .models import CommandDefinition
# 导入 Enum 用于定义枚举
from enum import Enum

# 定义模型动作类型枚举
class ModelActionType(str, Enum):
    # 含义：表示模型仅回复用户，不调用系统命令
    REPLY_ONLY = "reply_only"
    # 含义：表示模型需要调用系统命令
    CALL_COMMAND = "call_command"
    # 含义：表示模型请求生成新命令（仅限自由模式）
    PROPOSE_COMMAND = "propose_command"

# 定义模型输出的动作数据模型
class ModelAction(BaseModel):
    # 含义：模型思考过程的简要记录，用于调试
    thought: str = Field(..., description="模型的思考过程")
    # 含义：模型行动的类型（回复、调用命令、提议命令）
    action_type: ModelActionType
    # 含义：面向用户的自然语言回复内容
    response_to_user: Optional[str] = Field(None, description="给用户看的回复")
    # 含义：要调用的系统命令 ID
    command_id: Optional[str] = Field(None, description="要执行的命令 ID")
    # 含义：命令所需的参数
    command_params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="命令参数")
    # 含义：如果是提议新命令，此处存放新命令的定义
    proposed_command: Optional[CommandDefinition] = Field(None, description="提议的新命令")

    # 含义：模型级验证器，在所有字段解析完成后执行
    @model_validator(mode='after')
    def validate_action_consistency(self):
        # 含义：如果动作类型是调用命令
        if self.action_type == ModelActionType.CALL_COMMAND:
            # 含义：检查是否提供了命令 ID
            if not self.command_id:
                # 含义：如果没有，抛出错误
                raise ValueError("CALL_COMMAND requires command_id")
        # 含义：如果动作类型是提议命令
        if self.action_type == ModelActionType.PROPOSE_COMMAND:
            # 含义：检查是否提供了命令定义
            if not self.proposed_command:
                # 含义：如果没有，抛出错误
                raise ValueError("PROPOSE_COMMAND requires proposed_command")
        # 含义：返回当前模型实例
        return self

# 定义发送给模型的请求数据包
class LLMRequest(BaseModel):
    # 含义：当前系统的反馈信息（状态、历史、可用命令）
    # 使用 Any 类型避免与 SystemFeedback 循环导入
    system_feedback: Any = Field(..., description="系统反馈数据包")
    # 含义：用户的最新输入内容
    user_input: str = Field(..., description="用户输入")
    # 含义：对话历史摘要（可选）
    conversation_history: List[str] = Field(default_factory=list, description="对话历史摘要")