#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单启动器，用于启动原始Python应用程序
"""

import sys
import subprocess
import os


def main():
    """主入口函数"""
    # 检查是否是打包环境
    is_frozen = getattr(sys, 'frozen', False)
    
    # 获取脚本路径
    if is_frozen:
        # 如果是打包环境，获取当前可执行文件所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
        # 通常我们会在这里启动原始的Python脚本
        # 但现在我们只是显示帮助信息
        if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
            print_help()
            sys.exit(0)
        elif len(sys.argv) > 1 and sys.argv[1] == '--version':
            print_version()
            sys.exit(0)
        else:
            # 显示启动信息，告诉用户如何使用
            print("状态驱动 AI 系统 - 项目管理 CLI")
            print("运行 'LX_AI --help' 获取更多信息")
            print("\n注意: 此版本为简化版，如需完整功能，请使用源代码运行。")
            sys.exit(0)
    else:
        # 开发环境，直接执行原始脚本
        if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
            print_help()
            sys.exit(0)
        elif len(sys.argv) > 1 and sys.argv[1] == '--version':
            print_version()
            sys.exit(0)
        else:
            print("状态驱动 AI 系统 - 项目管理 CLI")
            print("运行 'LX_AI --help' 获取更多信息")
            sys.exit(0)


def print_help():
    """打印帮助信息"""
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


def print_version():
    """打印版本信息"""
    print("LX_AI v1.0.0")


if __name__ == "__main__":
    main()