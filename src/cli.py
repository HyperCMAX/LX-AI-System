#!/usr/bin/env python3
# src/cli.py

# =============================================================================
# 打包环境路径修复（必须放在最前面）
# =============================================================================
import sys
import os
from pathlib import Path

# 含义：添加当前目录到路径
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# =============================================================================
# 导入（使用绝对导入）
# =============================================================================
import typer
import questionary
from questionary import Choice
from typing import Dict, Any, Optional, List
import json
import yaml
from datetime import datetime

# 含义：富文本导入
try:
    from rich.console import Console
    from rich.panel import Panel
    USE_RICH = True
    console = Console()
except ImportError:
    USE_RICH = False
    console = None
    Panel = None

# 含义：核心模块导入（绝对路径）
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
                Choice("⚙️  系统设置", "settings"),
                Choice("❌ 退出", "exit")
            ]
        ).ask()
        
        if choice == "open":
            open_project_menu()
        elif choice == "settings":
            settings_menu()
        elif choice == "exit" or choice is None:
            break


# =============================================================================
# 项目菜单
# =============================================================================

def open_project_menu():
    """打开项目选择菜单"""
    projects = pm.list_projects()
    if not projects:
        if USE_RICH and console:
            console.print("[yellow]⚠️  暂无项目[/yellow]")
        else:
            print("⚠️  暂无项目")
        return
    
    choices = [Choice(f"📂 {p['name']}", p['path']) for p in projects]
    choices.append(Choice("🔙 返回", None))
    
    selected = questionary.select("选择项目", choices=choices).ask()
    
    # 修复：检查 None 或空值
    if selected is None:
        return  # 用户选择返回，直接退出
    
    project_menu(selected)


def create_project_menu():
    """新建项目菜单"""
    name = questionary.text("项目名称").ask()
    if not name:
        return

    location = questionary.select(
        "保存位置",
        choices=[
            Choice("📁 默认目录 (projects/)", "default"),
            Choice("📂 自定义路径", "custom")
        ]
    ).ask()

    save_path = None
    if location == "custom":
        save_path = questionary.text("输入保存路径").ask()

    try:
        path = pm.create_project(name, save_path)
        if USE_RICH and console:
            console.print(f"[green]✅ 项目已创建：{path}[/green]")
        else:
            print(f"✅ 项目已创建：{path}")
        open_now = questionary.confirm("是否立即打开？").ask()
        if open_now:
            project_menu(path)
    except Exception as e:
        if USE_RICH and console:
            console.print(f"[red]❌ 创建失败：{str(e)}[/red]")
        else:
            print(f"❌ 创建失败：{str(e)}")


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
        
        # 修复：检查 None 或 back
        if choice is None or choice == "back":
            return  # 返回主菜单
        
        if choice == "conv":
            conversations_menu(project_path, config)
        elif choice == "cmd":
            commands_menu(project_path, config)
        elif choice == "state":
            states_menu(project_path, config)
        elif choice == "config":
            project_config_menu(project_path, config)


# =============================================================================
# 对话管理
# =============================================================================

