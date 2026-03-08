# src/core/command_handlers.py

# 导入 subprocess 用于执行系统命令
import subprocess
# 导入 requests 用于 HTTP 请求
import requests
# 导入 json 用于数据处理
import json
# 导入 typing 用于类型提示
from typing import Any, Dict, Optional, Callable, List
# 导入 Path 用于文件操作
from pathlib import Path


class ConfigHandler:
    """配置式命令处理器"""

    @staticmethod
    def run_command(command: str, args_from: str = None, **params) -> str:
        try:
            full_command = command.split()
            if args_from and args_from in params:
                full_command.append(str(params[args_from]))
            result = subprocess.run(full_command, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"命令执行失败：{result.stderr}"
        except Exception as e:
            return f"执行错误：{str(e)}"

    @staticmethod
    def http_request(url: str, method: str = "GET", body: Dict = None, headers: Dict = None, **params) -> str:
        try:
            if body:
                for key, value in params.items():
                    if isinstance(value, str):
                        body = json.loads(json.dumps(body).replace(f"${{{key}}}", value))
            response = requests.request(
                method=method,
                url=url,
                json=body if method in ["POST", "PUT", "PATCH"] else None,
                params=body if method == "GET" else None,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"HTTP 请求失败：{str(e)}"

    @staticmethod
    def echo(text: str, **params) -> str:
        for key, value in params.items():
            text = text.replace(f"${{{key}}}", str(value))
        return text

    @staticmethod
    def state_jump(target: str, **params) -> str:
        return f"跳转到 {target}"

    @staticmethod
    def output(output_key: str, format: str = "json", data: Dict = None,
               data_params: List = None, **params) -> Dict:
        """
        传出数据供外部执行器处理
        - output_key: 数据键名，用于外部识别
        - format: 输出格式 (json/text)
        - data: 固定数据
        - data_params: 从命令参数中获取的数据字段名
        - params: 命令执行时传入的参数
        """
        output_data = {}

        # 含义：添加固定数据
        if data:
            output_data.update(data)

        # 含义：添加动态参数
        if data_params:
            for param_name in data_params:
                if param_name in params:
                    output_data[param_name] = params[param_name]

        return {
            "output_key": output_key,
            "format": format,
            "data": output_data
        }


class PluginLoader:
    """项目插件加载器"""

    @staticmethod
    def load_handlers(project_path: str) -> Dict[str, Callable]:
        handlers = {}
        project_dir = Path(project_path)
        if project_dir.is_file():
            project_dir = project_dir.parent
        handler_file = project_dir / "handlers.py"

        if not handler_file.exists():
            return handlers

        import importlib.util
        spec = importlib.util.spec_from_file_location("handlers", handler_file)
        module = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(module)
            for name in dir(module):
                obj = getattr(module, name)
                if callable(obj) and not name.startswith("_"):
                    handlers[name] = obj
        except Exception as e:
            print(f"⚠️  加载插件失败：{e}")

        return handlers


class HandlerRegistry:
    """处理器注册表"""

    BUILTIN_HANDLERS = {
        "run_command": ConfigHandler.run_command,
        "http_request": ConfigHandler.http_request,
        "echo": ConfigHandler.echo,
        "state_jump": ConfigHandler.state_jump,
        "output": ConfigHandler.output,
    }

    def __init__(self):
        self.plugin_handlers: Dict[str, Callable] = {}

    def load_project_plugins(self, project_path: str):
        self.plugin_handlers = PluginLoader.load_handlers(project_path)

    def get_handler(self, handler_type: str, function_name: str = None) -> Optional[Callable]:
        if handler_type == "plugin" and function_name:
            return self.plugin_handlers.get(function_name)
        return self.BUILTIN_HANDLERS.get(handler_type)