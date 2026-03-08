# src/cli_optimized.py

# 导入 typer 用于构建 CLI
import typer
# 导入 questionary 用于交互式菜单
import questionary
from questionary import Choice
# 导入 Path 用于文件操作
from pathlib import Path
# 导入 typing 用于类型提示
from typing import Dict, Any, Optional, List
# 导入 json 用于配置
import json
# 导入 yaml 用于配置
import yaml
import sys
import os

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

# 延迟初始化项目管理器
def get_project_manager():
    # 导入核心控制器
    from core.controller import SystemController
    # 导入项目管理器
    from core.project_manager import ProjectManager
    # 导入项目加载器
    from core.project_loader import ProjectLoader
    
    return ProjectManager()


# =============================================================================
# 主菜单
# =============================================================================

@app.command()
def main():
    """启动主菜单界面"""
    # 延迟初始化
    pm = get_project_manager()
    
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
            open_project_menu(pm)
        elif choice == "create":
            create_project_menu(pm)
        elif choice == "settings":
            settings_menu(pm)
        elif choice == "exit" or choice is None:
            break


# =============================================================================
# 项目菜单
# =============================================================================

def open_project_menu(pm):
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
            print("没有找到项目")
            return

        project_choices = [Choice(p["name"], p["path"]) for p in projects]
        project_choices.append(Choice("🔙 返回", "back"))
        selected_path = questionary.select("选择项目", choices=project_choices).ask()

        if selected_path and selected_path != "back":
            load_and_run_project(selected_path)
    elif open_method == "manual":
        path = questionary.path("输入项目路径").ask()
        if path:
            load_and_run_project(path)


def create_project_menu(pm):
    """创建新项目菜单"""
    name = questionary.text("项目名称").ask()
    if name:
        save_path = questionary.path("保存路径（留空使用默认）", default=str(pm.projects_root)).ask()
        try:
            path = pm.create_project(name, save_path)
            print(f"项目已创建：{path}")
            
            # 直接加载新创建的项目
            load_and_run_project(path)
        except Exception as e:
            print(f"创建项目失败：{e}")


def settings_menu(pm):
    """系统设置菜单"""
    choice = questionary.select(
        "系统设置",
        choices=[
            Choice("📁 查看项目目录", "show_path"),
            Choice("⚙️  配置 API", "config_api"),
            Choice("🔙 返回", "back")
        ]
    ).ask()

    if choice == "show_path":
        print(f"项目目录：{pm.projects_root}")
        input("按回车继续...")
    elif choice == "config_api":
        configure_api(pm)
    elif choice == "back":
        return


def load_and_run_project(project_path):
    """加载并运行项目"""
    from core.project_loader import ProjectLoader
    
    try:
        loader = ProjectLoader(project_path)
        project = loader.load()
        
        # 启动项目专用的命令循环
        run_single_project(project_path)
    except Exception as e:
        print(f"加载项目失败：{e}")
        input("按回车返回...")


@app.command()
def run_single(
    project_path: str = typer.Argument(..., help="项目路径")
):
    """单窗口运行项目（供新窗口调用）"""
    from core.controller import SystemController
    
    controller = SystemController(project_path)
    controller.run()


# =============================================================================
# 入口点
# =============================================================================

if __name__ == "__main__":
    # 仅当直接运行此脚本时才启动应用
    # 检查是否是打包环境且带有 --help 参数
    if getattr(sys, 'frozen', False) and len(sys.argv) > 1 and sys.argv[1] == "--help":
        # 在打包环境中，快速输出帮助而不进行初始化
        print("状态驱动 AI 系统 - 项目管理 CLI")
        print("")
        print("Usage: LX_AI [OPTIONS] COMMAND [ARGS]...")
        print("")
        print("Options:")
        print("  --install-completion  Install completion for the current shell.")
        print("  --show-completion     Show completion for the current shell, to copy it or customize the installation.")
        print("  --help                Show this message and exit.")
        print("")
        print("Commands:")
        print("  main        启动主菜单界面")
        print("  run-single  单窗口运行项目（供新窗口调用）")
        sys.exit(0)
    
    app()