# src/cli.py

# 导入 typer 用于构建 CLI
import typer
# 导入 questionary 用于交互式菜单
import questionary
from questionary import Choice
# 导入核心控制器
from core.controller import SystemController
# 导入项目管理器
from core.project_manager import ProjectManager
# 导入项目加载器
from core.project_loader import ProjectLoader
# 导入 Path 用于文件操作
from pathlib import Path
# 导入 typing 用于类型提示
from typing import Dict, Any, Optional, List
# 导入 json 用于配置
import json
# 导入 yaml 用于配置
import yaml

# 含义：导入富文本库
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel

    USE_RICH = True
    console = Console()
except ImportError:
    USE_RICH = False
    console = None
    Table = None
    Panel = None

# 含义：创建 Typer 应用实例
app = typer.Typer(help="状态驱动 AI 系统 - 项目管理 CLI")

# =============================================================================
# 【新增】设置默认回调（无子命令时自动执行 main）
# =============================================================================
@app.callback(invoke_without_command=True)
def default_callback(ctx: typer.Context):
    """默认执行主菜单"""
    if ctx.invoked_subcommand is None:
        main()

# 含义：创建项目管理器实例
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
# 项目菜单
# =============================================================================

def open_project_menu():
    """打开项目选择菜单"""
    # 含义：选择打开方式
    open_method = questionary.select(
        "打开项目方式",
        choices=[
            Choice("📂 从列表选择", "list"),
            Choice("📝 手动输入路径", "manual"),
            Choice("🔙 返回", "back")
        ]
    ).ask()

    if open_method == "back" or open_method is None:
        return
    elif open_method == "list":
        # 含义：从列表选择
        projects = pm.list_projects()
        if not projects:
            if USE_RICH and console:
                console.print("[yellow]⚠️  暂无项目，请先新建项目[/yellow]")
            else:
                print("⚠️  暂无项目，请先新建项目")
            return

        choices = []
        for p in projects:
            choices.append(Choice(f"📂 {p['name']} ({p['version']})", p['path']))
        choices.append(Choice("🔙 返回", None))

        selected = questionary.select("选择项目", choices=choices).ask()
        if selected:
            project_menu(selected)
    elif open_method == "manual":
        # 含义：手动输入路径
        path = questionary.text("输入项目路径或 project.yaml 文件路径").ask()
        if path:
            try:
                test_path = Path(path)
                if test_path.is_dir():
                    config_file = test_path / "project.yaml"
                    if not config_file.exists():
                        raise FileNotFoundError("项目目录中未找到 project.yaml")
                elif test_path.is_file() and test_path.name == "project.yaml":
                    pass
                else:
                    raise FileNotFoundError("无效的项目路径")
                project_menu(str(test_path))
            except Exception as e:
                if USE_RICH and console:
                    console.print(f"[red]❌ 打开失败：{str(e)}[/red]")
                else:
                    print(f"❌ 打开失败：{str(e)}")


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
    project_name = config.get("project", {}).get("name", "Unknown")

    while True:
        choice = questionary.select(
            f"=== 项目：{project_name} ===",
            choices=[
                Choice("▶️  当前窗口运行", "run_current"),
                Choice("🪟 新窗口运行", "run_new_window"),
                Choice("📝 命令管理", "commands"),
                Choice("🗂️  状态编排", "states"),
                Choice("⚙️  项目配置", "config"),
                Choice("🔙 返回主菜单", "back")
            ]
        ).ask()

        if choice == "run_current":
            run_project(project_path, config)
        elif choice == "run_new_window":
            run_project_in_new_window(project_path, config)
        elif choice == "commands":
            commands_menu(project_path, config)
        elif choice == "states":
            states_menu(project_path, config)
        elif choice == "config":
            project_config_menu(project_path, config)
        elif choice == "back" or choice is None:
            break


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

