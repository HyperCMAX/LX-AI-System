# setup.py

from cx_Freeze import setup, Executable
import sys

# =============================================================================
# 构建配置
# =============================================================================

# 更全面地包含额外的包和模块
build_exe_options = {
    "packages": [
        "questionary", 
        "typer", 
        "core", 
        "pathlib", 
        "typing", 
        "json", 
        "yaml", 
        "xml", 
        "xml.dom.minidom",
        "prompt_toolkit",
        "prompt_toolkit.shortcuts",
        "prompt_toolkit.styles",
        "prompt_toolkit.application",
        "prompt_toolkit.buffer",
        "prompt_toolkit.completion",
        "prompt_toolkit.filters",
        "prompt_toolkit.formatted_text",
        "prompt_toolkit.key_binding",
        "prompt_toolkit.layout",
        "prompt_toolkit.widgets",
        "prompt_toolkit.output",
        "prompt_toolkit.input",
        "rich.console", 
        "rich.table", 
        "rich.panel",
        "rich.text",
        "rich.cells",
        "rich.segment",
        "rich.padding",
        "rich.align",
        "rich.measure",
        "subprocess",
        "sys",
        "os",
        "requests",
        "certifi",
        "urllib3"
    ],
    "excludes": [],
    "include_files": [],
    "optimize": 2
}

# =============================================================================
# 应用配置
# =============================================================================

# 为 macOS 设置控制台应用程序
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Windows上隐藏控制台窗口

executables = [
    Executable(
        "src/cli.py", 
        base=base, 
        target_name="LX_AI",
        icon=None
    )
]

# =============================================================================
# 打包配置
# =============================================================================

setup(
    name="LX_AI",
    version="1.0",
    description="状态驱动 AI 系统 - 项目管理 CLI",
    options={"build_exe": build_exe_options},
    executables=executables
)