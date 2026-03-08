# src/core/config_manager.py

# 导入 json 模块用于处理配置文件
import json
# 导入 os 模块用于处理文件路径
import os
# 导入 Path 用于构建跨平台路径
from pathlib import Path
# 导入 typing 用于类型提示
from typing import Optional, Dict

# 定义配置管理器类
class ConfigManager:
    # 含义：初始化方法，确定配置文件路径
    def __init__(self, config_file: str = "config.json"):
        # =====================================================================
        # 修复：使用用户主目录的 .lx_ai 配置目录
        # =====================================================================
        # 含义：获取用户主目录
        home_dir = Path.home()
        # 含义：构建 .lx_ai 配置目录路径
        self.lx_ai_dir = home_dir / ".lx_ai"
        # 含义：确保配置目录存在
        self.lx_ai_dir.mkdir(parents=True, exist_ok=True)
        # 含义：构建配置文件的完整绝对路径
        self.config_path = self.lx_ai_dir / config_file
        # 含义：初始化配置数据字典
        self.config: Dict = {}
        # 含义：加载现有配置
        self._load()

    # 含义：内部方法，从文件加载配置
    def _load(self):
        # 含义：检查配置文件是否存在
        if self.config_path.exists():
            # 含义：如果存在，打开文件
            with open(self.config_path, 'r', encoding='utf-8') as f:
                try:
                    # 含义：解析 JSON 内容到字典
                    self.config = json.load(f)
                except json.JSONDecodeError:
                    # 含义：如果 JSON 格式错误，初始化为空字典
                    self.config = {}
        else:
            # 含义：如果文件不存在，初始化为空字典
            self.config = {}

    # 含义：内部方法，保存配置到文件
    def _save(self):
        # 含义：打开文件准备写入
        with open(self.config_path, 'w', encoding='utf-8') as f:
            # 含义：将配置字典写入文件，格式化缩进
            json.dump(self.config, f, indent=4)

    # 含义：获取 API 配置的方法
    def get_api_config(self) -> Dict:
        # 含义：返回配置中的 api 部分，如果没有则返回空字典
        return self.config.get("api", {})

    # 含义：设置 API 配置的方法
    def set_api_config(self, api_key: str, base_url: str, model: str):
        # 含义：如果配置中没有 api 键，创建一个
        if "api" not in self.config:
            self.config["api"] = {}
        # 含义：更新 API Key
        self.config["api"]["key"] = api_key
        # 含义：更新 API 基础 URL
        self.config["api"]["base_url"] = base_url
        # 含义：更新模型名称
        self.config["api"]["model"] = model
        # 含义：保存更改到文件
        self._save()

    # 含义：检查配置是否完整的方法
    def is_configured(self) -> bool:
        # 含义：获取 API 配置
        api = self.get_api_config()
        # 含义：检查是否包含关键字段
        return bool(api.get("key") and api.get("base_url") and api.get("model"))