def conversations_menu(project_path: str, config: Dict):
    """对话管理菜单"""
    while True:
        # 含义：每次进入菜单都刷新对话列表
        convs = pm.list_conversations(project_path)
        
        # 含义：构建选择列表（显示对话轮数）
        choices = []
        for c in convs:
            # 显示格式：💬 对话名称 (X 轮对话，Y 条消息)
            display_text = f"💬 {c['name']} ({c['round_count']}轮，{c['message_count']}条)"
            choices.append(Choice(display_text, c['id']))
        
        choices.extend([
            Choice("➕ 新建对话", "new"),
            Choice("👁️  查看对话", "view"),
            Choice("🗑️  删除对话", "delete"),
            Choice("🔄 刷新列表", "refresh"),
            Choice("🔙 返回", "back")
        ])
        
        choice = questionary.select("对话管理", choices=choices).ask()
        
        if choice == "back" or choice is None:
            break
        elif choice == "new":
            name = questionary.text("对话名称（留空自动生成）").ask()
            conv_id = pm.create_conversation(project_path, name)
            print("✅ 新对话已创建")
            
            # 询问打开方式
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
            # 含义：查看对话内容
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
                    
                    # 修复：显示全部消息，不限制数量
                    for i, msg in enumerate(messages, 1):
                        role = msg.get("role", "unknown")
                        content = msg.get("content", "")
                        # 修复：显示完整内容，不截断
                        if role == "user":
                            print(f"[{i}] 👤 用户：{content}")
                        else:
                            # 修复：长内容分多行显示
                            print(f"[{i}] 🤖 AI:")
                            for line in content.split('\n'):
                                print(f"    {line}")
                        print()  # 空行分隔
                    
                    print(f"{'='*60}\n")
                else:
                    print("❌ 无法加载对话")
                    
        elif choice == "delete":
            if not convs:
                print("⚠️  暂无对话可删除")
                continue
            
            del_choices = [Choice(f"💬 {c['name']} ({c['round_count']}轮)", c['id']) for c in convs]
            sel = questionary.select("选择删除", choices=del_choices).ask()
            if sel and questionary.confirm("确定删除？").ask():
                pm.delete_conversation(project_path, sel)
                print("✅ 已删除")
                
        elif choice == "refresh":
            print("🔄 已刷新列表")
            continue
            
        elif choice:
            # 打开现有对话
            open_mode = questionary.select(
                "打开方式",
                choices=[
                    Choice("🪟 新窗口打开", "new_window"),
                    Choice("▶️  当前窗口打开", "current")
                ]
            ).ask()
            
            if open_mode == "new_window":
                run_project_in_new_window(project_path, config, choice)
            elif open_mode == "current":
                run_project(project_path, config, choice)


# =============================================================================
# 运行项目
# =============================================================================
def run_project(project_path: str, config: Dict, conv_id: str = None):
    """运行项目（支持对话历史和返回值管理）"""
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
        
        # 加载对话历史
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
                # 显示等待中的返回值
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
                
                # 查看历史
                if user.lower() == "history":
                    print(f"\n=== 当前对话历史 ({len(controller.conversation_history)} 条) ===")
                    for msg in controller.conversation_history[-10:]:
                        print(f"  {msg}")
                    print("=" * 50)
                    continue
                
                # 查看返回值状态
                if user.lower() == "returns":
                    # 含义：显示所有返回值历史（包括已通知的）
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
                                value = p['value']
                                if isinstance(value, dict):
                                    print(f"     返回值：{str(value)[:100]}...")
                                else:
                                    print(f"     返回值：{str(value)[:100]}...")
                            print("-" * 40)
                        print("=" * 50)
                    else:
                        print("暂无返回值记录")
                    continue
                
                # 提交返回值
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
                
                # 清理已完成的返回值
                if user.lower() == "clear":
                    controller.clear_completed_returns()
                    print("✅ 已清理已完成的返回值")
                    continue
                
                # 正常处理用户输入
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
    
    # 检测是否为打包环境
    is_packaged = getattr(sys, 'frozen', False)
    
    try:
        if sys.platform == "darwin":  # macOS
            if is_packaged:
                # 打包环境
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
                # 开发环境
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
            if USE_RICH and console:
                console.print("[green]✅ 已在新窗口中启动[/green]")
            else:
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
            if USE_RICH and console:
                console.print("[green]✅ 已在新窗口中启动[/green]")
            else:
                print("✅ 已在新窗口中启动")
            
        else:  # Linux
            if USE_RICH and console:
                console.print("[yellow]⚠️  Linux 请使用终端手动运行[/yellow]")
            else:
                print("⚠️  Linux 请使用终端手动运行")
            run_project(project_path, config, conv_id)
            
    except Exception as e:
        if USE_RICH and console:
            console.print(f"[red]❌ 打开新窗口失败：{e}[/red]")
        else:
            print(f"❌ 打开新窗口失败：{e}")
        run_project(project_path, config, conv_id)

# =============================================================================
# 命令管理
# =============================================================================

