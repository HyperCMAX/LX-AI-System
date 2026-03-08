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
    if selected:
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
        
        if choice == "conv":
            conversations_menu(project_path, config)
        elif choice == "cmd":
            commands_menu(project_path, config)
        elif choice == "state":
            states_menu(project_path, config)
        elif choice == "config":
            project_config_menu(project_path, config)
        elif choice == "back" or choice is None:
            break


# =============================================================================
# 对话管理
# =============================================================================

def conversations_menu(project_path: str, config: Dict):
    """对话管理菜单"""
    while True:
        convs = pm.list_conversations(project_path)
        choices = [Choice(f"💬 {c['name']} ({c['message_count']})", c['id']) for c in convs]
        choices.extend([
            Choice("➕ 新建对话", "new"),
            Choice("🗑️  删除对话", "delete"),
            Choice("🔙 返回", "back")
        ])
        
        choice = questionary.select("对话管理", choices=choices).ask()
        
        if choice == "back" or choice is None:
            break
        elif choice == "new":
            name = questionary.text("对话名称（留空自动生成）").ask()
            conv_id = pm.create_conversation(project_path, name)
            if USE_RICH and console:
                console.print("[green]✅ 新对话已创建[/green]")
            else:
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
                
        elif choice == "delete":
            if convs:
                del_choices = [Choice(f"💬 {c['name']}", c['id']) for c in convs]
                sel = questionary.select("选择删除", choices=del_choices).ask()
                if sel and questionary.confirm("确定？").ask():
                    pm.delete_conversation(project_path, sel)
                    if USE_RICH and console:
                        console.print("[green]✅ 已删除[/green]")
                    else:
                        print("✅ 已删除")
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
    """运行项目（支持对话历史）"""
    api = config.get("api", {})
    if not api.get("key"):
        g = pm.get_global_api_config()
        if g.get("key"):
            config["api"] = g
        else:
            if USE_RICH and console:
                console.print("[red]❌ 未配置 API[/red]")
            else:
                print("❌ 未配置 API")
            return
    
    pm.save_project(project_path, config)
    
    try:
        loader = ProjectLoader(project_path)
        controller = SystemController(initial_state_id=config.get("initial_state", "root"))
        
        if conv_id:
            data = pm.load_conversation(project_path, conv_id)
            controller.conversation_history = [f"{m['role']}: {m['content']}" for m in data.get("messages", [])]
            curr_id = conv_id
            conv_name = data.get("name", conv_id)
        else:
            curr_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            conv_name = f"对话 {curr_id}"
        
        info = loader.apply_to(controller)
        
        if USE_RICH and console:
            if Panel:
                console.print(Panel(f"[bold blue]{info['project_name']} - {conv_name}[/bold blue]"))
            else:
                console.print(f"[bold blue]{info['project_name']} - {conv_name}[/bold blue]")
            console.print(f"上下文长度：{pm.get_context_length()} 轮")
        else:
            print(f"\n=== {info['project_name']} - {conv_name} ===")
            print(f"上下文长度：{pm.get_context_length()} 轮\n")
        
        while True:
            try:
                user = typer.prompt("用户")
                if user.lower() in ["exit", "quit"]:
                    _save_conv(pm, project_path, curr_id, controller)
                    break
                
                fb = controller.process_user_input(user)
                ai = controller.get_last_response()
                
                if ai:
                    if USE_RICH and console:
                        console.print(f"[bold white]AI: {ai}[/bold white]")
                    else:
                        print(f"AI: {ai}")
                
            except KeyboardInterrupt:
                _save_conv(pm, project_path, curr_id, controller)
                break
            except Exception as e:
                if USE_RICH and console:
                    console.print(f"[red]❌ 错误：{e}[/red]")
                else:
                    print(f"❌ 错误：{e}")
    except Exception as e:
        if USE_RICH and console:
            console.print(f"[red]❌ 启动失败：{e}[/red]")
        else:
            print(f"❌ 启动失败：{e}")

