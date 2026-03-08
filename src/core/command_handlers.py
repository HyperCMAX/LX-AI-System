# src/core/command_handlers.py

import subprocess
import requests
import json
from typing import Any, Dict, Optional, Callable, List
from pathlib import Path


class ConfigHandler:
    """配置式命令处理器"""
    
    @staticmethod
    def run_command(command: str, args_from: str = None, timeout: int = 30, **params) -> Dict:
        """
        执行系统命令
        返回：{
            "success": bool,
            "stdout": str,
            "stderr": str,
            "returncode": int,
            "auto_return": bool  # 标记是否自动返回值
        }
        """
        try:
            full_command = command.split()
            if args_from and args_from in params:
                full_command.append(str(params[args_from]))
            
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # 自动返回值
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode,
                "auto_return": True,  # 标记为自动返回值
                "return_type": "command_output"
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "命令执行超时",
                "auto_return": True,
                "return_type": "timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "auto_return": True,
                "return_type": "error"
            }
    
    @staticmethod
    def http_request(url: str, method: str = "GET", body: Dict = None, 
                     headers: Dict = None, timeout: int = 30, **params) -> Dict:
        """
        发送 HTTP 请求
        返回：{
            "success": bool,
            "status_code": int,
            "response_body": str,
            "auto_return": bool
        }
        """
        try:
            if body:
                for key, value in params.items():
                    if isinstance(value, str):
                        body_str = json.dumps(body)
                        body = json.loads(body_str.replace(f"${key}", value))
            
            response = requests.request(
                method=method,
                url=url,
                json=body if method in ["POST", "PUT", "PATCH"] else None,
                params=body if method == "GET" else None,
                headers=headers,
                timeout=timeout
            )
            
            # 自动返回值
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response_body": response.text,
                "auto_return": True,
                "return_type": "http_response"
            }
        except requests.Timeout:
            return {
                "success": False,
                "error": "HTTP 请求超时",
                "auto_return": True,
                "return_type": "timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "auto_return": True,
                "return_type": "error"
            }
    
    @staticmethod
    def echo(text: str, **params) -> Dict:
        """返回固定文本"""
        for key, value in params.items():
            text = text.replace(f"${key}", str(value))
        return {
            "success": True,
            "output": text,
            "auto_return": True,
            "return_type": "echo"
        }
    
    @staticmethod
    def state_jump(target: str, **params) -> Dict:
        """状态跳转"""
        return {
            "success": True,
            "target_state": target,
            "auto_return": True,
            "return_type": "state_jump"
        }
    
    @staticmethod
    def output(output_key: str, format: str = "json", data: Dict = None, 
               data_params: List = None, **params) -> Dict:
        """传出数据"""
        output_data = {}
        
        if data:
            output_data.update(data)
        
        if data_params:
            for param_name in data_params:
                if param_name in params:
                    output_data[param_name] = params[param_name]
        
        return {
            "output_key": output_key,
            "format": format,
            "data": output_data,
            "auto_return": True,
            "return_type": "output"
        }
    
    @staticmethod
    def wait_for_user(prompt: str = "请输入返回值", **params) -> Dict:
        """
        等待用户手动输入返回值
        返回：{
            "success": True,
            "auto_return": False,  # 标记为需要手动输入
            "return_type": "manual_input",
            "prompt": str  # 提示用户输入什么
        }
        """
        return {
            "success": True,
            "auto_return": False,
            "return_type": "manual_input",
            "prompt": prompt
        }
    
    @staticmethod
    def wait_for_external(file_path: str, timeout: int = 300, **params) -> Dict:
        """
        等待外部 API 返回值（通过文件）
        返回：{
            "success": True,
            "auto_return": False,
            "return_type": "external",
            "file_path": str,
            "timeout": int
        }
        """
        return {
            "success": True,
            "auto_return": False,
            "return_type": "external",
            "file_path": file_path,
            "timeout": timeout
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
        "wait_for_user": ConfigHandler.wait_for_user,
        "wait_for_external": ConfigHandler.wait_for_external,
    }
    
    def __init__(self):
        self.plugin_handlers: Dict[str, Callable] = {}
    
    def load_project_plugins(self, project_path: str):
        self.plugin_handlers = PluginLoader.load_handlers(project_path)
    
    def get_handler(self, handler_type: str, function_name: str = None) -> Optional[Callable]:
        if handler_type == "plugin" and function_name:
            return self.plugin_handlers.get(function_name)
        return self.BUILTIN_HANDLERS.get(handler_type)