def project_config_menu(project_path: str, config: Dict[str, Any]):
    """项目配置菜单"""
    while True:
        choice = questionary.select(
            "项目配置",
            choices=[
                Choice("🔑 完整 API 配置", "api_full"),
                Choice("🏷️  项目信息", "info"),
                Choice("🔙 返回", "back")
            ]
        ).ask()

        if choice == "back" or choice is None:
            pm.save_project(project_path, config)
            break
        elif choice == "api_full":
            # =================================================================
            # 项目级 API 配置（保存在项目文件夹内的 config.json）✅
            # =================================================================
            if "api" not in config:
                config["api"] = {}

            current_key = config["api"].get("key", "")
            api_key = questionary.password(
                "API Key",
                default=current_key if current_key else ""
            ).ask()
            if api_key:
                config["api"]["key"] = api_key

            current_url = config["api"].get("base_url", "")
            base_url = questionary.text(
                "API Base URL",
                default=current_url if current_url else "https://api.openai.com/v1"
            ).ask()
            config["api"]["base_url"] = base_url

            current_model = config["api"].get("model", "")
            model = questionary.text(
                "模型名称",
                default=current_model if current_model else "gpt-3.5-turbo"
            ).ask()
            config["api"]["model"] = model

            # 含义：保存到项目文件夹内的 config.json
            pm.save_project(project_path, config)

            if USE_RICH and console:
                console.print("[green]✅ API 配置已保存到项目文件夹[/green]")
                console.print(f"   路径：{project_path}/config.json")
            else:
                print("✅ API 配置已保存到项目文件夹")
                print(f"   路径：{project_path}/config.json")

        elif choice == "info":
            config["project"]["name"] = questionary.text(
                "项目名称", default=config.get("project", {}).get("name", "")
            ).ask()
            config["project"]["version"] = questionary.text(
                "版本号", default=config.get("project", {}).get("version", "")
            ).ask()
            pm.save_project(project_path, config)
            if USE_RICH and console:
                console.print("[green]✅ 项目信息已保存[/green]")

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
                Choice("📂 项目目录设置", "dir"),
                Choice("📄 查看配置文件", "view_config"),
                Choice("🔙 返回主菜单", "back")
            ]
        ).ask()

        if choice == "back" or choice is None:
            break
        elif choice == "api":
            # 获取当前配置
            current_api = pm.get_global_api_config()

            api_key = questionary.password(
                "API Key",
                default=current_api.get("key", "")
            ).ask()

            base_url = questionary.text(
                "API Base URL",
                default=current_api.get("base_url", "https://api.openai.com/v1")
            ).ask()

            model = questionary.text(
                "模型名称",
                default=current_api.get("model", "gpt-3.5-turbo")
            ).ask()

            if api_key or base_url or model:
                pm.set_global_api_config(
                    api_key if api_key else current_api.get("key", ""),
                    base_url,
                    model
                )
                if USE_RICH and console:
                    console.print("[green]✅ API 配置已保存到 api_config.json[/green]")
                else:
                    print("✅ API 配置已保存到 api_config.json")

        elif choice == "dir":
            new_path = questionary.text("项目根目录路径").ask()
            if new_path:
                pm.projects_root = Path(new_path)
                if USE_RICH and console:
                    console.print(f"[green]✅ 项目目录已设置为：{new_path}[/green]")
                else:
                    print(f"✅ 项目目录已设置为：{new_path}")


        elif choice == "view_config":

            # 显示配置文件路径

            if USE_RICH and console:

                console.print("\n[bold]配置文件位置：[/bold]")

                console.print(f"  全局 API 配置：[cyan]{pm.api_config_path}[/cyan]")

                console.print(f"  全局配置：[cyan]{pm.global_config_path}[/cyan]")

                console.print(f"  配置目录：[cyan]{pm.get_config_dir()}[/cyan]")

                console.print(f"  项目目录：[cyan]{pm.projects_root}[/cyan]")

            else:

                print("\n配置文件位置：")

                print(f"  全局 API 配置：{pm.api_config_path}")

                print(f"  全局配置：{pm.global_config_path}")

                print(f"  配置目录：{pm.get_config_dir()}")

                print(f"  项目目录：{pm.projects_root}")

# =============================================================================
# 新窗口运行功能
# =============================================================================

