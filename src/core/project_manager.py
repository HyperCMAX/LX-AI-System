# src/core/project_manager.py

import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import sys


class ProjectManager:
    def __init__(self, projects_root: str = None):
        # =====================================================================
        # 智能检测运行环境（开发 or 打包）
        # =====================================================================
        self.is_bundle = getattr(sys, 'frozen', False)

        if self.is_bundle:
            # 含义：打包后 - 使用用户目录
            try:
                self.base_dir = Path.home() / ".lx_ai"
            except Exception as e:
                # 如果无法访问用户目录，则使用临时目录
                import tempfile
                self.base_dir = Path(tempfile.gettempdir()) / ".lx_ai"
                print(f"⚠️  无法访问用户目录，使用临时目录：{self.base_dir}")
        else:
            # 含义：开发环境 - 使用项目根目录
            self.base_dir = Path(__file__).parent.parent

        # =====================================================================
        # 项目目录
        # =====================================================================
        if projects_root:
            self.projects_root = Path(projects_root)
        else:
            self.projects_root = self.base_dir / "projects"
        
        # =====================================================================
        # 全局配置（只存项目路径列表，不存 API）
        # =====================================================================
        # 含义：全局配置始终在用户目录（打包前后都能访问）
        try:
            self.user_config_dir = Path.home() / ".lx_ai"
            self.global_config_path = self.user_config_dir / "config.json"
        except Exception as e:
            print(f"⚠️  无法访问用户配置目录: {e}")
            import tempfile
            self.user_config_dir = Path(tempfile.mkdtemp()) / ".lx_ai"
            self.global_config_path = self.user_config_dir / "config.json"

        # 含义：API 配置在项目文件夹内（不在这里）
        self.api_config_path = None  # 每个项目独立

        # 含义：延迟加载全局配置
        self.global_config = None

        # 含义：仅在非打包环境下输出路径信息
        if not self.is_bundle:
            print(f"✅ 运行模式：{'打包' if self.is_bundle else '开发'}")
            print(f"✅ 项目目录：{self.projects_root}")
            print(f"📁 全局配置：{self.global_config_path}")

    def ensure_dirs(self):
        """确保所有必要目录存在"""
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            import tempfile
            self.base_dir = Path(tempfile.gettempdir()) / ".lx_ai"
            self.base_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            self.projects_root.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"⚠️  无法创建项目目录 {self.projects_root}: {e}")
            import tempfile
            self.projects_root = Path(tempfile.mkdtemp()) / "lx_ai_projects"
            self.projects_root.mkdir(parents=True, exist_ok=True)
            print(f"⚠️  使用临时项目目录：{self.projects_root}")
        
        try:
            self.user_config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"⚠️  无法访问用户配置目录: {e}")
            import tempfile
            self.user_config_dir = Path(tempfile.mkdtemp()) / ".lx_ai"
            self.user_config_dir.mkdir(parents=True, exist_ok=True)

    def _load_global_config(self) -> Dict:
        """延迟加载全局配置"""
        if self.global_config is None:
            # 确保目录存在
            self.ensure_dirs()
            
            if self.global_config_path.exists():
                try:
                    with open(self.global_config_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if not content.strip():
                            self.global_config = {"projects": []}
                        else:
                            self.global_config = json.loads(content)
                except Exception as e:
                    print(f"⚠️  无法读取全局配置: {e}")
                    self.global_config = {"projects": []}
            else:
                self.global_config = {"projects": []}
        
        return self.global_config

    def _save_global_config(self):
        """保存全局配置"""
        # 确保目录存在
        self.ensure_dirs()
        
        try:
            with open(self.global_config_path, 'w', encoding='utf-8') as f:
                json.dump(self.global_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  无法保存全局配置: {e}")

    def list_projects(self) -> List[Dict[str, str]]:
        """列出所有项目"""
        config = self._load_global_config()
        projects = []
        for proj_path in config.get("projects", []):
            path_obj = Path(proj_path)
            if path_obj.exists():
                projects.append({
                    "name": path_obj.name,
                    "path": str(path_obj)
                })
        return projects

    def create_project(self, name: str, save_path: Optional[str] = None) -> str:
        """创建新项目"""
        # 确保目录存在
        self.ensure_dirs()
        
        if save_path:
            project_dir = Path(save_path) / name
        else:
            project_dir = self.projects_root / name

        project_dir.mkdir(parents=True, exist_ok=True)

        # 创建项目配置文件
        project_config_path = project_dir / "project.yaml"
        if not project_config_path.exists():
            project_data = {
                "project": {
                    "name": name,
                    "version": "1.0",
                    "created": datetime.now().isoformat(),
                    "updated": datetime.now().isoformat()
                },
                "initial_state": "root",
                "commands": [],
                "states": [
                    {
                        "id": "root",
                        "description": "根状态",
                        "mode": "stable",
                        "parent_id": None,
                        "available_commands": [],
                        "command_transitions": {}
                    }
                ]
            }
            with open(project_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(project_data, f, default_flow_style=False, allow_unicode=True)

        # 添加到全局配置
        config = self._load_global_config()
        project_str_path = str(project_dir)
        if project_str_path not in config.get("projects", []):
            config.setdefault("projects", []).append(project_str_path)
            self._save_global_config()

        return str(project_dir)

    def open_project(self, project_path: str) -> Dict:
        path = Path(project_path)
        if not path.exists():
            raise FileNotFoundError(f"项目不存在：{project_path}")

        if path.is_file():
            if path.name == "project.yaml":
                path = path.parent
            else:
                raise FileNotFoundError("请指定项目文件夹或 project.yaml 文件")

        # 加载 project.yaml
        project_file = path / "project.yaml"
        if not project_file.exists():
            raise FileNotFoundError(f"项目配置文件不存在：{project_file}")
        with open(project_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # =====================================================================
        # 加载项目级 config.json（API 配置在项目文件夹内）✅
        # =====================================================================
        config_file = path / "config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                project_api_config = json.load(f)
            config["api"] = project_api_config.get("api", {})
        else:
            config["api"] = {"key": "", "base_url": "", "model": ""}

        self.global_config["last_project"] = str(path)
        self._save_global_config()
        return config

    def save_project(self, project_path: str, config: Dict):
        path = Path(project_path)
        if path.is_file():
            path = path.parent

        # 分离 project.yaml 和 config.json
        project_config = {k: v for k, v in config.items() if k != "api"}
        api_config = {"api": config.get("api", {})}

        # 保存 project.yaml
        project_config["project"]["updated"] = datetime.now().isoformat()
        with open(path / "project.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(project_config, f, allow_unicode=True, default_flow_style=False)

        # =====================================================================
        # 保存项目级 config.json（API 配置在项目文件夹内）✅
        # =====================================================================
        with open(path / "config.json", 'w', encoding='utf-8') as f:
            json.dump(api_config, f, indent=4, ensure_ascii=False)

    def get_global_api_config(self) -> Dict:
        """获取全局 API 配置（从项目配置读取，或返回空）"""
        return self.global_config.get("api", {})

    def set_global_api_config(self, api_key: str, base_url: str, model: str):
        """设置全局 API 配置（保存到全局配置，作为默认值）"""
        self.global_config["api"] = {
            "key": api_key,
            "base_url": base_url,
            "model": model
        }
        self._save_global_config()

    def delete_project(self, project_path: str) -> bool:
        path = Path(project_path)
        if not path.exists():
            return False
        
        # 从全局配置中移除
        config = self._load_global_config()
        project_str_path = str(path)
        if project_str_path in config.get("projects", []):
            config["projects"].remove(project_str_path)
            self._save_global_config()
        
        # 删除项目目录
        import shutil
        shutil.rmtree(path)
        return True

    def get_config_dir(self) -> Path:
        return self.user_config_dir
            
    def print_startup_info(self):
        """在启动时打印信息"""
        if self.is_bundle:
            print(f"✅ 运行模式：{'打包' if self.is_bundle else '开发'}")
            print(f"✅ 项目目录：{self.projects_root}")
            print(f"📁 全局配置：{self.global_config_path}")