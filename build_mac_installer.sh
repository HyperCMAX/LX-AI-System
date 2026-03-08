#!/bin/bash

# 构建Mac安装包

set -e  # 遇到错误时停止执行

echo "开始构建Mac安装包..."

# 清理旧的构建文件
rm -rf build/ dist/ *.egg-info/ app/ LX_AI_Mac_Installer.pkg

# 使用cx_Freeze构建应用程序
python3 setup.py build

# 检查构建是否成功
if [ -d "build" ]; then
    echo "构建成功，正在准备应用包..."
    
    # 创建.app结构
    mkdir -p app/LX_AI.app/Contents/MacOS
    mkdir -p app/LX_AI.app/Contents/Resources
    
    # 复制可执行文件
    cp -r build/* app/LX_AI.app/Contents/MacOS/
    
    # 创建Info.plist
    cat > app/LX_AI.app/Contents/Info.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>LX_AI</string>
    <key>CFBundleIconFile</key>
    <string>app.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.arxav.lxai</string>
    <key>CFBundleName</key>
    <string>LX AI</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF
    
    echo "创建DMG镜像..."
    
    # 安装create-dmg如果尚未安装
    if ! command -v create-dmg &> /dev/null; then
        echo "正在安装create-dmg..."
        pip3 install create-dmg || {
            echo "无法安装create-dmg，使用自制脚本创建DMG"
            
            # 复制到Applications的脚本
            mkdir -p app/.background
            cp src/core/logo.png app/.background/ 2>/dev/null || touch app/.background/.keep
            
            hdiutil create -volname "LX AI Installer" -srcfolder app -ov -format UDZO "LX_AI_Mac_Installer.dmg"
        }
    else
        create-dmg \
          --volname "LX AI Installer" \
          --window-pos 200 120 \
          --window-size 600 300 \
          --icon-size 100 \
          --icon "LX_AI.app" 175 120 \
          --hide-extension "LX_AI.app" \
          --app-drop-link 425 120 \
          "LX_AI_Mac_Installer.dmg" \
          "app/"
    fi
    
    echo "Mac安装包已创建: LX_AI_Mac_Installer.dmg"
    
    # 清理临时文件
    rm -rf app/
    
else
    echo "构建失败"
    exit 1
fi

echo "Mac安装包构建完成！"