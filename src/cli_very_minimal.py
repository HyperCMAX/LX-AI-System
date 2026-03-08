#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
极简的CLI入口，仅处理命令行参数而不导入任何复杂模块
"""

import sys
import os


def show_help():
    """显示帮助信息"""
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


def show_version():
    """显示版本信息"""
    print("LX_AI v1.0.0")


def main():
    """主入口函数"""
    # 检查是否是打包环境
    is_frozen = getattr(sys, 'frozen', False)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            show_help()
            sys.exit(0)
        elif sys.argv[1] == '--version':
            show_version()
            sys.exit(0)
        elif sys.argv[1] in ['main', 'run-single']:
            # 如果是有效命令，这时才导入所有依赖
            # 这样可以避免在--help时执行初始化
            try:
                # 尝试导入必要的模块
                import typer
                import questionary
                
                # 现在导入我们的模块
                from core.controller import SystemController
                from core.project_manager import ProjectManager
                from core.project_loader import ProjectLoader
                
                # 执行命令
                if sys.argv[1] == 'main':
                    pm = ProjectManager()
                    pm.print_startup_info()  # 打印启动信息
                    
                    while True:
                        choice = questionary.select(
                            "=== 状态驱动 AI 系统 ===",
                            choices=[
                                questionary.Choice("📁 打开项目", "open"),
                                questionary.Choice("➕ 新建项目", "create"),
                                questionary.Choice("⚙️  系统设置", "settings"),
                                questionary.Choice("❌ 退出", "exit")
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
                elif sys.argv[1] == 'run-single':
                    if len(sys.argv) < 3:
                        print("错误: run-single 命令需要项目路径参数")
                        sys.exit(1)
                    
                    project_path = sys.argv[2]
                    controller = SystemController(project_path)
                    controller.run()
            except ImportError as e:
                print(f"错误: 缺少必要的依赖: {e}")
                print("请确保安装了所有依赖项")
                sys.exit(1)
            except Exception as e:
                print(f"执行命令时出错: {e}")
                sys.exit(1)
        else:
            print(f"错误: 未知命令 '{sys.argv[1]}'")
            show_help()
            sys.exit(1)
    else:
        # 没有参数时，显示简短帮助
        if is_frozen:
            print("状态驱动 AI 系统 - 项目管理 CLI")
            print("运行 'LX_AI --help' 获取更多信息")
        else:
            show_help()


def open_project_menu(pm):
    """打开项目选择菜单"""
    import questionary
    
    # 含义：选择打开方式
    open_method = questionary.select(
        "打开项目方式",
        choices=[
            questionary.Choice("📂 从列表选择", "list"),
            questionary.Choice("📝 手动输入路径", "manual"),
            questionary.Choice("🔙 返回", "back")
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

        project_choices = [questionary.Choice(p["name"], p["path"]) for p in projects]
        project_choices.append(questionary.Choice("🔙 返回", "back"))
        selected_path = questionary.select("选择项目", choices=project_choices).ask()

        if selected_path and selected_path != "back":
            load_and_run_project(selected_path, pm)
    elif open_method == "manual":
        path = questionary.path("输入项目路径").ask()
        if path:
            load_and_run_project(path, pm)


def create_project_menu(pm):
    """创建新项目菜单"""
    import questionary
    
    name = questionary.text("项目名称").ask()
    if name:
        save_path = questionary.path("保存路径（留空使用默认）", default=str(pm.projects_root)).ask()
        try:
            path = pm.create_project(name, save_path)
            print(f"项目已创建：{path}")
            
            # 直接加载新创建的项目
            load_and_run_project(path, pm)
        except Exception as e:
            print(f"创建项目失败：{e}")


def settings_menu(pm):
    """系统设置菜单"""
    import questionary
    
    choice = questionary.select(
        "系统设置",
        choices=[
            questionary.Choice("📁 查看项目目录", "show_path"),
            questionary.Choice("⚙️  配置 API", "config_api"),
            questionary.Choice("🔙 返回", "back")
        ]
    ).ask()

    if choice == "show_path":
        print(f"项目目录：{pm.projects_root}")
        input("按回车继续...")
    elif choice == "config_api":
        configure_api(pm)
    elif choice == "back":
        return


def load_and_run_project(project_path, pm):
    """加载并运行项目"""
    from core.project_loader import ProjectLoader
    
    try:
        loader = ProjectLoader(project_path)
        project = loader.load()
        
        # 启动项目专用的命令循环
        from core.controller import SystemController
        controller = SystemController(project_path)
        controller.run()
    except Exception as e:
        print(f"加载项目失败：{e}")
        input("按回车返回...")


def configure_api(pm):
    """配置API（简化实现）"""
    print("API配置功能待实现")
    input("按回车返回...")


if __name__ == "__main__":
    main()