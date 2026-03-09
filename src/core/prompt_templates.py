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
你是一个系统架构师 AI。你的任务是根据当前上下文，从现有命令中选择可用的命令，并管理状态。

【当前状态】
{state_description} (模式：{state_mode})

【现有命令列表】（只能从以下命令中选择）
{all_commands}

【当前上下文摘要】
{context_summary}

【用户最新输入】
{user_input}

【重要规则】
1. 你不能生成新命令，只能从【现有命令列表】中选择
2. 选择 3-5 个最相关的命令 ID 放入 selected_command_ids
3. 如果需要创建新状态，在 suggest_new_state 中填写新状态 ID（必须是自由模式）
4. 如果需要跳转状态，在 suggest_state_change 中填写目标状态 ID
5. 输出严格 JSON 格式

【输出格式】
{format_example}
"""

# 定义架构师输出格式示例
ARCHITECT_FORMAT_EXAMPLE = """
{
    "thought": "用户想搜索文件，需要选择搜索相关命令",
    "current_state_description": "文件搜索任务中",
    "selected_command_ids": ["search_file", "filter_result", "open_file"],
    "suggest_new_state": null,
    "suggest_state_change": null
}
"""

ARCHITECT_FORMAT_EXAMPLE_WITH_STATE = """
{
    "thought": "用户想进入设置，需要创建新状态",
    "current_state_description": "系统设置",
    "selected_command_ids": ["change_setting", "save_setting"],
    "suggest_new_state": "settings_state",
    "suggest_state_change": null
}
"""