def commands_menu(project_path: str, config: Dict[str, Any]):
    """命令管理菜单（重新设计版）"""
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
            # =================================================================
            # 1. 基本信息
            # =================================================================
            cmd_id = questionary.text("命令 ID").ask()
            if not cmd_id:
                continue
            cmd_desc = questionary.text("命令描述").ask()

            # =============================================================
            # 2. 处理器类型（重新分类）
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
            
            # 根据类别显示具体处理器
            handler_type = None
            if processor_category == "reply":
                handler_type = questionary.select(
                    "选择处理器",
                    choices=[
                        Choice("📝 文本回复 (echo)", "echo")
                    ]
                ).ask()
            elif processor_category == "system":
                handler_type = questionary.select(
                    "选择处理器",
                    choices=[
                        Choice("🔄 状态跳转 (state_jump)", "state_jump")
                    ]
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
                    choices=[
                        Choice("📤 传出数据 (output)", "output")
                    ]
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
            # 3. 返回值设置
            # =============================================================
            has_return = questionary.confirm(
                "是否有返回值？",
                default=(processor_category in ["external", "output", "wait"])
            ).ask()
            
            return_type = None
            if has_return:
                if processor_category in ["external", "output"]:
                    # 外部请求和数据输出通常是自动返回值
                    return_type = "auto"
                elif processor_category == "wait":
                    # 等待类是手动返回值
                    return_type = "manual"
                else:
                    return_type = questionary.select(
                        "返回值类型",
                        choices=[
                            Choice("🔄 自动 (HTTP/命令输出等)", "auto"),
                            Choice("👤 手动 (用户输入/外部回调)", "manual")
                        ]
                    ).ask()
            
            wait_for_return = False
            if has_return:
                wait_for_return = questionary.confirm(
                    "是否需要等待返回值后再回复用户？",
                    default=False
                ).ask()
            
            # =============================================================
            # 4. 处理器配置
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
            # =================================================================
            # 编辑现有命令
            # =================================================================
            cmd = commands[choice]
            cmd_action = questionary.select(
                f"命令：{cmd['id']}",
                choices=[
                    Choice("✏️  编辑基本信息", "edit_basic"),
                    Choice("🔧 修改处理器", "edit_handler"),
                    Choice("⏱️  修改返回值设置", "edit_return"),
                    Choice("🗑️  删除命令", "delete"),
                    Choice("🔙 取消", "cancel")
                ]
            ).ask()

            if cmd_action == "edit_basic":
                # 含义：编辑基本信息
                cmd["description"] = questionary.text(
                    "描述", default=cmd.get("description", "")
                ).ask()
                
            elif cmd_action == "edit_handler":
                # 含义：重新选择处理器类别和类型
                current_category = cmd.get("processor_category", "none")
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
                    default=current_category
                ).ask()
                
                # 根据类别显示具体处理器
                handler_type = None
                if processor_category == "reply":
                    handler_type = questionary.select(
                        "选择处理器",
                        choices=[
                            Choice("📝 文本回复 (echo)", "echo")
                        ]
                    ).ask()
                elif processor_category == "system":
                    handler_type = questionary.select(
                        "选择处理器",
                        choices=[
                            Choice("🔄 状态跳转 (state_jump)", "state_jump")
                        ]
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
                        choices=[
                            Choice("📤 传出数据 (output)", "output")
                        ]
                    ).ask()
                elif processor_category == "wait":
                    handler_type = questionary.select(
                        "选择处理器",
                        choices=[
                            Choice("👤 等待用户输入 (wait_for_user)", "wait_for_user"),
                            Choice("🌐 等待外部回调 (wait_for_external)", "wait_for_external")
                        ]
                    ).ask()
                
                # 获取当前配置作为默认值
                current_config = cmd.get("handler", {}).get("config", {}) if cmd.get("handler") else {}
                handler_config = _build_handler_config(handler_type, current_config)
                
                cmd["processor_category"] = processor_category
                if handler_type and handler_type != "none":
                    cmd["handler"] = {"type": handler_type, "config": handler_config}
                else:
                    cmd["handler"] = None
                    
            elif cmd_action == "edit_return":
                # 含义：编辑返回值设置
                current = cmd.get("return_settings", {})
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
                config["commands"].pop(choice)
                print("✅ 命令已删除")


