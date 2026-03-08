# LX-AI: Large Language Model Application Framework

LX-AI is an advanced application framework designed for interacting with large language models (LLMs), providing a comprehensive solution for AI-powered interactions and data management.

## Features

- **Multi-model Support**: Compatible with various LLM providers including OpenAI GPT series, Claude, Gemini, and locally deployed models.
- **Interactive CLI Interface**: User-friendly command-line interface for seamless interactions.
- **Conversation Management**: Sophisticated conversation history tracking and management.
- **Data Persistence**: Robust local storage of conversations and configurations.
- **Flexible Configuration**: Easy API key and preference configuration.

## Installation

There are two ways to use LX-AI:

### Method 1: Using Pre-built Installer (Recommended)

Download the appropriate installer for your platform:

- **Mac Users**: Download [LX_AI_Mac_Installer.zip](LX_AI_Mac_Installer.zip)
  - Extract the ZIP file
  - Navigate to the extracted folder and double-click on the LX_AI executable to run the application

### Method 2: From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/HyperCMAX/LX-AI-System.git
   cd LX-AI-System
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:

```bash
cd src
python cli.py
```

Or execute the packaged binary:

```bash
cd src
./LX_AI
```

## Building from Source

To rebuild the executable:

```bash
cd src
python setup.py build
```

