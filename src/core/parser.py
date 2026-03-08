# src/core/parser.py

# 导入 json 模块用于解析字符串
import json
# 导入之前定义的消息协议模型
try:
    from .message_protocol import ModelAction
except ImportError:
    from message_protocol import ModelAction
# 导入 Pydantic 验证异常
from pydantic import ValidationError


# 定义解析器异常类
class ParserError(Exception):
    # 含义：初始化异常信息
    def __init__(self, message: str):
        # 含义：保存错误消息
        self.message = message
        # 含义：调用父类初始化
        super().__init__(self.message)


# 定义解析器类
class ResponseParser:
    # 含义：解析 LLM 输出的原始文本
    def parse(self, raw_text: str) -> ModelAction:
        # 含义：尝试提取 JSON 内容（防止模型包裹 markdown 代码块）
        json_str = self._extract_json(raw_text)

        # 含义：尝试将 JSON 字符串加载为字典
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            # 含义：如果 JSON 格式错误，抛出自定义解析错误
            raise ParserError(f"Invalid JSON format: {str(e)}")

        # =====================================================================
        # 修复：标准化 action_type 值
        # =====================================================================
        if "action_type" in data:
            action_type = data["action_type"]
            # 含义：映射常见变体到标准值
            action_type_mapping = {
                "reply_only": "reply_only",
                "reply": "reply_only",
                "回复": "reply_only",
                "仅回复": "reply_only",
                "call_command": "call_command",
                "call": "call_command",
                "命令": "call_command",
                "调用命令": "call_command",
                "propose_command": "propose_command",
                "propose": "propose_command",
                "提议": "propose_command",
                "新命令": "propose_command",
            }
            # 含义：标准化 action_type
            data["action_type"] = action_type_mapping.get(action_type, action_type)

        # =============================================================
        # 【关键修复】确保 has_return 和 wait_for_return 有默认值
        # =============================================================
        if "has_return" not in data:
            data["has_return"] = False
        if "wait_for_return" not in data:
            data["wait_for_return"] = False

        # 含义：尝试用 Pydantic 模型验证数据
        try:
            action = ModelAction(**data)
        except ValidationError as e:
            # 含义：如果数据字段不符合模型定义，抛出验证错误
            raise ParserError(f"Data validation failed: {str(e)}")

        # 含义：返回验证通过的动作对象
        return action

    # 含义：辅助方法，从文本中提取 JSON 字符串
    def _extract_json(self, text: str) -> str:
        # 含义：查找第一个左花括号的位置
        start = text.find('{')
        # 含义：查找最后一个右花括号的位置
        end = text.rfind('}')

        # 含义：如果没找到花括号，返回原文本（让后续 json.loads 报错）
        if start == -1 or end == -1:
            return text

        # 含义：截取 JSON 部分
        return text[start:end + 1]