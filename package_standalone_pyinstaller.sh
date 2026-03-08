#!/bin/bash

# 使用PyInstaller打包独立的LX AI可执行文件

echo "开始使用PyInstaller打包独立的LX AI可执行文件..."

# 检查是否安装了PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller未安装，正在安装..."
    pip install pyinstaller
fi

# 清理旧的构建文件
rm -rf build/ dist/ *.spec

# 切换到src目录
cd src

# 使用PyInstaller创建独立可执行文件
pyinstaller --onefile --name LX_AI_Standalone cli.py

# 检查构建是否成功
if [ -f "dist/LX_AI_Standalone" ]; then
    echo "独立可执行文件已成功构建到 src/dist/ 目录"
    
    # 将可执行文件复制到src目录根部
    cp dist/LX_AI_Standalone .
    
    # 设置执行权限
    chmod +x LX_AI_Standalone
    
    echo "独立可执行文件已创建: src/LX_AI_Standalone"
    
    # 清理PyInstaller构建目录
    cd ..
    rm -rf build/ dist/ *.spec src/LX_AI_Standalone.spec
    
else
    echo "构建失败，正在回退..."
    cd ..
    rm -rf build/ dist/ *.spec
fi