# src/core/prompt_templates.py

# 定义系统提示词模板字符串
SYSTEM_PROMPT_TEMPLATE = """
你是一个状态驱动的智能助手。当前系统状态如下：

【当前状态】
{state_description} (模式：{state_mode})

【可用命令】（只能使用以下命令）
{commands_list}

【系统事件历史】
{event_history}

【返回值状态】（如果有等待中的命令，会在这里显示）
{user_input}

【重要指令】
1. 你必须输出严格的 JSON 格式，不要包含任何 Markdown 或其他文本
2. action_type 必须是以下三个值之一：'reply_only', 'call_command', 'propose_command'
3. 只能使用【可用命令】列表中列出的命令
4. 如果只需要回复用户，使用 action_type: "reply_only"
5. 如果需要执行命令，使用 action_type: "call_command" 并提供：
   - command_id: 命令 ID
   - command_params: 命令参数
   - has_return: true/false - 该命令是否会产生返回值
   - wait_for_return: true/false - 是否需要等待返回值后再回复用户
     * wait_for_return=true: 执行命令后暂停，等系统返回值后再回复
     * wait_for_return=false: 执行命令后立即回复用户，但系统会在下次用户输入时附带返回值状态
6. 如果用户输入中包含 [系统返回值状态]，说明有命令正在等待返回值，请根据状态回复用户
7. 返回值状态格式：
   - [等待中] cmd_id: 已等待 X 秒/Y 秒
   - [已返回] cmd_id: 返回值内容
   - [已超时] cmd_id: 超过 Y 秒无返回值
8. 如果在自由模式想提议新命令，使用 action_type: "propose_command"

【输出格式示例】

仅回复：
{{
    "thought": "用户只是打招呼",
    "action_type": "reply_only",
    "response_to_user": "你好！有什么可以帮你的？"
}}

执行命令（需要等待返回值）：
{{
    "thought": "用户想查询数据，需要等待结果",
    "action_type": "call_command",
    "response_to_user": "正在为您查询数据，请稍候...",
    "command_id": "query_data",
    "command_params": "query": "用户的问题",
    "has_return": true,
    "wait_for_return": true
}}

执行命令（不需要等待，但追踪返回值）：
{{
    "thought": "用户想发送异步请求",
    "action_type": "call_command",
    "response_to_user": "已为您发送请求，正在处理中",
    "command_id": "async_request",
    "command_params": "data": "请求数据",
    "has_return": true,
    "wait_for_return": false
}}

【用户输入】
{user_input}
"""

def format_commands(commands: list) -> str:
    """格式化命令列表，显示返回值信息"""
    if not commands:
        return "（无可用命令）"
    formatted = []
    for cmd in commands:
        # 返回值信息
        return_info = ""
        if hasattr(cmd, 'has_return') and cmd.has_return:
            if hasattr(cmd, 'wait_for_return') and cmd.wait_for_return:
                return_info = " 🔒 需等待"
            else:
                return_info = " ⏳ 追踪中"
        
        line = f"- {cmd.id}: {cmd.description}{return_info}"
        formatted.append(line)
    return "\n".join(formatted)

def format_events(events: list) -> str:
    if not events:
        return "（无事件历史）"
    formatted = []
    for evt in events:
        line = f"[{evt.event_type.value}] {evt.message}"
        formatted.append(line)
    return "\n".join(formatted)

ARCHITECT_PROMPT_TEMPLATE = """
你是一个系统架构师 AI。你的任务是根据当前上下文，动态规划可用的状态和命令。

【当前上下文摘要】
{context_summary}

【用户最新输入】
{user_input}

【指令】
1. 分析用户意图和上下文
2. 定义当前状态描述（简短）
3. 生成 3-5 个最相关的可用命令（包含 ID、描述、has_return、wait_for_return）
4. 输出严格的 JSON 格式

【输出格式】
{format_example}
"""

ARCHITECT_FORMAT_EXAMPLE = """
{{
    "thought": "用户想搜索文件，需要搜索相关命令",
    "current_state_description": "文件搜索任务中",
    "available_commands": [
        {{
            "id": "search_file",
            "description": "搜索指定文件",
            "parameters_schema": {{"path": "str"}},
            "has_return": true,
            "wait_for_return": true
        }},
        {{
            "id": "notify_result",
            "description": "通知搜索结果",
            "parameters_schema": {{"message": "str"}},
            "has_return": false,
            "wait_for_return": false
        }}
    ]
}}
"""