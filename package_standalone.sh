#!/bin/bash

# 打包独立的LX AI可执行文件

echo "开始打包独立的LX AI可执行文件..."

# 清理旧的构建文件
rm -rf build/ dist/ *.egg-info/

# 切换到src目录
cd src

# 使用cx_Freeze创建独立可执行文件
python3 setup.py build_exe --standalone

# 回到项目根目录
cd ..

# 检查构建是否成功
if [ -f "dist/LX_AI" ]; then
    echo "可执行文件已成功构建到 dist/ 目录"
    
    # 将可执行文件复制到src目录
    cp dist/LX_AI src/LX_AI_Standalone
    
    # 设置执行权限
    chmod +x src/LX_AI_Standalone
    
    echo "独立可执行文件已创建: src/LX_AI_Standalone"
    
    # 清理构建目录
    rm -rf build/ dist/ *.egg-info/
    
else
    echo "构建失败，正在回退..."
    rm -rf build/ dist/ *.egg-info/
fi