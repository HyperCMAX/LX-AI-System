# src/core/project_manager.py

import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


class ProjectManager:
    def __init__(self, projects_root: str = None):
        # =====================================================================
        # 智能检测运行环境（开发 or 打包）
        # =====================================================================
        self.is_bundle = getattr(sys, 'frozen', False)

        if self.is_bundle:
            # 含义：打包后 - 使用用户目录
            self.base_dir = Path.home() / ".lx_ai"
            self.base_dir.mkdir(parents=True, exist_ok=True)
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
        self.projects_root.mkdir(parents=True, exist_ok=True)

        # =====================================================================
        # 全局配置（只存项目路径列表，不存 API）
        # =====================================================================
        # 含义：全局配置始终在用户目录（打包前后都能访问）
        self.user_config_dir = Path.home() / ".lx_ai"
        self.user_config_dir.mkdir(parents=True, exist_ok=True)
        self.global_config_path = self.user_config_dir / "config.json"

        # 含义：API 配置在项目文件夹内（不在这里）
        self.api_config_path = None  # 每个项目独立

        # 含义：加载全局配置（项目列表）
        self.global_config = self._load_global_config()

        # 含义：打印路径信息
        print(f"✅ 运行模式：{'打包' if self.is_bundle else '开发'}")
        print(f"✅ 项目目录：{self.projects_root}")
        print(f"📁 全局配置：{self.global_config_path}")

    def _load_global_config(self) -> Dict:
        if self.global_config_path.exists():
            try:
                with open(self.global_config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.strip():
                        return self._get_default_global_config()
                    return json.loads(content)
            except Exception as e:
                print(f"⚠️  加载全局配置失败：{e}")
                return self._get_default_global_config()
        return self._get_default_global_config()

    def _get_default_global_config(self) -> Dict:
        return {
            "last_project": None, 
            "projects": [],
            "context_length": 5,  # 新增：默认上下文长度
            "command_timeout": 30  # 新增：默认命令超时时间
        }

    def _save_global_config(self):
        try:
            with open(self.global_config_path, 'w', encoding='utf-8') as f:
                json.dump(self.global_config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存全局配置失败：{e}")

    # =============================================================================
    # 上下文长度管理
    # =============================================================================
    
    def get_context_length(self) -> int:
        """获取全局上下文长度设置"""
        return self.global_config.get("context_length", 5)

    def set_context_length(self, length: int):
        """设置全局上下文长度"""
        self.global_config["context_length"] = length
        self._save_global_config()

    # =============================================================================
    # 命令超时时间管理
    # =============================================================================
    
    def get_command_timeout(self) -> int:
        """获取命令超时时间（秒）"""
        return self.global_config.get("command_timeout", 30)

    def set_command_timeout(self, timeout: int):
        """设置命令超时时间"""
        self.global_config["command_timeout"] = timeout
        self._save_global_config()

    # =============================================================================
    # 对话历史管理
    # =============================================================================
    
    def get_conversations_dir(self, project_path: str) -> Path:
        """获取项目的对话历史目录"""
        path = Path(project_path)
        if path.is_file():
            path = path.parent
        conv_dir = path / "conversations"
        # 含义：确保目录存在
        conv_dir.mkdir(exist_ok=True)
        return conv_dir

    def list_conversations(self, project_path: str) -> List[Dict]:
        """列出项目的所有对话历史"""
        conv_dir = self.get_conversations_dir(project_path)
        conversations = []
        
        if conv_dir.exists():
            for conv_file in conv_dir.glob("*.json"):
                try:
                    with open(conv_file, 'r', encoding='utf-8') as f:
                        conv_data = json.load(f)
                    
                    messages = conv_data.get("messages", [])
                    user_count = sum(1 for m in messages if m.get("role") == "user")
                    assistant_count = sum(1 for m in messages if m.get("role") == "assistant")
                    
                    conversations.append({
                        "id": conv_file.stem,
                        "name": conv_data.get("name", conv_file.stem),
                        "created": conv_data.get("created", "Unknown"),
                        "updated": conv_data.get("updated", "Unknown"),
                        "message_count": len(messages),
                        "round_count": min(user_count, assistant_count),  # 新增：对话轮数统计
                        "path": str(conv_file)
                    })
                except:
                    continue
        
        conversations.sort(key=lambda x: x.get("updated", ""), reverse=True)
        return conversations

    def create_conversation(self, project_path: str, name: str = None) -> str:
        """创建新对话 - 返回对话 ID 而非路径"""
        conv_dir = self.get_conversations_dir(project_path)
        
        # 生成对话 ID
        conv_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        conv_file = conv_dir / f"{conv_id}.json"
        
        # 创建对话文件
        conv_data = {
            "id": conv_id,
            "name": name or f"对话 {conv_id}",
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "messages": [],
            "context_length": self.get_context_length()
        }
        
        with open(conv_file, 'w', encoding='utf-8') as f:
            json.dump(conv_data, f, indent=4, ensure_ascii=False)
        
        # 修复：返回对话 ID 而非路径
        return conv_id

    def load_conversation(self, project_path: str, conversation_id: str) -> Dict:
        """加载对话历史"""
        conv_dir = self.get_conversations_dir(project_path)
        conv_file = conv_dir / f"{conversation_id}.json"
        
        if not conv_file.exists():
            raise FileNotFoundError(f"对话不存在：{conversation_id}")
        
        with open(conv_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_conversation(self, project_path: str, conversation_id: str, messages: List[Dict]):
        """保存对话历史"""
        conv_dir = self.get_conversations_dir(project_path)
        conv_file = conv_dir / f"{conversation_id}.json"
        
        if not conv_file.exists():
            conv_data = {
                "id": conversation_id,
                "name": f"对话 {conversation_id}",
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
                "messages": messages,
                "context_length": self.get_context_length()
            }
        else:
            with open(conv_file, 'r', encoding='utf-8') as f:
                conv_data = json.load(f)
            conv_data["messages"] = messages
            conv_data["updated"] = datetime.now().isoformat()
            conv_data["context_length"] = self.get_context_length()
        
        with open(conv_file, 'w', encoding='utf-8') as f:
            json.dump(conv_data, f, indent=4, ensure_ascii=False)

    def delete_conversation(self, project_path: str, conversation_id: str) -> bool:
        """删除对话历史"""
        conv_dir = self.get_conversations_dir(project_path)
        conv_file = conv_dir / f"{conversation_id}.json"
        
        if conv_file.exists():
            conv_file.unlink()
            return True
        return False

    def view_conversation(self, project_path: str, conversation_id: str) -> Optional[Dict]:
        """查看对话内容"""
        try:
            return self.load_conversation(project_path, conversation_id)
        except:
            return None

    def list_projects(self) -> List[Dict]:
        projects = []
        if not self.projects_root.exists():
            return projects
        for project_dir in self.projects_root.iterdir():
            if project_dir.is_dir():
                config_file = project_dir / "project.yaml"
                if config_file.exists():
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                    projects.append({
                        "name": config.get("project", {}).get("name", project_dir.name),
                        "path": str(project_dir),
                        "version": config.get("project", {}).get("version", "1.0"),
                        "updated": config.get("project", {}).get("updated", "Unknown")
                    })
        return projects

    def create_project(self, name: str, save_path: str = None) -> str:
        # =====================================================================
        # 确定项目文件夹路径
        # =====================================================================
        if save_path:
            user_path = Path(save_path)
            if user_path.is_file():
                parent_dir = user_path.parent
            elif user_path.is_dir():
                parent_dir = user_path
            else:
                parent_dir = user_path
                parent_dir.mkdir(parents=True, exist_ok=True)
            # 含义：在指定父目录下创建项目文件夹
            project_dir = parent_dir / name
        else:
            # 含义：在默认项目目录下创建项目文件夹
            project_dir = self.projects_root / name

        # 含义：创建项目文件夹
        project_dir.mkdir(parents=True, exist_ok=True)

        # =====================================================================
        # 文件 1：project.yaml（状态和命令编排）
        # =====================================================================
        project_config = {
            "project": {
                "name": name,
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat()
            },
            "initial_state": "root",
            "commands": [
                {"id": "help", "description": "显示帮助信息"},
                {"id": "back", "description": "返回上一级"}
            ],
            "states": [
                {
                    "id": "root",
                    "description": "主菜单",
                    "mode": "stable",
                    "parent_id": None,
                    "available_commands": ["help"],
                    "command_transitions": {}
                }
            ]
        }

        with open(project_dir / "project.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(project_config, f, allow_unicode=True, default_flow_style=False)

        # =====================================================================
        # 文件 2：config.json（项目级 API 配置）✅ 在项目文件夹内
        # =====================================================================
        api_config = {
            "api": {
                "key": "",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-3.5-turbo"
            }
        }

        with open(project_dir / "config.json", 'w', encoding='utf-8') as f:
            json.dump(api_config, f, indent=4, ensure_ascii=False)

        # =====================================================================
        # 文件 3：handlers.py（自定义插件）
        # =====================================================================
        handlers_content = '''# 项目自定义处理器
# 在此定义 Python 函数，可在命令配置中引用

def example_handler(param1: str, **kwargs) -> str:
    """示例处理函数"""
    return f"处理结果：{param1}"
'''
        with open(project_dir / "handlers.py", 'w', encoding='utf-8') as f:
            f.write(handlers_content)

        # =====================================================================
        # 更新全局配置（只存项目路径列表）
        # =====================================================================
        project_path_str = str(project_dir)
        if "projects" not in self.global_config:
            self.global_config["projects"] = []

        if project_path_str not in self.global_config["projects"]:
            self.global_config["projects"].append(project_path_str)
            self._save_global_config()

        print(f"✅ 项目已创建：{project_dir}")
        print(f"   - project.yaml")
        print(f"   - config.json (API 配置)")
        print(f"   - handlers.py")

        return project_path_str

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
        if "projects" in self.global_config:
            self.global_config["projects"] = [
                p for p in self.global_config["projects"] if p != str(path)
            ]
            self._save_global_config()
        import shutil
        shutil.rmtree(path)
        return True

    def get_config_dir(self) -> Path:
        return self.user_config_dir