The executable will be created in a subdirectory under [src](file:///Users/hypercmax/Documents/Project/LX/src/core/__init__.py).

## Contributing

We welcome contributions! Please follow standard open-source practices:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with your changes

## License

This project is licensed under the MIT License - see the [LICENSE](file:///Users/hypercmax/Documents/Project/LX/LICENSE) file for details.

## Contact

Author: ArXav
Email: eurexon@outlook.com

# LX AI 系统 - 完整文件目录与技术文档

作者：ArXav (eurexon@outlook.com)
---
要是想直接用的话就下载[src/LX_AI](https://github.com/HyperCMAX/LX-AI-System/blob/main/src/LX_AI)
## 📁 完整文件目录结构

```
LX/
├── src/                              # 源代码目录
│   ├── LX_AI                         # UNIX可执行文件
│   ├── cli.py                        # 主程序入口（CLI 界面）
│   ├── frozen_application_license.txt # 打包许可证文件
│   ├── lib/                          # 打包依赖库目录
│   ├── share/                        # 打包共享资源目录
│   └── core/                         # 核心模块
│       ├── config.py                 # 系统配置常量
│       ├── models.py                 # 数据模型定义
│       ├── registry.py               # 命令注册中心
│       ├── state_machine.py          # 状态机管理
│       ├── message_protocol.py       # 通讯协议定义
│       ├── prompt_templates.py       # 提示词模板
│       ├── parser.py                 # 响应解析器
│       ├── executor.py               # 命令执行器
│       ├── logger.py                 # 事件日志器
│       ├── controller.py             # 系统控制器
│       ├── config_manager.py         # 配置管理器
│       ├── project_manager.py        # 项目管理器
│       ├── project_loader.py         # 项目加载器
│       └── command_handlers.py       # 命令处理器
├── projects/                         # 项目存储目录
│   └── [项目名]/                     # 每个项目独立文件夹
│       ├── project.yaml              # 状态和命令编排
│       ├── config.json               # 项目级 API 配置
│       └── handlers.py               # 自定义插件
├── api_config.json                   # 全局 API 配置
├── config.json                       # 全局配置（项目列表等）
├── requirements.txt                  # Python 依赖列表
├── README.md                         # 项目说明
├── .gitignore                        # Git 忽略文件
├── cleanup_for_package.py            # 清理脚本（打包前使用）
├── package.sh                        # 打包脚本
└── setup.py                          # 项目打包配置
```

---

## 📄 项目技术文档

---

### 1. 项目概述

**LX AI 系统** 是一个基于状态驱动的 AI 指令披露框架，通过状态机管理命令集的可见性，实现安全、可控的 AI 交互。

#### 核心特性

| 特性         | 说明                         |
| :--------- | :------------------------- |
| **状态驱动**   | 命令集根据当前状态动态披露              |
| **双模式支持**  | 稳定模式（预设）+ 自由模式（AI 动态生成）    |
| **双对象交互**  | 面向用户（自然语言）+ 面向系统（结构化命令）    |
| **项目制管理**  | 每个项目独立配置，支持自定义路径           |
| **命令处理器**  | 支持 echo、HTTP、系统命令、插件、数据输出等 |
| **CLI 界面** | 交互式命令行管理工具                 |

---

### 2. 核心架构

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

---

### 3. 模块说明

#### 3.1 核心模块 ([`src/core/`](file:///Users/hypercmax/Documents/Project/LX/src/core/__init__.py))

| 模块       | 文件                    | 功能                         |
| :------- | :-------------------- | :------------------------- |
| **配置**   | [`config.py`](file:///Users/hypercmax/Documents/Project/LX/src/core/config.py)           | 系统常量（正则、深度限制、历史长度）         |
| **模型**   | [`models.py`](file:///Users/hypercmax/Documents/Project/LX/src/core/models.py)           | Pydantic 数据模型（命令、状态、事件、反馈） |
| **注册**   | [`registry.py`](file:///Users/hypercmax/Documents/Project/LX/src/core/registry.py)         | 命令注册与查询                    |
| **状态**   | [`state_machine.py`](file:///Users/hypercmax/Documents/Project/LX/src/core/state_machine.py)    | 状态流转、深度计算、命令披露             |
| **协议**   | [`message_protocol.py`](file:///Users/hypercmax/Documents/Project/LX/src/core/message_protocol.py) | LLM 输入输出数据结构               |
| **提示词**  | [`prompt_templates.py`](file:///Users/hypercmax/Documents/Project/LX/src/core/prompt_templates.py) | 系统提示词模板                    |
| **解析**   | [`parser.py`](file:///Users/hypercmax/Documents/Project/LX/src/core/parser.py)           | LLM 输出解析与验证                |
| **执行**   | [`executor.py`](file:///Users/hypercmax/Documents/Project/LX/src/core/executor.py)         | 命令执行与结果返回                  |
| **日志**   | [`logger.py`](file:///Users/hypercmax/Documents/Project/LX/src/core/logger.py)           | 系统事件记录（滑动窗口）               |
| **控制器**  | [`controller.py`](file:///Users/hypercmax/Documents/Project/LX/src/core/controller.py)       | 核心编排（状态 + 命令+LLM）          |
| **配置管理** | [`config_manager.py`](file:///Users/hypercmax/Documents/Project/LX/src/core/config_manager.py)   | 全局配置读写                     |
| **项目管理** | [`project_manager.py`](file:///Users/hypercmax/Documents/Project/LX/src/core/project_manager.py)  | 项目创建、打开、保存                 |
| **项目加载** | [`project_loader.py`](file:///Users/hypercmax/Documents/Project/LX/src/core/project_loader.py)   | 加载项目配置到系统                  |
| **命令处理** | [`command_handlers.py`](file:///Users/hypercmax/Documents/Project/LX/src/core/command_handlers.py) | 命令处理器（echo/HTTP/插件等）       |

#### 3.2 入口模块 ([`src/`](file:///Users/hypercmax/Documents/Project/LX/src/core/__init__.py))

| 文件       | 功能               |
| :------- | :--------------- |
| `LX_AI`  | 打包好的UNIX可执行文件    |
| `frozen_application_license.txt` | 打包许可证文件 |
| `lib/`   | 打包依赖库目录 |
| `share/` | 打包共享资源目录 |
| [`cli.py`](file:///Users/hypercmax/Documents/Project/LX/src/cli.py) | 主程序入口，交互式 CLI 界面 |

---

### 4. 数据模型

#### 4.1 命令定义 (`CommandDefinition`)

```python
{
    "id": "search",                    # 命令 ID（小写字母 + 数字 + 下划线）
    "description": "搜索文件",          # 命令描述
    "parameters_schema": {"query": "str"},  # 参数定义
    "has_return": true,                # 是否有返回值
    "wait_for_return": false,          # 是否等待返回值
    "handler": {                       # 处理器配置（可选）
        "type": "http_request",
        "config": {"url": "...", "method": "POST"}
    }
}
```

#### 4.2 状态节点 (`StateNode`)

```python
{
    "id": "root",                      # 状态 ID
    "description": "主菜单",            # 状态描述
    "mode": "stable",                  # 模式：stable / free
    "parent_id": null,                 # 父状态 ID（支持嵌套）
    "available_command_ids": ["help", "search"],  # 可用命令
    "command_transitions": {           # 命令跳转映射
        "search": "search_state"
    }
}
```

#### 4.3 系统反馈 (`SystemFeedback`)

```python
{
    "current_state": {...},            # 当前状态
    "event_history": [...],            # 事件历史（最多 100 条）
    "data_payload": null,              # 命令返回数据
    "disclosed_commands": [...]        # 当前可用命令列表
}
```

#### 4.4 模型动作 (`ModelAction`)

```python
{
    "thought": "用户想搜索文件",        # 模型思考过程
    "action_type": "call_command",     # 动作类型
    "response_to_user": "正在搜索...", # 给用户的回复
    "command_id": "search",            # 要执行的命令
    "command_params": {"query": "..."} # 命令参数
}
```

---

### 5. 命令处理器类型

| 类型                | 说明           | 配置示例                                       |
| :---------------- | :----------- | :----------------------------------------- |
| **echo**          | 返回固定文本       | `{"text": "你好，${name}"}`                   |
| **run\_command**  | 执行系统命令       | `{"command": "ls", "args_from": "path"}`   |
| **http\_request** | 发送 HTTP 请求   | `{"url": "...", "method": "POST"}`         |
| **plugin**        | 调用 Python 插件 | `{"function": "my_handler"}`               |
| **state\_jump**   | 仅状态跳转        | `{"target": "next_state"}`                 |
| **output**        | 传出数据         | `{"output_key": "data", "format": "json"}` |
| **none**          | 无处理器         | -                                          |

---

### 6. 配置文件说明

#### 6.1 全局 API 配置 (`api_config.json`)

```json
{
    "api": {
        "key": "",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo"
    }
}
```

#### 6.2 全局配置 (`config.json`)

```json
{
    "last_project": "/path/to/project",
    "projects": ["/path/to/project1", "/path/to/project2"]
}
```

#### 6.3 项目配置 (`projects/项目名/project.yaml`)

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

#### 6.4 项目级 API 配置 (`projects/项目名/config.json`)

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

### 7. CLI 命令说明

| 方式    | 命令                                 | 说明                | 示例                                          |
| :---- | :--------------------------------- | :---------------- | :------------------------------------------ |
| 源码    | `python3 cli.py`                   | 启动主菜单             | -                                           |
| 源码    | `python3 cli.py main`              | 启动主菜单             | -                                           |
| 源码    | `python3 cli.py run-single <path>` | 单窗口运行项目           | `python3 cli.py run-single ./projects/demo` |
| 可执行文件 | `./LX_AI`                          | 启动主菜单（无需Python环境） | -                                           |
| 可执行文件 | `./LX_AI main`                     | 启动主菜单（无需Python环境） | -                                           |

**主菜单功能**：
- 📁 打开项目（列表选择 / 手动输入路径）
- ➕ 新建项目（默认目录 / 自定义路径）
- ⚙️ 系统设置（全局 API 配置 / 项目目录设置）
- ❌ 退出

**项目内功能**：
- ▶️ 当前窗口运行 / 🪟 新窗口运行
- 📝 命令管理（添加 / 编辑 / 删除）
- 🗂️ 状态编排（添加 / 编辑 / 命令绑定 / 跳转配置）
- ⚙️ 项目配置（API 配置 / 模型配置 / 项目信息）

---

### 8. 运行模式

#### 8.1 稳定模式 (`stable`)

- 命令集预设，不可动态更改
- 适用于固定业务流程（如支付、审批）
- 状态跳转由 `command_transitions` 配置

#### 8.2 自由模式 (`free`)

- 架构师 AI 动态生成状态描述和命令集
- 适用于探索性任务（如调研、创意）
- 深度限制：最多 5 层嵌套

---

### 9. 安全机制

| 机制           | 说明                          |
| :----------- | :-------------------------- |
| **命令 ID 验证** | 正则 `^[a-z][a-z0-9_]*$`，防止注入 |
| **深度限制**     | 自由模式最多 5 层，防止无限嵌套           |
| **事件历史限制**   | 最多 100 条，防止 Token 爆炸        |
| **配置分离**     | 全局/项目级配置独立，支持多环境            |
| **打包清理**     | 提供清理脚本，移除敏感数据               |

---

### 10. 依赖说明

**requirements.txt**:
```
questionary>=2.1.0
typer>=0.24.0
cx_Freeze>=8.6.0
prompt_toolkit>=3.0.0
rich>=14.3.0
PyYAML>=6.0
requests>=2.32.0
pydantic>=2.12.0
```

**安装**:
```bash
pip install -r requirements.txt
```

---

### 11. 快速开始

```bash
# 1. 源码方式：安装依赖
pip install -r requirements.txt

# 2. 源码方式：启动 CLI
cd src
python3 cli.py

# 或者直接运行可执行文件（无需安装Python环境）
cd src
chmod +x LX_AI
./LX_AI
```

---

### 12. 重要说明

**关于程序运行行为**：
- `cli.py` 是一个交互式程序，运行后会进入菜单界面等待用户输入
- 当您运行 `python src/cli.py` 或 `./src/LX_AI` 时，程序正常启动会显示主菜单选项
- 要退出程序，可以在菜单中选择"❌ 退出"选项
- 如果程序正常显示菜单（如："📁 打开项目", "➕ 新建项目", "⚙️ 系统设置", "❌ 退出"），则表示程序运行正常

---

### 13. 安装包发布

我们现在提供 Mac 和 Windows 平台的安装包，用户可以直接下载已构建好的安装包进行安装，无需配置 Python 环境或处理源码文件。

#### 13.1 Mac 安装包

Mac 用户可直接下载位于项目根目录的安装包：[LX_AI_Mac_Installer.dmg](file:///Users/hypercmax/Documents/Project/LX/LX_AI_Mac_Installer.dmg)。下载后双击打开，并将应用程序拖拽至 `Applications` 文件夹即可完成安装。

#### 13.2 Windows 安装包

Windows 用户可直接下载位于 `dist/` 目录下的可执行文件：[LX_AI_Windows.exe](file:///Users/hypercmax/Documents/Project/LX/dist/LX_AI_Windows.exe)。下载后直接运行该文件即可启动 LX AI 系统。

---

### 14. 常见问题

| 问题                  | 解决方案                                     |
| :------------------ | :--------------------------------------- |
| **Missing command** | 检查 `cli.py` 是否有 `@app.callback` 装饰器      |
| **JSON 解析错误**       | 删除 `config.json` 和 `api_config.json` 后重启 |
| **命令 ID 验证失败**      | 确保 ID 以小写字母开头，只含字母数字下划线                  |
| **新窗口无法打开**         | macOS 需允许 Terminal 的 AppleScript 权限      |
| **API 调用失败**        | 检查 `api_config.json` 中 Key 和 URL 是否正确    |
| **程序启动后无响应**        | 这是正常的，程序已进入菜单界面等待用户选择                    |
| **UNIX 可执行文件无法运行**  | 确保文件具有可执行权限 (`chmod +x src/LX_AI`)       |

---

---

**文档版本**: 1.1  
作者：ArXav (eurexon@outlook.com)
