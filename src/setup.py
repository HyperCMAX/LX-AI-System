# src/setup.py

from cx_Freeze import setup, Executable
import sys
import os

# =============================================================================
# 构建配置
# =============================================================================

# 含义：包含的模块
build_exe_options = {
    "packages": [
        "questionary",
        "rich",
        "typer",
        "yaml",
        "pydantic",
        "requests",
        "json",
        "pathlib",
        "datetime",
    ],
    "includes": [
        "core",
        "core.config",
        "core.models",
        "core.registry",
        "core.state_machine",
        "core.message_protocol",
        "core.prompt_templates",
        "core.parser",
        "core.executor",
        "core.logger",
        "core.controller",
        "core.config_manager",
        "core.project_manager",
        "core.project_loader",
        "core.command_handlers",
    ],
    "include_files": [
        ("core", "core"),
    ],
    "excludes": [
        "tkinter",
        "unittest",
        "email",
        "http",
        "xml",
        "pydoc",
    ],
    "optimize": 2,
}

# =============================================================================
# 应用配置
# =============================================================================

executables = [
    Executable(
        "cli.py",
        target_name="LX_AI",
        base="console",  # macOS 使用 console，不要用 Win32GUI
        icon=None,
    )
]

# =============================================================================
# 打包配置
# =============================================================================

setup(
    name="LX_AI_System",
    version="1.0",
    description="状态驱动 AI 系统",
    options={"build_exe": build_exe_options},
    executables=executables,
)