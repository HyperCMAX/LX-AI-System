#!/bin/bash

# 构建Windows安装包（通过Wine或交叉编译）

echo "准备构建Windows安装包..."

# 检查是否安装了PyInstaller（Windows打包工具）
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller未安装，建议手动安装或使用pip install pyinstaller"
    echo "或者考虑使用cx_Freeze创建Windows安装程序"
    exit 1
fi

echo "创建Windows安装包目录结构..."

# 创建构建目录
mkdir -p win_installer_temp/{output,build}

# 复制源代码到临时目录
cp -r src win_installer_temp/build/src
cp setup.py win_installer_temp/build/
cp requirements.txt win_installer_temp/build/

# 生成Windows安装脚本
cat > win_installer_temp/windows_setup.py << 'EOF'
# Windows安装脚本
import sys
import os
from cx_Freeze import setup, Executable

# 构建配置
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
    "compressed": True,
    "include_msvcrt": True,
    "silent": True
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Windows上隐藏控制台窗口

executables = [
    Executable(
        "src/cli.py", 
        base=base, 
        target_name="LX_AI.exe",
        icon=None
    )
]

setup(
    name="LX_AI",
    version="1.0",
    description="LX AI System - State-driven AI Interaction Framework",
    options={"build_exe": build_exe_options},
    executables=executables
)
EOF

cat > win_installer_temp/create_installer.bat << 'EOF'
@echo off
echo Creating Windows installer...

REM 安装依赖
pip install cx_Freeze

REM 创建可执行文件
python windows_setup.py build

REM 检查是否构建成功
if exist "build\exe.*" (
    echo Build successful!
    xcopy /E /I build\exe.* ..\output\LX_AI_Windows
    echo Windows executable ready in output folder
) else (
    echo Build failed
    exit /b 1
)

echo Windows installer creation completed!
pause
EOF

cat > win_installer_temp/create_installer_with_pyinstaller.bat << 'EOF'
@echo off
echo Creating Windows installer with PyInstaller...

REM 安装依赖
pip install pyinstaller

REM 创建单文件可执行文件
pyinstaller --onefile --windowed --name "LX_AI" src\cli.py

REM 检查是否构建成功
if exist "dist\LX_AI.exe" (
    echo Build successful!
    copy dist\LX_AI.exe ..\output\
    echo Windows executable ready in output folder
) else (
    echo Build failed
    exit /b 1
)

echo Windows installer creation completed!
pause
EOF

echo "Windows安装包构建脚本已创建在 win_installer_temp/ 目录中"
echo "请在Windows环境中运行这些脚本，或使用Wine模拟器:"
echo "1. cd win_installer_temp"
echo "2. wine create_installer.bat (如果使用Wine)"
echo "或直接在Windows上运行 create_installer.bat"