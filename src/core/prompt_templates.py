# src/core/prompt_templates.py

# 定义系统提示词模板字符串
SYSTEM_PROMPT_TEMPLATE = """
你是一个状态驱动的智能助手。当前系统状态如下：

【当前状态】
{state_description} (模式：{state_mode})

【可用命令】
{commands_list}

【系统事件历史】
{event_history}

【重要指令】
1. 你必须输出严格的 JSON 格式，不要包含任何 Markdown 或其他文本
2. action_type 必须是以下三个值之一：'reply_only', 'call_command', 'propose_command'
3. 如果只需要回复用户，使用 action_type: "reply_only"
4. 如果需要执行命令，使用 action_type: "call_command" 并提供 command_id
5. 如果在自由模式想提议新命令，使用 action_type: "propose_command"

【输出格式示例】
{{
    "thought": "你的思考过程",
    "action_type": "reply_only",
    "response_to_user": "给用户的回复"
}}

或

{{
    "thought": "你的思考过程",
    "action_type": "call_command",
    "response_to_user": "给用户的回复",
    "command_id": "命令 ID",
    "command_params": {{"参数名": "参数值"}}
}}

【用户输入】
{user_input}
"""

# 定义生成命令列表字符串的辅助函数
def format_commands(commands: list) -> str:
    # 含义：创建一个空列表用于存储格式化后的字符串
    formatted = []
    # 含义：遍历每一个命令对象
    for cmd in commands:
        # 含义：将命令 ID 和描述拼接成字符串
        line = f"- {cmd.id}: {cmd.description}"
        # 含义：加入列表
        formatted.append(line)
    # 含义：用换行符连接所有字符串并返回
    return "\n".join(formatted)

# 定义生成事件历史字符串的辅助函数
def format_events(events: list) -> str:
    # 含义：创建一个空列表
    formatted = []
    # 含义：遍历每一个事件对象
    for evt in events:
        # 含义：拼接时间、类型和消息
        line = f"[{evt.event_type.value}] {evt.message}"
        # 含义：加入列表
        formatted.append(line)
    # 含义：返回连接后的字符串
    return "\n".join(formatted)

# 在 src/core/prompt_templates.py 末尾添加

# 定义架构师系统提示词模板
ARCHITECT_PROMPT_TEMPLATE = """
你是一个系统架构师 AI。你的任务是根据当前上下文，动态规划可用的状态和命令。
限制：上下文有限，请只保留最相关的命令。

【当前上下文摘要】
{context_summary}

【用户最新输入】
{user_input}

【指令】
1. 分析用户意图和上下文。
2. 定义当前状态描述（简短）。
3. 生成 3-5 个最相关的可用命令（包含 ID 和描述）。
4. 输出严格的 JSON 格式。

【输出格式】
{format_example}
"""

# 定义架构师输出格式示例
ARCHITECT_FORMAT_EXAMPLE = """
{
    "thought": "用户想搜索文件，需要搜索相关命令",
    "current_state_description": "文件搜索任务中",
    "available_commands": [
        {"id": "search_file", "description": "搜索指定文件", "parameters_schema": {"path": "str"}},
        {"id": "filter_result", "description": "过滤搜索结果", "parameters_schema": {"type": "str"}}
    ]
}
"""