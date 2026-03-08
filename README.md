# LX-AI 系统 - 完整文件目录与技术文档

**版本**: 1.1  
**作者**: ArXav (eurexon@outlook.com)  
**许可证**: MIT License  
**分发方式**: 源代码分发 (无预编译安装包)

---

## 📖 项目概述

**LX-AI 系统** 是一个基于状态驱动的 AI 指令披露框架，专为与大型语言模型（LLMs）交互而设计。它通过状态机管理命令集的可见性，实现安全、可控的 AI 交互，提供全面的 AI 驱动交互和数据管理解决方案。
如果你想直接使用，可以直接下载此unix文件 -->[src/LX_AI](https://github.com/HyperCMAX/LX-AI-System/blob/main/src/LX_AI)

### 核心特性

| 特性 | 说明 |
| :--- | :--- |
| **状态驱动** | 命令集根据当前状态动态披露，确保交互可控 |
| **双模式支持** | **稳定模式**（预设流程）+ **自由模式**（AI 动态生成） |
| **双对象交互** | 面向用户（自然语言）+ 面向系统（结构化命令） |
| **项目制管理** | 每个项目独立配置，支持自定义路径与插件 |
| **交互式 CLI** | 用户友好的命令行界面，无缝交互体验 |
| **数据持久化** | 稳健的本地对话历史与配置存储 |

---

## 🚀 快速开始

本项目目前以**源代码形式**分发，用户需配置 Python 环境后运行。

### 1. 环境要求

确保已安装 **Python 3.9+**。

```bash
python3 --version
```

### 2. 安装依赖

克隆仓库后，在项目根目录安装所需依赖：

```bash
pip install -r requirements.txt
```

### 3. 运行程序

进入 `src` 目录并启动 CLI 主程序：

```bash
cd src
python3 cli.py
```

*注：程序启动后进入菜单界面，选择"❌ 退出"可关闭程序。*

### 4. 初始配置

1.  **配置全局 API**: 在主菜单选择 `⚙️ 系统设置` → `全局 API 配置`，输入 API Key、Base URL 和模型名称。
2.  **新建项目**: 在主菜单选择 `➕ 新建项目`，输入项目名称并选择保存位置。
3.  **运行项目**: 打开项目后，选择 `▶️ 当前窗口运行` 开始交互。

---

## 📁 完整文件目录结构

```text
LX/
├── README.md                         # 项目说明
├── setup.py                          # Python 包安装脚本
├── publish/                          # 发布目录
│   ├── INSTALL.md                    # 安装说明
│   ├── LX_AI                         # 可执行文件
│   └── README.md                     # 发布版说明
└── src/                              # 源代码目录
    ├── cli.py                        # 主程序入口（CLI 界面）
    ├── core/                         # 核心模块
    │   ├── command_handlers.py       # 命令处理器
    │   ├── config_manager.py         # 配置管理器
    │   ├── config.py                 # 系统配置常量
    │   ├── controller.py             # 系统控制器
    │   ├── executor.py               # 命令执行器
    │   ├── logger.py                 # 事件日志器
    │   ├── message_protocol.py       # 通讯协议定义
    │   ├── models.py                 # 数据模型定义
    │   ├── parser.py                 # 响应解析器
    │   ├── project_loader.py         # 项目加载器
    │   ├── project_manager.py        # 项目管理器
    │   ├── prompt_templates.py       # 提示词模板
    │   ├── registry.py               # 命令注册中心
    │   └── state_machine.py          # 状态机管理
    └── projects/                     # 项目存储目录
```

---

## 🏗 核心架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户界面 (CLI)                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        系统控制器                                │
│                    (SystemController)                           │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│   状态机    │   命令注册   │   命令执行   │     事件日志        │
│ StateMachine│  Registry   │  Executor   │     Logger          │
└─────────────┴─────────────┴─────────────┴─────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        LLM 集成层                                │
│              (架构师 AI + 执行者 AI 双模型)                       │
└─────────────────────────────────────────────────────────────────┘
```

### 核心模块说明

| 模块 | 文件 | 功能 |
| :--- | :--- | :--- |
| **配置** | `core/config.py` | 系统常量（正则、深度限制、历史长度） |
| **模型** | `core/models.py` | Pydantic 数据模型（命令、状态、事件、反馈） |
| **注册** | `core/registry.py` | 命令注册与查询 |
| **状态** | `core/state_machine.py` | 状态流转、深度计算、命令披露 |
| **协议** | `core/message_protocol.py` | LLM 输入输出数据结构 |
| **提示词** | `core/prompt_templates.py` | 系统提示词模板 |
| **解析** | `core/parser.py` | LLM 输出解析与验证 |
| **执行** | `core/executor.py` | 命令执行与结果返回 |
| **日志** | `core/logger.py` | 系统事件记录（滑动窗口） |
| **控制器** | `core/controller.py` | 核心编排（状态 + 命令+LLM） |
| **项目管理** | `core/project_manager.py` | 项目创建、打开、保存 |
| **命令处理** | `core/command_handlers.py` | 命令处理器（echo/HTTP/插件等） |

### 辅助脚本 (`src/`)

| 文件 | 功能 |
| :--- | :--- |
| `cli.py` | 主程序入口，交互式 CLI 界面 |
| `test_*.py` | 各阶段功能测试脚本 |
| `scenario_example.py` | 场景配置示例 |
| `demo_run.py` | 简易演示入口 |
| `verify_depth.py` | 深度限制验证工具 |

---

## ⚙️ 配置说明

### 1. 全局 API 配置 (`api_config.json`)
```json
{
    "api": {
        "key": "YOUR_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo"
    }
}
```

### 2. 全局系统配置 (`config.json`)
```json
{
    "last_project": "/path/to/project",
    "projects": ["/path/to/project1", "/path/to/project2"]
}
```

### 3. 项目配置 (`projects/项目名/project.yaml`)
```yaml
project:
  name: "客服助手"
  version: "1.0"
  created: "2024-01-01T00:00:00"
  updated: "2024-01-01T00:00:00"

initial_state: "root"

commands:
  - id: "help"
    description: "显示帮助"
  - id: "search"
    description: "搜索"
    handler:
      type: "http_request"
      config:
        url: "https://api.example.com/search"
        method: "GET"

states:
  - id: "root"
    description: "主菜单"
    mode: "stable"
    parent_id: null
    available_commands: ["help", "search"]
    command_transitions:
      search: "search_state"
```

### 4. 项目级 API 配置 (`projects/项目名/config.json`)
项目可独立配置 API，覆盖全局设置。
```json
{
    "api": {
        "key": "",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo"
    }
}
```

---

## 🛠 功能详解

### 1. 运行模式

| 模式 | 说明 | 适用场景 |
| :--- | :--- | :--- |
| **稳定模式 (stable)** | 命令集预设，不可动态更改。状态跳转由 `command_transitions` 配置。 | 固定业务流程（如支付、审批） |
| **自由模式 (free)** | 架构师 AI 动态生成状态描述和命令集。深度限制最多 5 层。 | 探索性任务（如调研、创意） |

### 2. 命令处理器类型

| 类型 | 说明 | 配置示例 |
| :--- | :--- | :--- |
| **echo** | 返回固定文本 | `{"text": "你好，${name}"}` |
| **run_command** | 执行系统命令 | `{"command": "ls", "args_from": "path"}` |
| **http_request** | 发送 HTTP 请求 | `{"url": "...", "method": "POST"}` |
| **plugin** | 调用 Python 插件 | `{"function": "my_handler"}` |
| **state_jump** | 仅状态跳转 | `{"target": "next_state"}` |
| **output** | 传出数据 | `{"output_key": "data", "format": "json"}` |
| **none** | 无处理器 | - |

### 3. 数据模型示例

**命令定义 (`CommandDefinition`)**
```python
{
    "id": "search",
    "description": "搜索文件",
    "parameters_schema": {"query": "str"},
    "has_return": true,
    "wait_for_return": false,
    "handler": { "type": "http_request", "config": {...} }
}
```

**系统反馈 (`SystemFeedback`)**
```python
{
    "current_state": {...},
    "event_history": [...],  # 最多 100 条
    "data_payload": null,
    "disclosed_commands": [...]
}
```

---

## 💻 CLI 使用指南

### 启动命令

| 命令 | 说明 | 示例 |
| :--- | :--- | :--- |
| `python3 cli.py` | 启动主菜单 | `cd src && python3 cli.py` |
| `python3 cli.py main` | 启动主菜单 | `cd src && python3 cli.py main` |
| `python3 cli.py run-single <path>` | 单窗口运行项目 | `python3 cli.py run-single ./projects/demo` |

### 主菜单功能
*   📁 **打开项目**: 列表选择或手动输入路径
*   ➕ **新建项目**: 默认目录或自定义路径
*   ⚙️ **系统设置**: 全局 API 配置 / 项目目录设置
*   ❌ **退出**: 关闭应用程序

### 项目内功能
*   ▶️ **运行**: 当前窗口运行 / 新窗口运行
*   📝 **命令管理**: 添加 / 编辑 / 删除
*   🗂️ **状态编排**: 添加 / 编辑 / 命令绑定 / 跳转配置
*   ⚙️ **项目配置**: API 配置 / 模型配置 / 项目信息

---

## 🔒 安全机制

| 机制 | 说明 |
| :--- | :--- |
| **命令 ID 验证** | 正则 `^[a-z][a-z0-9_]*$`，防止注入 |
| **深度限制** | 自由模式最多 5 层，防止无限嵌套 |
| **事件历史限制** | 最多 100 条，防止 Token 爆炸 |
| **配置分离** | 全局/项目级配置独立，支持多环境 |
| **打包清理** | 提供清理脚本，移除敏感数据 |

---

## 📦 打包与发布 (开发者)

本项目主要提供源码，如需自行打包可执行文件：

1.  **清理敏感数据**:
    ```bash
    python3 cleanup_for_package.py
    ```
2.  **删除缓存**:
    ```bash
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} +
    rm -rf .venv
    ```
3.  **执行打包**:
    ```bash
    ./package.sh
    ```
4.  **验证**:
    检查生成的压缩包或可执行文件。

---

## ❓ 常见问题 (FAQ)

| 问题 | 解决方案 |
| :--- | :--- |
| **Missing command** | 检查 `cli.py` 是否有 `@app.callback` 装饰器 |
| **JSON 解析错误** | 删除 `config.json` 和 `api_config.json` 后重启 |
| **命令 ID 验证失败** | 确保 ID 以小写字母开头，只含字母数字下划线 |
| **新窗口无法打开** | macOS 需允许 Terminal 的 AppleScript 权限 |
| **API 调用失败** | 检查 `api_config.json` 中 Key 和 URL 是否正确 |
| **程序启动后无响应** | 正常现象，程序已进入菜单界面等待用户选择 |
| **依赖安装失败** | 确保使用的是 Python 3.9+ 版本，并尝试 `pip install --upgrade pip` |

---

## 📄 依赖说明

**requirements.txt**:
```text
typer>=0.9.0
questionary>=2.0.0
pyyaml>=6.0
rich>=13.0.0
requests>=2.31.0
pydantic>=2.0.0
```

**安装**:
```bash
pip install -r requirements.txt
```

---

## 🤝 贡献与许可

### 贡献指南
我们欢迎贡献！请遵循标准的开源实践：
1.  Fork 本仓库
2.  创建功能分支
3.  提交包含您更改的 Pull Request

### 许可证
本项目采用 **MIT License** 许可。

### 联系方式
*   **作者**: ArXav
*   **邮箱**: eurexon@outlook.com
*   **仓库**: [https://github.com/ArXav/LX-AI-System.git](https://github.com/ArXav/LX-AI-System.git)
