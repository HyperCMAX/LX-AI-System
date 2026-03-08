# setup.py

import os
import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_options = {
    'packages': [],
    'excludes': [],
    'include_files': []  # 添加任何需要包含的非Python文件
}

executables = [
    Executable(
        'src/cli.py',  # 主入口脚本
        target_name='LX_AI',  # 输出的可执行文件名
        base=None  # 使用None以支持控制台和非控制台应用
    )
]

setup(
    name='LX_AI',
    version='1.0.0',
    description='Large Language Model Application Framework',
    options={'build_exe': build_options},
    executables=executables
)

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

# =============================================================================
# 构建配置
# =============================================================================

# 更全面地包含额外的包和模块
build_exe_options = {
    "packages": [
        "questionary", 
        "typer", 
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
    "optimize": 2,
    "include_msvcrt": True,
    "silent": True
}

# =============================================================================
# 应用配置
# =============================================================================

# 为不同操作系统设置适当的base
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
    executables=executables,
    distclass=None,
    script_name=None,
    script_args=None,
    cmdclass=None,
    ext_modules=None,
    classifiers=None,
    download_url=None,
    data_files=None,
    project_urls=None,
    provides=None,
    obsoletes=None,
    package_dir=None,
    packages=None,
    py_modules=None,
    url=None,
    license=None,
    long_description=None,
    author=None,
    author_email=None,
    maintainer=None,
    maintainer_email=None,
    keywords=None,
    platforms=None,
    requires=None,
    command_packages=None,
    fullname=None,
    dist_dir="dist/LX_AI_Standalone"
)