def _build_handler_config(handler_type: str, current_config: Dict = None) -> Dict:
    """
    构建处理器配置
    - handler_type: 处理器类型
    - current_config: 当前配置（用于编辑时保留默认值）
    """
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
        args_from = questionary.text(
            "参数来源（留空则无参数）",
            default=current_config.get("args_from", "")
        ).ask()
        if args_from:
            config["args_from"] = args_from

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
            "输出数据键名（用于外部识别）",
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
# 状态编排
# =============================================================================

def states_menu(project_path: str, config: Dict[str, Any]):
    """状态编排菜单"""
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
            state_id = questionary.text("状态 ID").ask()
            if not state_id:
                continue
            state_desc = questionary.text("状态描述").ask()
            state_mode = questionary.select(
                "模式",
                choices=[
                    Choice("稳定模式 (stable)", "stable"),
                    Choice("自由模式 (free)", "free")
                ]
            ).ask()
            parent_id = questionary.text("父状态 ID (留空为根)").ask() or None
            config["states"].append({
                "id": state_id,
                "description": state_desc,
                "mode": state_mode,
                "parent_id": parent_id,
                "available_commands": [],
                "command_transitions": {}
            })
            if USE_RICH and console:
                console.print("[green]✅ 状态已添加[/green]")
        elif isinstance(choice, int):
            state = states[choice]
            state_action = questionary.select(
                f"状态：{state['id']}",
                choices=[
                    Choice("✏️  编辑", "edit"),
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
            elif state_action == "commands":
                # 含义：获取所有可用命令
                all_cmds = config.get("commands", [])

                # 含义：如果没有任何命令，提示用户
                if not all_cmds:
                    if USE_RICH and console:
                        console.print("[yellow]⚠️  请先在命令管理中添加命令[/yellow]")
                    else:
                        print("⚠️  请先在命令管理中添加命令")
                    continue

                # 含义：获取当前状态已选的命令
                current = state.get("available_commands", [])
                if not isinstance(current, list):
                    current = []

                # 含义：构建 Choice 列表，使用 checked 属性标记已选项
                cmd_choices = []
                for c in all_cmds:
                    cmd_id = c["id"]
                    # 含义：如果该命令在当前已选列表中，标记为 checked=True
                    is_checked = cmd_id in current
                    cmd_choices.append(Choice(cmd_id, cmd_id, checked=is_checked))

                # 含义：显示多选框（不使用 default 参数）
                selected = questionary.checkbox(
                    "选择可用命令",
                    choices=cmd_choices
                    # 修复：不使用 default 参数，改用 Choice 的 checked 属性
                ).ask()

                if selected is not None:
                    state["available_commands"] = selected
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
                config["states"].pop(choice)

# =============================================================================
# 项目配置
# =============================================================================
def project_config_menu(project_path: str, config: Dict):
    """项目配置菜单"""
    while True:
        choice = questionary.select(
            "项目配置",
            choices=[
                Choice("🔑 API 配置", "api"),
                Choice("🔙 返回", "back")
            ]
        ).ask()
        
        if choice == "back":
            pm.save_project(project_path, config)
            break
        elif choice == "api":
            if "api" not in config:
                config["api"] = {}
            k = questionary.password("Key", default=config["api"].get("key", "")).ask()
            u = questionary.text("URL", default=config["api"].get("base_url", "")).ask()
            m = questionary.text("Model", default=config["api"].get("model", "")).ask()
            config["api"].update({"key": k, "base_url": u, "model": m})
            pm.save_project(project_path, config)
            if USE_RICH and console:
                console.print("[green]✅ 已保存[/green]")
            else:
                print("✅ 已保存")

# =============================================================================
# 系统设置
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
            # =============================================================
            # 【新增】超时时间设置
            # =============================================================
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
# 新窗口运行功能
# =============================================================================

# 子命令：单窗口运行（供新窗口调用）
# =============================================================================

@app.command("run-single")
def run_single_cmd(
    project_path: str = typer.Argument(..., help="项目路径"),
    conv_id: Optional[str] = typer.Option(None, "--conv", "-c", help="对话 ID")
):
    """单窗口运行项目（供新窗口调用）"""
    config = pm.open_project(project_path)
    run_project(project_path, config, conv_id)


# =============================================================================
# 入口点（修复打包问题）
# =============================================================================

def main_entry():
    """主入口函数（打包后调用）"""
    app()

if __name__ == "__main__":
    main_entry()
