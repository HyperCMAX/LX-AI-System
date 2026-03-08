#!/usr/bin/env python3
# cleanup_for_package.py
# 用途：打包前清除所有敏感数据

import json
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent

# 需要清理的文件
FILES_TO_CLEAN = [
    BASE_DIR / "api_config.json",
    BASE_DIR / "config.json",
]

# 全局 API 配置模板
API_CONFIG_TEMPLATE = {
    "api": {
        "key": "",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo"
    }
}

# 全局配置模板
GLOBAL_CONFIG_TEMPLATE = {
    "last_project": None,
    "projects": []
}

# 项目级 API 配置模板
PROJECT_API_TEMPLATE = {
    "api": {
        "key": "",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo"
    }
}


def clean_file(file_path: Path, template: dict):
    """重置配置文件为模板内容"""
    if file_path.exists():
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=4, ensure_ascii=False)
        print(f"✅ 已重置：{file_path}")
    else:
        print(f"⚠️  文件不存在：{file_path}")


def clean_project_configs():
    """清理所有项目级配置"""
    projects_dir = BASE_DIR / "projects"
    if not projects_dir.exists():
        print("⚠️  项目目录不存在")
        return

    for project_dir in projects_dir.iterdir():
        if project_dir.is_dir():
            config_file = project_dir / "config.json"
            if config_file.exists():
                clean_file(config_file, PROJECT_API_TEMPLATE)
                print(f"✅ 已清理项目配置：{project_dir.name}")


def clean_handlers():
    """清理自定义插件（可选）"""
    projects_dir = BASE_DIR / "projects"
    if not projects_dir.exists():
        return

    for project_dir in projects_dir.iterdir():
        if project_dir.is_dir():
            handlers_file = project_dir / "handlers.py"
            if handlers_file.exists():
                # 替换为模板内容
                template = '''# 项目自定义处理器
# 在此定义 Python 函数，可在命令配置中引用

def example_handler(param1: str, **kwargs) -> str:
    """示例处理函数"""
    return f"处理结果：{param1}"
'''
                with open(handlers_file, 'w', encoding='utf-8') as f:
                    f.write(template)
                print(f"✅ 已重置插件：{project_dir.name}/handlers.py")


def main():
    print("=" * 50)
    print("🧹 开始清理敏感数据")
    print("=" * 50)

    # 清理全局配置
    print("\n📁 全局配置:")
    clean_file(BASE_DIR / "api_config.json", API_CONFIG_TEMPLATE)
    clean_file(BASE_DIR / "config.json", GLOBAL_CONFIG_TEMPLATE)

    # 清理项目配置
    print("\n📁 项目配置:")
    clean_project_configs()

    # 清理插件（可选）
    print("\n📁 自定义插件:")
    clean_handlers()

    print("\n" + "=" * 50)
    print("✅ 清理完成！可以安全打包")
    print("=" * 50)
    print("\n📦 建议打包时排除以下文件/目录:")
    print("   - __pycache__/")
    print("   - *.pyc")
    print("   - .venv/")
    print("   - .git/")
    print("   - *.log")


if __name__ == "__main__":
    main()