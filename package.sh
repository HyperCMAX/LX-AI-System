#!/bin/bash

# package.sh
# 用途：打包项目为独立可执行文件

set -e  # 遇到错误时停止执行

echo "📦 开始打包项目..."

# 1. 清理敏感数据
echo "🧹 清理敏感数据..."
python3 cleanup_for_package.py

# 2. 清理旧的构建文件
echo "🗑️ 清理旧构建文件..."
rm -rf build/ dist/ *.egg-info/ publish/

# 3. 构建可执行文件
echo "🔨 构建可执行文件..."
python3 setup.py build

# 4. 将整个构建目录复制到publish目录
echo "📁 复制构建目录到publish目录..."
mkdir -p publish
cp -r build/exe.*/* publish/

# 5. 将publish目录内容移动到src目录并重命名
echo "📁 移动到src目录..."
mv publish/* src/

# 6. 清理构建目录
echo "🧹 清理构建文件..."
rm -rf build/ dist/

echo "✅ 打包完成！"
echo ""
echo "📁 输出文件结构："
ls -la src/
echo ""
echo "💡 现在您可以分发 src/ 目录中的文件，它们是一个独立的应用程序"