def _save_conv(pm, path, conv_id, controller):
    """保存对话历史"""
    msgs = []
    for m in controller.conversation_history:
        if m.startswith("User:"):
            msgs.append({"role": "user", "content": m[5:]})
        elif m.startswith("Assistant:"):
            msgs.append({"role": "assistant", "content": m[12:]})
    pm.save_conversation(path, conv_id, msgs)


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
                        do script "{exe} run-single '{project_path}' '{conv_id}'"
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
                        do script "cd '{cli_path.parent}' && {sys.executable} '{cli_path}' run-single '{project_path}' '{conv_id}'"
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
                    cmd = f'start "LX_AI" "{sys.executable}" run-single "{project_path}" "{conv_id}"'
                else:
                    cmd = f'start "LX_AI" "{sys.executable}" run-single "{project_path}"'
            else:
                cli_path = Path(__file__).absolute()
                if conv_id:
                    cmd = f'start "LX_AI" "{sys.executable}" "{cli_path}" run-single "{project_path}" "{conv_id}"'
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
    """命令管理菜单"""
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
            # 添加新命令
            # =================================================================
            cmd_id = questionary.text("命令 ID").ask()
            if not cmd_id:
                continue
            cmd_desc = questionary.text("命令描述").ask()

            handler_type = questionary.select(
                "处理器类型",
                choices=[
                    Choice("📝 返回固定文本 (echo)", "echo"),
                    Choice("💻 执行系统命令 (run_command)", "run_command"),
                    Choice("🌐 HTTP 请求 (http_request)", "http_request"),
                    Choice("🔌 Python 插件 (plugin)", "plugin"),
                    Choice("⏭️  仅状态跳转 (state_jump)", "state_jump"),
                    Choice("📤 传出数据 (output)", "output"),
                    Choice("⚪ 无处理器", "none")
                ]
            ).ask()

            handler_config = _build_handler_config(handler_type)

            cmd_entry = {
                "id": cmd_id,
                "description": cmd_desc,
                "parameters_schema": {}
            }
            if handler_type != "none":
                cmd_entry["handler"] = handler_config

            config["commands"].append(cmd_entry)
            if USE_RICH and console:
                console.print("[green]✅ 命令已添加[/green]")
            else:
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
                    Choice("🔧 修改处理器配置", "edit_handler"),
                    Choice("🗑️  删除命令", "delete"),
                    Choice("🔙 取消", "cancel")
                ]
            ).ask()

            if cmd_action == "edit_basic":
                # 含义：编辑基本信息
                cmd["description"] = questionary.text(
                    "描述", default=cmd.get("description", "")
                ).ask()
                # 含义：编辑参数 schema
                params_str = questionary.text(
                    "参数定义 (JSON 格式，如 {\"query\": \"str\"})",
                    default=json.dumps(cmd.get("parameters_schema", {}))
                ).ask()
                try:
                    cmd["parameters_schema"] = json.loads(params_str) if params_str else {}
                except json.JSONDecodeError:
                    if USE_RICH and console:
                        console.print("[yellow]⚠️  JSON 格式错误，使用空参数[/yellow]")
                    else:
                        print("⚠️  JSON 格式错误，使用空参数")
                    cmd["parameters_schema"] = {}

            elif cmd_action == "edit_handler":
                # 含义：修改处理器配置
                current_type = cmd.get("handler", {}).get("type", "none")
                new_type = questionary.select(
                    "处理器类型",
                    choices=[
                        Choice("📝 返回固定文本 (echo)", "echo"),
                        Choice("💻 执行系统命令 (run_command)", "run_command"),
                        Choice("🌐 HTTP 请求 (http_request)", "http_request"),
                        Choice("🔌 Python 插件 (plugin)", "plugin"),
                        Choice("⏭️  仅状态跳转 (state_jump)", "state_jump"),
                        Choice("📤 传出数据 (output)", "output"),
                        Choice("⚪ 无处理器", "none"),
                        Choice(f"保持当前 ({current_type})", "keep")
                    ]
                ).ask()

                if new_type == "keep":
                    new_type = current_type

                if new_type != "none":
                    # 含义：获取当前配置作为默认值
                    current_config = cmd.get("handler", {}).get("config", {})
                    # 含义：构建新配置
                    handler_config = _build_handler_config(new_type, current_config)
                    cmd["handler"] = {"type": new_type, "config": handler_config}
                else:
                    # 含义：移除处理器
                    if "handler" in cmd:
                        del cmd["handler"]

            elif cmd_action == "delete":
                config["commands"].pop(choice)


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
        # =====================================================================
        # 修复：完整的传出数据配置
        # =====================================================================
        config["output_key"] = questionary.text(
            "输出数据键名（用于外部执行器识别）",
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

        # 含义：配置要传出的数据内容
        data_method = questionary.select(
            "数据来源",
            choices=[
                Choice("📝 固定数据", "fixed"),
                Choice("📥 从命令参数获取", "from_params"),
                Choice("🔗 混合模式", "mixed")
            ]
        ).ask()

        if data_method == "fixed":
            # 含义：固定数据
            fixed_data_str = questionary.text(
                "固定数据 (JSON 格式)",
                default=json.dumps(current_config.get("data", {}))
            ).ask()
            try:
                config["data"] = json.loads(fixed_data_str) if fixed_data_str else {}
            except json.JSONDecodeError:
                config["data"] = {}
        elif data_method == "from_params":
            # 含义：从参数获取
            param_names = questionary.text(
                "参数名列表 (逗号分隔，如：query,user_id)",
                default=",".join(current_config.get("data_params", []))
            ).ask()
            config["data_params"] = [p.strip() for p in param_names.split(",") if p.strip()]
        elif data_method == "mixed":
            # 含义：混合模式
            fixed_data_str = questionary.text(
                "固定数据 (JSON 格式)",
                default=json.dumps(current_config.get("data", {}))
            ).ask()
            try:
                config["data"] = json.loads(fixed_data_str) if fixed_data_str else {}
            except json.JSONDecodeError:
                config["data"] = {}
            param_names = questionary.text(
                "动态参数名列表 (逗号分隔)",
                default=",".join(current_config.get("data_params", []))
            ).ask()
            config["data_params"] = [p.strip() for p in param_names.split(",") if p.strip()]

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
            if USE_RICH and console:
                console.print("[green]✅ API 配置已保存[/green]")
            else:
                print("✅ API 配置已保存")
        elif choice == "context":
            current = pm.get_context_length()
            new = questionary.text("上下文长度 (1-50)", default=str(current)).ask()
            try:
                pm.set_context_length(max(1, min(50, int(new))))
                if USE_RICH and console:
                    console.print(f"[green]✅ 上下文长度已设置为 {new}[/green]")
                else:
                    print(f"✅ 上下文长度已设置为 {new}")
            except:
                if USE_RICH and console:
                    console.print("[red]❌ 请输入有效数字[/red]")
                else:
                    print("❌ 请输入有效数字")

# =============================================================================
# 新窗口运行功能
# =============================================================================

# 子命令：单窗口运行（供新窗口调用）
# =============================================================================

@app.command("run-single")
def run_single_cmd(project_path: str, conv_id: str = None):
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
