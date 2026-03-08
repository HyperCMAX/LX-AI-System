#!/usr/bin/env python3
# build.py - LX 项目打包脚本

import subprocess
import sys
import shutil
from pathlib import Path

def build():
    """构建可执行文件"""
    print("🔨 开始打包...")
    
    # 清理旧的构建文件
    build_dir = Path("build")
    dist_dir = Path("dist")
    spec_file = Path("lx_ai.spec")
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("🧹 清理 build 目录")
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print("🧹 清理 dist 目录")
    
    # 运行 PyInstaller
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        str(spec_file)
    ]
    
    print(f"📦 执行：{' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    # 复制配置文件模板
    dist_lx_ai = dist_dir / "LX_AI"
    if dist_lx_ai.exists():
        # 复制 api_config.json 模板
        api_config_template = {
            "api": {
                "key": "",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-3.5-turbo"
            }
        }
        import json
        with open(dist_lx_ai / "api_config.json.template", 'w') as f:
            json.dump(api_config_template, f, indent=4)
        
        print("\n✅ 打包完成！")
        print(f"📁 可执行文件位置：{dist_lx_ai / 'LX_AI'}")
        print("\n📋 使用说明：")
        print("  1. 首次运行会自动创建配置文件")
        print("  2. 运行：./dist/LX_AI/LX_AI")
        print("  3. 配置 API：系统设置 → 全局 API 配置")
    else:
        print("❌ 打包失败")
        sys.exit(1)

if __name__ == "__main__":
    build()
