#!/usr/bin/env python3
# src/cli.py

# =============================================================================
# 打包环境路径修复
# =============================================================================
import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# =============================================================================
# 导入
# =============================================================================
import typer
import questionary
from questionary import Choice
from typing import Dict, Any, Optional, List
import json
import yaml
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    USE_RICH = True
    console = Console()
except ImportError:
    USE_RICH = False
    console = None
    Panel = None

from core.controller import SystemController
from core.project_manager import ProjectManager
from core.project_loader import ProjectLoader

# =============================================================================
# Typer 应用
# =============================================================================
app = typer.Typer(help="状态驱动 AI 系统")

@app.callback(invoke_without_command=True)
def default_callback(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        main()

pm = ProjectManager()

# =============================================================================
# 主菜单
# =============================================================================
@app.command()
def main():
    """启动主菜单界面"""
    while True:
        choice = questionary.select(
            "=== 状态驱动 AI 系统 ===",
            choices=[
                Choice("📁 打开项目", "open"),
                Choice("➕ 新建项目", "create"),
                Choice("⚙️  系统设置", "settings"),
                Choice("❌ 退出", "exit")
            ]
        ).ask()
        
        if choice == "open":
            open_project_menu()
        elif choice == "create":
            create_project_menu()
        elif choice == "settings":
            settings_menu()
        elif choice == "exit" or choice is None:
            break

# =============================================================================
# 打开项目菜单
# =============================================================================
def open_project_menu():
    """打开项目选择菜单"""
    projects = pm.list_projects()
    
    choices = []
    for p in projects:
        choices.append(Choice(f"📂 {p['name']} ({p['version']})", p['path']))
    choices.append(Choice("🔙 返回", "back"))  # 返回的 value 设为 "back"
    
    selected = questionary.select("选择项目", choices=choices).ask()
    
    if selected == "back":
        return
    
    project_menu(selected)

# =============================================================================
# 新建项目菜单
# =============================================================================
def create_project_menu():
    """新建项目菜单"""
    # 选择保存位置
    location = questionary.select(
        "保存位置",
        choices=[
            Choice("📁 默认目录 (projects/)", "default"),
            Choice("📂 手动输入地址", "manual"),
            Choice("🔙 返回", "back")
        ]
    ).ask()
    
    if location == "back" or location is None:
        return
    
    # 输入项目名称
    name = questionary.text("项目名称").ask()
    if not name:
        print("❌ 项目名称不能为空")
        return
    
    # 确定保存路径
    save_path = None
    if location == "manual":
        save_path = questionary.text("输入保存路径").ask()
    
    try:
        path = pm.create_project(name, save_path)
        print(f"✅ 项目已创建：{path}")
        
        # 询问是否立即打开
        open_now = questionary.confirm("是否立即打开？").ask()
        if open_now:
            project_menu(path)
    except Exception as e:
        print(f"❌ 创建失败：{e}")

# =============================================================================
# 项目菜单
# =============================================================================
def project_menu(project_path: str):
    """项目内功能菜单"""
    config = pm.open_project(project_path)
    name = config.get("project", {}).get("name", "Unknown")
    
    while True:
        choice = questionary.select(
            f"=== 项目：{name} ===",
            choices=[
                Choice("💬 对话管理", "conv"),
                Choice("📝 命令管理", "cmd"),
                Choice("🗂️  状态编排", "state"),
                Choice("⚙️  项目配置", "config"),
                Choice("🔙 返回", "back")
            ]
        ).ask()
        
        if choice is None or choice == "back":
            return
        
        if choice == "conv":
            conversations_menu(project_path, config)
        elif choice == "cmd":
            commands_menu(project_path, config)
        elif choice == "state":
            states_menu(project_path, config)
        elif choice == "config":
            project_config_menu(project_path, config)

# =============================================================================
# 对话管理菜单
# =============================================================================
def conversations_menu(project_path: str, config: Dict):
    """对话管理菜单"""
    while True:
        convs = pm.list_conversations(project_path)
        
        choices = []
        for c in convs:
            choices.append(Choice(f"💬 {c['name']} ({c['message_count']}条)", c['id']))
        
        choices.extend([
            Choice("➕ 新建对话", "new"),
            Choice("👁️  查看对话", "view"),
            Choice("🗑️  删除对话", "delete"),
            Choice("🔙 返回", "back")
        ])
        
        choice = questionary.select("对话管理", choices=choices).ask()
        
        if choice == "back" or choice is None:
            break
        elif choice == "new":
            conv_name = questionary.text("对话名称（留空自动生成）").ask()
            conv_id = pm.create_conversation(project_path, conv_name)
            print("✅ 新对话已创建")
            
            # 修复：恢复新窗口选项
            open_mode = questionary.select(
                "打开方式",
                choices=[
                    Choice("🪟 新窗口打开", "new_window"),
                    Choice("▶️  当前窗口打开", "current"),
                    Choice("❌ 暂不打开", "cancel")
                ]
            ).ask()
            
            if open_mode == "new_window":
                run_project_in_new_window(project_path, config, conv_id)
            elif open_mode == "current":
                run_project(project_path, config, conv_id)
                
        elif choice == "view":
            if not convs:
                print("⚠️  暂无对话可查看")
                continue
            
            view_choices = [Choice(f"💬 {c['name']} ({c['message_count']}条)", c['id']) for c in convs]
            sel = questionary.select("选择查看", choices=view_choices).ask()
            
            if sel:
                conv_data = pm.view_conversation(project_path, sel)
                if conv_data:
                    print(f"\n{'='*60}")
                    print(f"对话：{conv_data.get('name', sel)}")
                    print(f"创建：{conv_data.get('created', 'Unknown')}")
                    print(f"更新：{conv_data.get('updated', 'Unknown')}")
                    messages = conv_data.get("messages", [])
                    print(f"总消息数：{len(messages)}")
                    print(f"{'='*60}\n")
                    
                    for i, msg in enumerate(messages, 1):
                        role = msg.get("role", "unknown")
                        content = msg.get("content", "")
                        if role == "user":
                            print(f"[{i}] 👤 用户：{content}")
                        else:
                            print(f"[{i}] 🤖 AI:")
                            for line in content.split('\n'):
                                print(f"    {line}")
                        print()
                    
                    print(f"{'='*60}\n")
                else:
                    print("❌ 无法加载对话")
                    
        elif choice == "delete":
            if not convs:
                print("⚠️  暂无对话可删除")
                continue
            
            del_choices = [Choice(f"💬 {c['name']} ({c['message_count']}条)", c['id']) for c in convs]
            sel = questionary.select("选择删除", choices=del_choices).ask()
            if sel and questionary.confirm("确定删除？").ask():
                pm.delete_conversation(project_path, sel)
                print("✅ 已删除")
                
        elif choice:
            # 修复：恢复新窗口选项
            open_mode = questionary.select(
                "打开方式",
                choices=[
                    Choice("🪟 新窗口打开", "new_window"),
                    Choice("▶️  当前窗口打开", "current"),
                ]
            ).ask()
            
            if open_mode == "new_window":
                run_project_in_new_window(project_path, config, choice)
            elif open_mode == "current":
                run_project(project_path, config, choice)

# =============================================================================
# 命令管理菜单
# =============================================================================
def commands_menu(project_path: str, config: Dict):
    """命令管理菜单"""
    import re
    
    while True:
        commands = config.get("commands", [])
        choices = [Choice(f"⚡ {c['id']}: {c['description']}", i) 
                   for i, c in enumerate(commands)]
        choices.extend([
            Choice("➕ 添加命令", "add"),
            Choice("🔙 返回", "back")
        ])
        
        choice = questionary.select("命令管理", choices=choices).ask()
        
        if choice == "back" or choice is None:
            pm.save_project(project_path, config)
            break
        elif choice == "add":
            # =============================================================
            # 1. 命令 ID 验证（强制格式）
            # =============================================================
            while True:
                cmd_id = questionary.text(
                    "命令 ID（只允许小写字母、数字、下划线，必须以字母开头）"
                ).ask()
                
                if not cmd_id:
                    print("❌ 命令 ID 不能为空")
                    continue
                
                # 验证格式
                if not re.match(r'^[a-z][a-z0-9_-]*$', cmd_id):
                    print("❌ 格式错误！示例：help, search_file, get_data")
                    continue
                
                # 检查是否重复
                existing_ids = [c["id"] for c in commands]
                if cmd_id in existing_ids:
                    print(f"❌ 命令 ID '{cmd_id}' 已存在")
                    continue
                
                break
            
            cmd_desc = questionary.text("命令描述").ask()
            
            # =============================================================
            # 2. 处理器类型（先选择处理器）
            # =============================================================
            processor_category = questionary.select(
                "处理器类别",
                choices=[
                    Choice("💬 回复类", "reply"),
                    Choice("⚙️ 系统类", "system"),
                    Choice("🌐 外部请求类", "external"),
                    Choice("📤 数据输出类", "output"),
                    Choice("⏳ 等待类", "wait"),
                    Choice("⚪ 无处理器", "none")
                ]
            ).ask()
            
            handler_type = None
            if processor_category == "reply":
                handler_type = questionary.select(
                    "选择处理器",
                    choices=[Choice("📝 文本回复 (echo)", "echo")]
                ).ask()
            elif processor_category == "system":
                handler_type = questionary.select(
                    "选择处理器",
                    choices=[Choice("🔄 状态跳转 (state_jump)", "state_jump")]
                ).ask()
            elif processor_category == "external":
                handler_type = questionary.select(
                    "选择处理器",
                    choices=[
                        Choice("🌐 HTTP 请求 (http_request)", "http_request"),
                        Choice("💻 系统命令 (run_command)", "run_command"),
                        Choice("🔌 Python 插件 (plugin)", "plugin")
                    ]
                ).ask()
            elif processor_category == "output":
                handler_type = questionary.select(
                    "选择处理器",
                    choices=[Choice("📤 传出数据 (output)", "output")]
                ).ask()
            elif processor_category == "wait":
                handler_type = questionary.select(
                    "选择处理器",
                    choices=[
                        Choice("👤 等待用户输入 (wait_for_user)", "wait_for_user"),
                        Choice("🌐 等待外部回调 (wait_for_external)", "wait_for_external")
                    ]
                ).ask()
            
            # =============================================================
            # 3. 返回值设置（根据处理器类别自动判断）
            # =============================================================
            has_return = False
            return_type = None
            wait_for_return = False
            
            # 含义：根据处理器类别自动设置返回值
            if processor_category in ["external", "output"]:
                # 外部请求和数据输出通常有自动返回值
                has_return = questionary.confirm(
                    "是否有返回值？",
                    default=True
                ).ask()
                if has_return:
                    return_type = "auto"
                    wait_for_return = questionary.confirm(
                        "是否需要等待返回值后再回复用户？",
                        default=False
                    ).ask()
            elif processor_category == "wait":
                # 等待类一定有手动返回值
                has_return = True
                return_type = "manual"
                wait_for_return = questionary.confirm(
                    "是否需要等待返回值后再回复用户？",
                    default=True
                ).ask()
            else:
                # 回复类、系统类、无处理器通常没有返回值
                has_return = False
            
            # =============================================================
            # 4. 处理器配置（根据处理器类型询问）
            # =============================================================
            handler_config = _build_handler_config(handler_type)
            
            # =============================================================
            # 5. 保存命令配置
            # =============================================================
            cmd_entry = {
                "id": cmd_id,
                "description": cmd_desc,
                "parameters_schema": {},
                "processor_category": processor_category,
                "handler": {
                    "type": handler_type,
                    "config": handler_config
                } if handler_type and handler_type != "none" else None,
                "return_settings": {
                    "has_return": has_return,
                    "return_type": return_type,
                    "wait_for_return": wait_for_return
                } if has_return else None
            }
            
            config["commands"].append(cmd_entry)
            print("✅ 命令已添加")
            
        elif isinstance(choice, int):
            cmd = commands[choice]
            cmd_action = questionary.select(
                f"命令：{cmd['id']}",
                choices=[
                    Choice("✏️  编辑基本信息", "edit_basic"),
                    Choice("🔖 重命名命令", "rename"),
                    Choice("🔧 修改处理器", "edit_handler"),
                    Choice("⏱️  修改返回值设置", "edit_return"),
                    Choice("🗑️  删除命令", "delete"),
                    Choice("🔙 取消", "cancel")
                ]
            ).ask()
            
            if cmd_action == "edit_basic":
                cmd["description"] = questionary.text(
                    "描述", default=cmd.get("description", "")
                ).ask()
            elif cmd_action == "rename":
                # =============================================================
                # 【新增】重命名命令（带验证和引用更新）
                # =============================================================
                old_id = cmd["id"]
                while True:
                    new_id = questionary.text(
                        f"新命令 ID（当前：{old_id}）"
                    ).ask()
                    
                    if not new_id:
                        print("❌ 命令 ID 不能为空")
                        continue
                    
                    if not re.match(r'^[a-z][a-z0-9_-]*$', new_id):
                        print("❌ 格式错误！示例：help, search_file, get_data")
                        continue
                    
                    if new_id == old_id:
                        print("⚠️  新 ID 与旧 ID 相同，无需更改")
                        break
                    
                    existing_ids = [c["id"] for i, c in enumerate(commands) if i != choice]
                    if new_id in existing_ids:
                        print(f"❌ 命令 ID '{new_id}' 已存在")
                        continue
                    
                    break
                
                if new_id and new_id != old_id:
                    # 更新命令 ID
                    cmd["id"] = new_id
                    
                    # 更新所有状态中的引用
                    states = config.get("states", [])
                    updated_count = 0
                    for state in states:
                        # 更新 available_commands
                        if old_id in state.get("available_commands", []):
                            state["available_commands"] = [
                                new_id if cmd_id == old_id else cmd_id
                                for cmd_id in state["available_commands"]
                            ]
                            updated_count += 1
                        
                        # 更新 command_transitions
                        if "command_transitions" in state:
                            if old_id in state["command_transitions"]:
                                state["command_transitions"][new_id] = state["command_transitions"].pop(old_id)
                                updated_count += 1
                    
                    pm.save_project(project_path, config)
                    print(f"✅ 命令已重命名：{old_id} → {new_id}")
                    print(f"✅ 已更新 {updated_count} 个状态中的引用")
            elif cmd_action == "edit_handler":
                # =============================================================
                # 1. 显示当前处理器信息
                # =============================================================
                current_handler = cmd.get("handler", {})
                current_type = current_handler.get("type", "none") if current_handler else "none"
                
                print(f"\n当前处理器类型：{current_type}")
                if current_handler:
                    print(f"当前配置：{current_handler.get('config', {})}")
                
                # =============================================================
                # 2. 重新选择处理器类别
                # =============================================================
                processor_category = questionary.select(
                    "处理器类别",
                    choices=[
                        Choice("💬 回复类", "reply"),
                        Choice("⚙️ 系统类", "system"),
                        Choice("🌐 外部请求类", "external"),
                        Choice("📤 数据输出类", "output"),
                        Choice("⏳ 等待类", "wait"),
                        Choice("⚪ 无处理器", "none")
                    ],
                    default=current_processor_category(cmd)
                ).ask()
                
                # =============================================================
                # 3. 选择具体处理器
                # =============================================================
                handler_type = None
                if processor_category == "reply":
                    handler_type = questionary.select(
                        "选择处理器",
                        choices=[Choice("📝 文本回复 (echo)", "echo")]
                    ).ask()
                elif processor_category == "system":
                    handler_type = questionary.select(
                        "选择处理器",
                        choices=[Choice("🔄 状态跳转 (state_jump)", "state_jump")]
                    ).ask()
                elif processor_category == "external":
                    handler_type = questionary.select(
                        "选择处理器",
                        choices=[
                            Choice("🌐 HTTP 请求 (http_request)", "http_request"),
                            Choice("💻 系统命令 (run_command)", "run_command"),
                            Choice("🔌 Python 插件 (plugin)", "plugin")
                        ]
                    ).ask()
                elif processor_category == "output":
                    handler_type = questionary.select(
                        "选择处理器",
                        choices=[Choice("📤 传出数据 (output)", "output")]
                    ).ask()
                elif processor_category == "wait":
                    handler_type = questionary.select(
                        "选择处理器",
                        choices=[
                            Choice("👤 等待用户输入 (wait_for_user)", "wait_for_user"),
                            Choice("🌐 等待外部回调 (wait_for_external)", "wait_for_external")
                        ]
                    ).ask()
                
                # =============================================================
                # 4. 根据处理器类别自动设置返回值
                # =============================================================
                has_return = False
                return_type = None
                wait_for_return = False
                
                if processor_category in ["external", "output"]:
                    has_return = questionary.confirm(
                        "是否有返回值？",
                        default=True
                    ).ask()
                    if has_return:
                        return_type = "auto"
                        wait_for_return = questionary.confirm(
                            "是否需要等待返回值后再回复用户？",
                            default=False
                        ).ask()
                elif processor_category == "wait":
                    has_return = True
                    return_type = "manual"
                    wait_for_return = questionary.confirm(
                        "是否需要等待返回值后再回复用户？",
                        default=True
                    ).ask()
                else:
                    has_return = False
                
                # =============================================================
                # 5. 重新配置处理器参数
                # =============================================================
                print("\n重新配置处理器参数：")
                handler_config = _build_handler_config(handler_type)
                
                # =============================================================
                # 6. 更新命令配置
                # =============================================================
                cmd["processor_category"] = processor_category
                cmd["handler"] = {
                    "type": handler_type,
                    "config": handler_config
                } if handler_type and handler_type != "none" else None
                
                cmd["return_settings"] = {
                    "has_return": has_return,
                    "return_type": return_type,
                    "wait_for_return": wait_for_return
                } if has_return else None
                
                print("✅ 处理器已更新")
            elif cmd_action == "edit_return":
                # =============================================================
                # 【关键修复】正确处理 None 值
                # =============================================================
                current = cmd.get("return_settings")
                if current is None:
                    current = {}
                
                has_return = questionary.confirm(
                    "是否有返回值？",
                    default=current.get("has_return", False) if current else False
                ).ask()
                
                if has_return:
                    return_type = questionary.select(
                        "返回值类型",
                        choices=[
                            Choice("🔄 自动", "auto"),
                            Choice("👤 手动", "manual")
                        ],
                        default=current.get("return_type", "auto") if current else "auto"
                    ).ask()
                    
                    wait_for_return = questionary.confirm(
                        "是否需要等待返回值后再回复用户？",
                        default=current.get("wait_for_return", False) if current else False
                    ).ask()
                    
                    cmd["return_settings"] = {
                        "has_return": has_return,
                        "return_type": return_type,
                        "wait_for_return": wait_for_return
                    }
                else:
                    cmd["return_settings"] = None
            elif cmd_action == "delete":
                old_id = cmd["id"]
                confirm = questionary.confirm(f"确定删除命令 '{old_id}'？").ask()
                if confirm:
                    config["commands"].pop(choice)
                    
                    # 清理所有状态中的引用
                    states = config.get("states", [])
                    for state in states:
                        if old_id in state.get("available_commands", []):
                            state["available_commands"].remove(old_id)
                        if "command_transitions" in state:
                            if old_id in state["command_transitions"]:
                                del state["command_transitions"][old_id]
                    
                    pm.save_project(project_path, config)
                    print(f"✅ 命令 '{old_id}' 已删除")

def current_processor_category(cmd: Dict) -> str:
    """获取命令当前的处理器类别"""
    processor_category = cmd.get("processor_category")
    if processor_category:
        return processor_category
    
    # 兼容旧配置：根据 handler type 推断类别
    handler = cmd.get("handler", {})
    if handler:
        handler_type = handler.get("type", "")
        if handler_type == "echo":
            return "reply"
        elif handler_type == "state_jump":
            return "system"
        elif handler_type in ["http_request", "run_command", "plugin"]:
            return "external"
        elif handler_type == "output":
            return "output"
        elif handler_type in ["wait_for_user", "wait_for_external"]:
            return "wait"
    
    return "none"

def _build_handler_config(handler_type: str, current_config: Dict = None) -> Dict:
    """构建处理器配置"""
    if current_config is None:
        current_config = {}
    
    config = {}
    
    if handler_type == "echo":
        config["text"] = questionary.text(
            "返回文本（支持 ${param} 参数）",
            default=current_config.get("text", "")
        ).ask()
    elif handler_type == "run_command":
        config["command"] = questionary.text(
            "系统命令",
            default=current_config.get("command", "")
        ).ask()
        config["timeout"] = questionary.text(
            "超时时间 (秒)",
            default=str(current_config.get("timeout", 30))
        ).ask()
    elif handler_type == "http_request":
        config["url"] = questionary.text(
            "API URL",
            default=current_config.get("url", "")
        ).ask()
        config["method"] = questionary.select(
            "HTTP 方法",
            choices=[
                Choice("GET", "GET"),
                Choice("POST", "POST"),
                Choice("PUT", "PUT"),
                Choice("DELETE", "DELETE")
            ],
            default=current_config.get("method", "GET")
        ).ask()
        config["timeout"] = questionary.text(
            "超时时间 (秒)",
            default=str(current_config.get("timeout", 30))
        ).ask()
    elif handler_type == "plugin":
        config["function"] = questionary.text(
            "插件函数名（handlers.py 中的函数）",
            default=current_config.get("function", "")
        ).ask()
    elif handler_type == "state_jump":
        config["target"] = questionary.text(
            "目标状态 ID",
            default=current_config.get("target", "")
        ).ask()
    elif handler_type == "output":
        config["output_key"] = questionary.text(
            "输出数据键名",
            default=current_config.get("output_key", "")
        ).ask()
        config["format"] = questionary.select(
            "输出格式",
            choices=[
                Choice("JSON", "json"),
                Choice("文本", "text")
            ],
            default=current_config.get("format", "json")
        ).ask()
    elif handler_type == "wait_for_user":
        config["prompt"] = questionary.text(
            "提示用户输入的内容",
            default=current_config.get("prompt", "请输入返回值")
        ).ask()
    elif handler_type == "wait_for_external":
        config["file_path"] = questionary.text(
            "返回值文件路径",
            default=current_config.get("file_path", "conversations/returns/")
        ).ask()
        config["timeout"] = questionary.text(
            "超时时间 (秒)",
            default=str(current_config.get("timeout", 300))
        ).ask()
    
    return config

# =============================================================================
# 状态编排菜单
# =============================================================================
def states_menu(project_path: str, config: Dict):
    """状态编排菜单"""
    import re
    
    while True:
        states = config.get("states", [])
        choices = [Choice(f"📍 {s['id']}: {s['description']}", i) 
                   for i, s in enumerate(states)]
        choices.extend([
            Choice("➕ 添加状态", "add"),
            Choice("🔙 返回", "back")
        ])
        
        choice = questionary.select("状态编排", choices=choices).ask()
        
        if choice == "back" or choice is None:
            pm.save_project(project_path, config)
            break
        elif choice == "add":
            # =============================================================
            # 1. 状态 ID 验证（强制格式）
            # =============================================================
            while True:
                state_id = questionary.text(
                    "状态 ID（只允许小写字母、数字、下划线，必须以字母开头）"
                ).ask()
                
                if not state_id:
                    print("❌ 状态 ID 不能为空")
                    continue
                
                # 验证格式
                if not re.match(r'^[a-z][a-z0-9_-]*$', state_id):
                    print("❌ 格式错误！示例：root, search_state, settings")
                    continue
                
                # 检查是否重复
                existing_ids = [s["id"] for s in states]
                if state_id in existing_ids:
                    print(f"❌ 状态 ID '{state_id}' 已存在")
                    continue
                
                break
            
            state_desc = questionary.text("状态描述").ask()
            state_mode = questionary.select(
                "模式",
                choices=[
                    Choice("稳定模式 (stable)", "stable"),
                    Choice("自由模式 (free)", "free")
                ]
            ).ask()
            
            # 父状态选择
            parent_choices = [Choice("(无)", None)]
            for s in states:
                parent_choices.append(Choice(s["id"], s["id"]))
            parent_id = questionary.select("父状态 ID", choices=parent_choices).ask()
            
            config["states"].append({
                "id": state_id,
                "description": state_desc,
                "mode": state_mode,
                "parent_id": parent_id,
                "available_commands": [],
                "command_transitions": {}
            })
            print("✅ 状态已添加")
            
        elif isinstance(choice, int):
            state = states[choice]
            old_id = state["id"]
            
            state_action = questionary.select(
                f"状态：{old_id}",
                choices=[
                    Choice("✏️  编辑", "edit"),
                    Choice("🔖 重命名状态", "rename"),
                    Choice("📋 编辑可用命令", "commands"),
                    Choice("🔗 编辑命令跳转", "transitions"),
                    Choice("🗑️  删除", "delete"),
                    Choice("🔙 取消", "cancel")
                ]
            ).ask()
            
            if state_action == "edit":
                state["description"] = questionary.text("描述", default=state["description"]).ask()
                state["mode"] = questionary.select(
                    "模式",
                    choices=[
                        Choice("稳定模式 (stable)", "stable"),
                        Choice("自由模式 (free)", "free")
                    ],
                    default=state["mode"]
                ).ask()
            elif state_action == "rename":
                # =============================================================
                # 【新增】重命名状态（带验证和引用更新）
                # =============================================================
                while True:
                    new_id = questionary.text(
                        f"新状态 ID（当前：{old_id}）"
                    ).ask()
                    
                    if not new_id:
                        print("❌ 状态 ID 不能为空")
                        continue
                    
                    if not re.match(r'^[a-z][a-z0-9_-]*$', new_id):
                        print("❌ 格式错误！示例：root, search_state, settings")
                        continue
                    
                    if new_id == old_id:
                        print("⚠️  新 ID 与旧 ID 相同，无需更改")
                        break
                    
                    existing_ids = [s["id"] for i, s in enumerate(states) if i != choice]
                    if new_id in existing_ids:
                        print(f"❌ 状态 ID '{new_id}' 已存在")
                        continue
                    
                    break
                
                if new_id and new_id != old_id:
                    # 更新状态 ID
                    state["id"] = new_id
                    
                    # 更新所有引用
                    updated_count = 0
                    for s in states:
                        # 更新 parent_id
                        if s.get("parent_id") == old_id:
                            s["parent_id"] = new_id
                            updated_count += 1
                        
                        # 更新 command_transitions 中的目标状态
                        if "command_transitions" in s:
                            for cmd_id, target in list(s["command_transitions"].items()):
                                if target == old_id:
                                    s["command_transitions"][cmd_id] = new_id
                                    updated_count += 1
                    
                    # 更新 initial_state
                    if config.get("initial_state") == old_id:
                        config["initial_state"] = new_id
                        updated_count += 1
                    
                    pm.save_project(project_path, config)
                    print(f"✅ 状态已重命名：{old_id} → {new_id}")
                    print(f"✅ 已更新 {updated_count} 个引用")
            elif state_action == "commands":
                all_cmds = config.get("commands", [])
                if not all_cmds:
                    print("⚠️  请先在命令管理中添加命令")
                    continue
                
                cmd_ids = [c["id"] for c in all_cmds]
                current = state.get("available_commands", [])
                if current is None:
                    current = []
                if not isinstance(current, list):
                    current = []
                valid_defaults = [cmd for cmd in current if cmd in cmd_ids]
                
                cmd_choices = []
                for c in all_cmds:
                    is_checked = c["id"] in valid_defaults
                    cmd_choices.append(Choice(c["id"], c["id"], checked=is_checked))
                
                selected = questionary.checkbox(
                    "选择可用命令",
                    choices=cmd_choices
                ).ask()
                
                if selected is not None:
                    state["available_commands"] = selected
                    print(f"✅ 已更新可用命令：{selected}")
                    
            elif state_action == "transitions":
                all_states = [s["id"] for s in config.get("states", [])]
                for cmd_id in state.get("available_commands", []):
                    target = questionary.select(
                        f"命令 '{cmd_id}' 跳转到",
                        choices=[Choice("(无跳转)", None)] + [Choice(s, s) for s in all_states],
                        default=state.get("command_transitions", {}).get(cmd_id)
                    ).ask()
                    if target:
                        if "command_transitions" not in state:
                            state["command_transitions"] = {}
                        state["command_transitions"][cmd_id] = target
            elif state_action == "delete":
                confirm = questionary.confirm(f"确定删除状态 '{old_id}'？").ask()
                if confirm:
                    # 检查是否有其他状态引用此状态
                    ref_count = 0
                    for s in states:
                        if s.get("parent_id") == old_id:
                            ref_count += 1
                        if "command_transitions" in s:
                            for cmd_id, target in s["command_transitions"].items():
                                if target == old_id:
                                    ref_count += 1
                    
                    if ref_count > 0:
                        force = questionary.confirm(
                            f"⚠️  有 {ref_count} 个引用指向此状态，确定删除？"
                        ).ask()
                        if not force:
                            continue
                    
                    config["states"].pop(choice)
                    
                    # 清理引用
                    for s in states:
                        if s.get("parent_id") == old_id:
                            s["parent_id"] = None
                        if "command_transitions" in s:
                            s["command_transitions"] = {
                                cmd_id: target
                                for cmd_id, target in s["command_transitions"].items()
                                if target != old_id
                            }
                    
                    # 更新 initial_state
                    if config.get("initial_state") == old_id:
                        config["initial_state"] = "root"
                    
                    pm.save_project(project_path, config)
                    print(f"✅ 状态 '{old_id}' 已删除")

# =============================================================================
# 项目配置菜单
# =============================================================================
def project_config_menu(project_path: str, config: Dict):
    """项目配置菜单"""
    while True:
        choice = questionary.select(
            "项目配置",
            choices=[
                Choice("🔑 API 配置", "api"),
                Choice("🏷️  项目信息", "info"),
                Choice("🔙 返回", "back")
            ]
        ).ask()
        
        if choice == "back" or choice is None:
            pm.save_project(project_path, config)
            break
        elif choice == "api":
            if "api" not in config:
                config["api"] = {}
            current_key = config["api"].get("key", "")
            api_key = questionary.password(
                "API Key",
                default=current_key if current_key else ""
            ).ask()
            if api_key:
                config["api"]["key"] = api_key
            base_url = questionary.text(
                "API Base URL",
                default=config["api"].get("base_url", "https://api.openai.com/v1")
            ).ask()
            model = questionary.text(
                "模型名称",
                default=config["api"].get("model", "gpt-3.5-turbo")
            ).ask()
            config["api"]["base_url"] = base_url
            config["api"]["model"] = model
            pm.save_project(project_path, config)
            print("✅ API 配置已保存")
        elif choice == "info":
            config["project"]["name"] = questionary.text(
                "项目名称", default=config.get("project", {}).get("name", "")
            ).ask()
            config["project"]["version"] = questionary.text(
                "版本号", default=config.get("project", {}).get("version", "")
            ).ask()
            pm.save_project(project_path, config)
            print("✅ 项目信息已保存")

# =============================================================================
# 系统设置菜单
# =============================================================================
def settings_menu():
    """系统设置菜单"""
    while True:
        choice = questionary.select(
            "系统设置",
            choices=[
                Choice("🔑 全局 API 配置", "api"),
                Choice("📏 上下文长度", "context"),
                Choice("⏱️  命令超时时间", "timeout"),
                Choice("📂 项目目录设置", "dir"),
                Choice("🔙 返回", "back")
            ]
        ).ask()
        
        if choice == "back" or choice is None:
            break
        elif choice == "api":
            current = pm.get_global_api_config()
            key = questionary.password("API Key", default=current.get("key", "")).ask()
            url = questionary.text("Base URL", default=current.get("base_url", "https://api.openai.com/v1")).ask()
            model = questionary.text("Model", default=current.get("model", "gpt-3.5-turbo")).ask()
            pm.set_global_api_config(key or current.get("key", ""), url, model)
            print("✅ API 配置已保存")
        elif choice == "context":
            current = pm.get_context_length()
            new = questionary.text("上下文长度 (1-50)", default=str(current)).ask()
            try:
                pm.set_context_length(max(1, min(50, int(new))))
                print(f"✅ 上下文长度已设置为 {new}")
            except:
                print("❌ 请输入有效数字")
        elif choice == "timeout":
            current = pm.get_command_timeout()
            new = questionary.text("命令超时时间 (秒，5-300)", default=str(current)).ask()
            try:
                timeout = int(new)
                if timeout < 5:
                    timeout = 5
                elif timeout > 300:
                    timeout = 300
                pm.set_command_timeout(timeout)
                print(f"✅ 命令超时时间已设置为 {timeout} 秒")
            except:
                print("❌ 请输入有效数字")
        elif choice == "dir":
            new_path = questionary.text("项目根目录路径").ask()
            if new_path:
                pm.projects_root = Path(new_path)
                print(f"✅ 项目目录已设置为：{new_path}")

# =============================================================================
# 运行项目
# =============================================================================
def run_project(project_path: str, config: Dict, conv_id: str = None):
    """运行项目"""
    api = config.get("api", {})
    if not api.get("key"):
        g = pm.get_global_api_config()
        if g.get("key"):
            config["api"] = g
        else:
            print("❌ 未配置 API")
            return
    
    pm.save_project(project_path, config)
    
    try:
        loader = ProjectLoader(project_path)
        controller = SystemController(initial_state_id=config.get("initial_state", "root"))
        
        if conv_id:
            data = pm.load_conversation(project_path, conv_id)
            controller.conversation_history = [
                f"{m['role']}: {m['content']}" 
                for m in data.get("messages", [])
            ]
            curr_id = conv_id
            conv_name = data.get("name", conv_id)
        else:
            curr_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            conv_name = f"对话 {curr_id}"
        
        info = loader.apply_to(controller)
        
        print(f"\n=== {info['project_name']} - {conv_name} ===")
        print(f"上下文长度：{pm.get_context_length()} 轮")
        print(f"命令超时：{pm.get_command_timeout()} 秒")
        print(f"输入 'exit' 退出，'history' 查看历史，'returns' 查看返回值状态\n")
        
        while True:
            try:
                pending = controller.get_pending_returns()
                if pending:
                    print(f"\n⏳ 等待中的返回值 ({len(pending)} 个):")
                    for p in pending:
                        status_map = {
                            "waiting": "🔒 阻塞等待",
                            "pending": "⏳ 追踪中",
                            "completed": "✅ 已完成",
                            "timeout": "❌ 已超时"
                        }
                        icon = status_map.get(p["status"], "❓")
                        print(f"   {icon} {p['command_id']} ({p['status']})")
                    print(f"   输入 'return <command_id> <值>' 提交返回值")
                    print(f"   输入 'clear' 清理已完成的返回值\n")
                
                user = typer.prompt("用户")
                
                if user.lower() in ["exit", "quit"]:
                    _save_conv(pm, project_path, curr_id, controller)
                    break
                
                if user.lower() == "history":
                    print(f"\n=== 当前对话历史 ({len(controller.conversation_history)} 条) ===")
                    for msg in controller.conversation_history[-10:]:
                        print(f"  {msg}")
                    print("=" * 50)
                    continue
                
                if user.lower() == "returns":
                    history = controller.get_return_history()
                    if history:
                        print(f"\n=== 返回值历史 ({len(history)} 个) ===")
                        for p in history:
                            status_icon = {
                                "waiting": "🔒",
                                "pending": "⏳",
                                "completed": "✅",
                                "timeout": "❌"
                            }.get(p["status"], "❓")
                            print(f"  {status_icon} {p['command_id']} ({p['status']})")
                            print(f"     创建：{p['created']}")
                            if p.get('completed'):
                                print(f"     完成：{p['completed']}")
                            if p.get('value'):
                                print(f"     返回值：{str(p['value'])[:100]}...")
                            print("-" * 40)
                        print("=" * 50)
                    else:
                        print("暂无返回值记录")
                    continue
                
                if user.lower().startswith("return "):
                    parts = user[7:].split(" ", 1)
                    if len(parts) >= 2:
                        cmd_id = parts[0]
                        return_value = parts[1]
                        controller.conversation_history.append(f"User: [RETURN]{cmd_id}:{return_value}")
                        feedback = controller.process_user_input(f"[RETURN]{cmd_id}:{return_value}")
                        ai = controller.get_last_response()
                        if ai:
                            print(f"AI: {ai}")
                    else:
                        print("❌ 格式：return <command_id> <返回值>")
                    continue
                
                if user.lower() == "clear":
                    controller.clear_completed_returns()
                    print("✅ 已清理已完成的返回值")
                    continue
                
                feedback = controller.process_user_input(user)
                ai = controller.get_last_response()
                output_data = controller.get_last_output()
                
                if output_data:
                    print(f"📤 输出数据：{output_data}")
                
                if ai:
                    print(f"AI: {ai}")
                
            except KeyboardInterrupt:
                _save_conv(pm, project_path, curr_id, controller)
                break
            except Exception as e:
                print(f"❌ 错误：{e}")
    
    except Exception as e:
        print(f"❌ 启动失败：{e}")

def _save_conv(pm, project_path, conv_id, controller):
    """保存对话历史"""
    msgs = []
    for m in controller.conversation_history:
        if m.startswith("User:"):
            msgs.append({"role": "user", "content": m[5:]})
        elif m.startswith("Assistant:"):
            msgs.append({"role": "assistant", "content": m[12:]})
        elif m.startswith("System:"):
            msgs.append({"role": "system", "content": m[8:]})
    pm.save_conversation(project_path, conv_id, msgs)
    print(f"\n✅ 对话已保存 ({len(msgs)} 条消息)")

# =============================================================================
# 新窗口运行功能
# =============================================================================

def run_project_in_new_window(project_path: str, config: Dict, conv_id: str = None):
    """在新终端窗口中运行项目"""
    import subprocess
    import sys
    
    is_packaged = getattr(sys, 'frozen', False)
    
    try:
        if sys.platform == "darwin":  # macOS
            if is_packaged:
                exe = sys.executable
                if conv_id:
                    script = f'''
                    tell application "Terminal"
                        activate
                        do script "{exe} run-single '{project_path}' --conv '{conv_id}'"
                    end tell
                    '''
                else:
                    script = f'''
                    tell application "Terminal"
                        activate
                        do script "{exe} run-single '{project_path}'"
                    end tell
                    '''
            else:
                cli_path = Path(__file__).absolute()
                if conv_id:
                    script = f'''
                    tell application "Terminal"
                        activate
                        do script "cd '{cli_path.parent}' && {sys.executable} '{cli_path}' run-single '{project_path}' --conv '{conv_id}'"
                    end tell
                    '''
                else:
                    script = f'''
                    tell application "Terminal"
                        activate
                        do script "cd '{cli_path.parent}' && {sys.executable} '{cli_path}' run-single '{project_path}'"
                    end tell
                    '''
            subprocess.run(["osascript", "-e", script])
            print("✅ 已在新窗口中启动")
            
        elif sys.platform == "win32":  # Windows
            if is_packaged:
                if conv_id:
                    cmd = f'start "LX_AI" "{sys.executable}" run-single "{project_path}" --conv "{conv_id}"'
                else:
                    cmd = f'start "LX_AI" "{sys.executable}" run-single "{project_path}"'
            else:
                cli_path = Path(__file__).absolute()
                if conv_id:
                    cmd = f'start "LX_AI" "{sys.executable}" "{cli_path}" run-single "{project_path}" --conv "{conv_id}"'
                else:
                    cmd = f'start "LX_AI" "{sys.executable}" "{cli_path}" run-single "{project_path}"'
            subprocess.Popen(cmd, shell=True)
            print("✅ 已在新窗口中启动")
            
        else:  # Linux
            print("⚠️  Linux 请使用终端手动运行")
            run_project(project_path, config, conv_id)
            
    except Exception as e:
        print(f"❌ 打开新窗口失败：{e}")
        run_project(project_path, config, conv_id)

# =============================================================================
# 子命令：单窗口运行
# =============================================================================

@app.command("run-single")
def run_single_cmd(
    project_path: str = typer.Argument(..., help="项目路径"),
    conv_id: Optional[str] = typer.Option(None, "--conv", "-c", help="对话 ID")
):
    """单窗口运行项目"""
    config = pm.open_project(project_path)
    run_project(project_path, config, conv_id)

# =============================================================================
# 入口
# =============================================================================
if __name__ == "__main__":
    app()
