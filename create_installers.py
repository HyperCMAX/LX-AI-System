#!/usr/bin/env python3
"""
创建跨平台安装包的脚本
用于为LX-AI项目创建Mac和Windows安装包
"""

import os
import sys
import shutil
import zipfile
import tarfile
from pathlib import Path


def create_mac_installer():
    """创建Mac安装包"""
    print("Creating Mac installer...")
    
    # 创建一个包含可执行文件和依赖的目录结构
    mac_dist_dir = "LX_AI_Mac_Package"
    if os.path.exists(mac_dist_dir):
        shutil.rmtree(mac_dist_dir)
    
    os.makedirs(mac_dist_dir, exist_ok=True)
    
    # 复制可执行文件及其依赖
    src_dir = "src"
    target_dir = os.path.join(mac_dist_dir, "LX_AI.app", "Contents", "MacOS")
    os.makedirs(target_dir, exist_ok=True)
    
    # 复制可执行文件
    shutil.copy2(os.path.join(src_dir, "LX_AI"), target_dir)
    
    # 复制依赖目录
    if os.path.exists(os.path.join(src_dir, "lib")):
        shutil.copytree(os.path.join(src_dir, "lib"), 
                       os.path.join(mac_dist_dir, "LX_AI.app", "Contents", "lib"))
    if os.path.exists(os.path.join(src_dir, "share")):
        shutil.copytree(os.path.join(src_dir, "share"), 
                       os.path.join(mac_dist_dir, "LX_AI.app", "Contents", "share"))
    
    # 创建压缩包
    with zipfile.ZipFile("LX_AI_Mac_Installer.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(mac_dist_dir):
            for file in files:
                file_path = os.path.join(root, file)
                archive_path = os.path.relpath(file_path, mac_dist_dir)
                zipf.write(file_path, os.path.join("LX_AI.app", archive_path))
    
    print("Mac installer created: LX_AI_Mac_Installer.zip")


def create_windows_installer():
    """创建Windows安装包"""
    print("Creating Windows installer...")
    
    # 使用PyInstaller创建Windows可执行文件
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 运行PyInstaller创建单文件可执行程序
    import subprocess
    result = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "LX_AI",
        "--add-data", "src/core:core",
        "--add-data", "src/api_config.json:.",
        "src/cli.py"
    ], cwd=os.getcwd())
    
    if result.returncode == 0:
        print("Windows executable created in dist/ folder")
        
        # 创建ZIP压缩包
        windows_dist_dir = "LX_AI_Windows_Package"
        if os.path.exists(windows_dist_dir):
            shutil.rmtree(windows_dist_dir)
        
        os.makedirs(windows_dist_dir, exist_ok=True)
        
        # 复制可执行文件
        shutil.copy2("dist/LX_AI.exe", windows_dist_dir)
        
        # 创建说明文件
        with open(os.path.join(windows_dist_dir, "README.txt"), "w", encoding="utf-8") as f:
            f.write("LX-AI Application\n\n")
            f.write("双击 LX_AI.exe 运行应用程序\n\n")
            f.write("注意：首次运行可能需要允许来自未知发布者的程序执行。\n")
        
        # 创建压缩包
        with zipfile.ZipFile("LX_AI_Windows_Installer.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(windows_dist_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    archive_path = os.path.relpath(file_path, windows_dist_dir)
                    zipf.write(file_path, archive_path)
        
        print("Windows installer created: LX_AI_Windows_Installer.zip")
    else:
        print("Failed to create Windows executable with PyInstaller")


def main():
    """主函数"""
    print("Creating cross-platform installers for LX-AI...")
    
    # 创建Mac安装包
    create_mac_installer()
    
    # 如果是Windows系统，则创建Windows安装包
    if sys.platform.startswith('win'):
        create_windows_installer()
    else:
        # 如果是Linux或Mac，提供创建Windows安装包的说明
        print("Skipping Windows installer creation on non-Windows platform.")
        print("To create Windows installer, run this script on a Windows machine.")
        print("Alternatively, use cx_Freeze or PyInstaller directly on this platform.")


if __name__ == "__main__":
    main()