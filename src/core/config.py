# src/core/config.py

# 定义命令 ID 的正则表达式模式
# 含义：只允许小写字母、数字和下划线，且必须以字母开头
COMMAND_ID_PATTERN = r"^[a-z][a-z0-9_]*$"

# 定义自由模式下的最大状态嵌套层级限制
# 含义：当处于自由模式时，状态树深度不能超过 5 层
FREE_MODE_MAX_DEPTH = 5

# 定义系统事件历史的最大保留条数
# 含义：防止内存溢出，只保留最近的 100 条系统事件
MAX_EVENT_HISTORY_SIZE = 100