def run_project_in_new_window(project_path: str, config: Dict[str, Any]):
    """在新终端窗口中运行项目"""
    import subprocess
    import sys
    import os

    # 含义：获取项目信息
    project_name = config.get("project", {}).get("name", "Unknown")

    # 含义：构建运行命令
    cli_path = Path(__file__).absolute()
    run_command = [
        sys.executable,
        str(cli_path),
        "run-single",  # 使用新的子命令
        project_path
    ]

    # 含义：根据操作系统打开新窗口
    try:
        if sys.platform == "darwin":  # macOS
            # 含义：macOS 使用 osascript 打开新 Terminal 窗口
            script = f'''
            tell application "Terminal"
                activate
                do script "cd '{cli_path.parent}' && {' '.join(run_command)}"
            end tell
            '''
            subprocess.run(["osascript", "-e", script])
            if USE_RICH and console:
                console.print("[green]✅ 已在新 Terminal 窗口中启动[/green]")
            else:
                print("✅ 已在新 Terminal 窗口中启动")

        elif sys.platform == "win32":  # Windows
            # 含义：Windows 使用 start 命令
            subprocess.Popen(
                f'start "LX Project - {project_name}" {" ".join(run_command)}',
                shell=True
            )
            if USE_RICH and console:
                console.print("[green]✅ 已在新命令提示符窗口中启动[/green]")
            else:
                print("✅ 已在新命令提示符窗口中启动")

        else:  # Linux 等其他系统
            # 含义：尝试使用 gnome-terminal 或 xterm
            terminal_commands = [
                ["gnome-terminal", "--", *run_command],
                ["xterm", "-e", *run_command],
                ["konsole", "-e", *run_command]
            ]
            launched = False
            for cmd in terminal_commands:
                try:
                    subprocess.Popen(cmd)
                    launched = True
                    break
                except FileNotFoundError:
                    continue
            if launched:
                if USE_RICH and console:
                    console.print("[green]✅ 已在新终端窗口中启动[/green]")
                else:
                    print("✅ 已在新终端窗口中启动")
            else:
                if USE_RICH and console:
                    console.print("[yellow]⚠️  无法找到可用终端，将在当前窗口运行[/yellow]")
                else:
                    print("⚠️  无法找到可用终端，将在当前窗口运行")
                run_project(project_path, config)
                return

    except Exception as e:
        if USE_RICH and console:
            console.print(f"[red]❌ 打开新窗口失败：{str(e)}[/red]")
        else:
            print(f"❌ 打开新窗口失败：{str(e)}")
        # 含义：降级为当前窗口运行
        run_project(project_path, config)
# =============================================================================
# 运行项目
# =============================================================================

def run_project(project_path: str, config: Dict[str, Any]):
    """运行项目"""
    api_config = config.get("api", {})
    if not api_config.get("key"):
        global_api = pm.get_global_api_config()
        if global_api.get("key"):
            config["api"] = global_api
        else:
            if USE_RICH and console:
                console.print("[red]❌ 未配置 API，请先在项目配置或系统设置中配置[/red]")
            else:
                print("❌ 未配置 API，请先在项目配置或系统设置中配置")
            return

    pm.save_project(project_path, config)

    try:
        loader = ProjectLoader(project_path)
        controller = SystemController(initial_state_id=config.get("initial_state", "root"))
        project_info = loader.apply_to(controller)

        if USE_RICH and console:
            if Panel:
                console.print(Panel(f"[bold blue]{project_info['project_name']} 已启动[/bold blue]"))
            else:
                console.print(f"[bold blue]{project_info['project_name']} 已启动[/bold blue]")
            console.print(f"初始状态：{project_info['initial_state']}")
        else:
            print(f"=== {project_info['project_name']} 已启动 ===")

        while True:
            try:
                user_input = typer.prompt("用户")
                if user_input.lower() in ["exit", "quit"]:
                    break
                feedback = controller.process_user_input(user_input)
                ai_response = controller.get_last_response()
                output_data = controller.get_last_output()

                if output_data:
                    if USE_RICH and console:
                        console.print(f"[yellow]📤 输出数据：{output_data}[/yellow]")
                    else:
                        print(f"📤 输出数据：{output_data}")

                if ai_response:
                    if USE_RICH and console:
                        console.print(f"[bold white]AI: {ai_response}[/bold white]")
                    else:
                        print(f"AI: {ai_response}")
                if USE_RICH and console:
                    if feedback.event_history:
                        evt = feedback.event_history[-1]
                        if "error" in evt.event_type.value:
                            console.print(f"[dim red]⚠️  {evt.message}[/dim red]")
            except KeyboardInterrupt:
                break
            except Exception as e:
                if USE_RICH and console:
                    console.print(f"[red]❌ 错误：{str(e)}[/red]")
                else:
                    print(f"❌ 错误：{str(e)}")
    except Exception as e:
        if USE_RICH and console:
            console.print(f"[red]❌ 启动失败：{str(e)}[/red]")
        else:
            print(f"❌ 启动失败：{str(e)}")


# =============================================================================
# 单窗口运行子命令（供新窗口调用）
# =============================================================================

@app.command("run-single")
def run_single(project_path: str):
    """单窗口运行项目（供新窗口调用）"""
    # 含义：加载项目配置
    config = pm.open_project(project_path)
    # 含义：直接运行，不返回主菜单
    run_project(project_path, config)


# =============================================================================
# 入口点
# =============================================================================

if __name__ == "__main__":
    app()