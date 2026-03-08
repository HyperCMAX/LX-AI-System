# LX-AI 系统 - 完整文件目录与技术文档

**版本**: 1.3  
**作者**: ArXav (eurexon@outlook.com)  
**许可证**: MIT License  
**分发方式**: 源代码分发 | 可执行文件 (macOS arm64)

---

## 📖 项目概述

**LX-AI 系统** 是一个基于状态驱动的 AI 指令披露框架，专为与大型语言模型（LLMs）交互而设计。它通过状态机管理命令集的可见性，实现安全、可控的 AI 交互，提供全面的 AI 驱动交互和数据管理解决方案。

### ✨ v1.3 新特性

| 特性 | 说明 |
| :--- | :--- |
| **🎯 智能状态跳转** | state_jump 处理器支持自动注册，无需手动配置 command_transitions |
| **🔄 返回值追踪** | 完整的返回值生命周期管理（pending/waiting/completed） |
| **⏱️ 超时机制** | 自动清理超时返回值，防止资源泄漏 |
| **📊 三重优先级** | 显式配置 > 自动注册 > 默认行为的灵活控制机制 |

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

### 对 Mac/Linux 用户，可选择快速配置-直接使用 Unix执行文件 [LX_AI](dist/LX_AI)
### 对 开发者/其他 用户，项目以**源代码形式**分发，需配置 Python 环境后运行

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

```
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

| 类型 | 说明 | 配置示例 | 返回值 | 副作用 |
| :--- | :--- | :--- | :--- | :--- |
| **echo** | 返回固定文本 | `{"text": "你好，${name}"}` | str | ❌ 无 |
| **run_command** | 执行系统命令 | `{"command": "ls", "args_from": "path"}` | str | ❌ 无 |
| **http_request** | 发送 HTTP 请求 | `{"url": "...", "method": "POST"}` | str | ❌ 无 |
| **plugin** | 调用 Python 插件 | `{"function": "my_handler"}` | any | ❌ 无 |
| **state_jump** ⭐ | 状态跳转 | `{"target": "next_state"}` | str | ✅ 有 |
| **output** | 传出数据 | `{"output_key": "data", "format": "json"}` | dict | ❌ 无 |
| **none** | 无处理器 | - | - | ❌ 无 |

> 💡 **注意**：只有 `state_jump` 处理器具有系统级副作用（改变状态机状态），采用双层控制机制（处理器层 + 配置层）。从 v1.3 开始支持自动注册机制。

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

## 🔄 返回值追踪机制 (v1.3+)

### 返回值类型

| 类型 | 说明 | 触发方式 | 示例 |
| :--- | :--- | :--- | :--- |
| **自动返回值** | HTTP 请求、系统命令执行后自动捕获 | `has_return=true` | API 响应数据 |
| **手动返回值** | 等待用户输入 | `wait_for_user` 处理器 | 用户确认信息 |
| **外部返回值** | 监控文件系统获取 | `wait_for_external` 处理器 | `.return` 文件 |

### 返回值状态生命周期

```
pending → waiting → completed/timeout
   ↓         ↓           ↓
 创建     等待中      完成/超时
```

### CLI 使用返回值

```bash
# 查看所有等待中的返回值
returns

# 提交返回值（索引从 1 开始）
return 1 success

# 查看返回值历史
returns --history
```

### 超时机制

- 默认超时时间：300 秒（5 分钟）
- 超时后自动清理，避免资源泄漏
- 可通过 `command_timeout` 配置自定义

### 编程接口

```python
# 获取所有等待中的返回值
pending = controller.get_pending_returns()

# 获取完整的返回值历史
history = controller.get_return_history()

# 清理已完成的返回值
controller.clear_completed_returns()
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

### macOS arm64 可执行文件

从 v1.3 开始，项目提供预编译的 macOS arm64 可执行文件（11MB），无需 Python 环境即可运行：

```bash
# 直接运行
./dist/LX_AI main

# 查看帮助
./dist/LX_AI --help
```

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
| **state_jump 不跳转** | ✅ v1.3+ 已修复，支持自动注册机制 |
| **返回值未提交给 AI** | 检查 `has_return` 和 `wait_for_return` 配置 |
| **返回值超时** | 调整 `command_timeout` 配置或使用 `returns` 命令查看状态 |

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
*   **仓库**: [https://github.com/HyperCMAX/LX-AI-System.git](https://github.com/HyperCMAX/LX-AI-System.git)

---

## 📊 版本历史

### v1.3 (2026-03-09) - 当前版本

**✨ 新特性：**
- ✅ 实现完整的返回值追踪机制（pending/waiting/completed）
- ✅ state_jump 处理器支持自动注册（三层优先级）
- ✅ 超时机制自动清理返回值
- ✅ 添加 get_pending_returns/get_return_history/clear_completed_returns 方法

**🐛 修复：**
- ✅ 修复 state_jump 缺少 command_transitions 时不跳转的问题
- ✅ 优化处理器注册逻辑，支持显式配置优先 + 自动 fallback
- ✅ 改进类型提示和边界条件处理

**📝 文档：**
- ✅ 更新 README 说明处理器行为特征
- ✅ 添加返回值追踪使用指南
- ✅ 完善双层控制机制说明

**🔧 技术改进：**
- ✅ 所有 6 种处理器类型测试通过
- ✅ PyInstaller 打包优化（11MB）
- ✅ 向后兼容旧配置文件

### v1.2

**功能：**
- 添加返回值追踪基础功能
- 优化 CLI 交互体验
- 改进项目管理系统

### v1.1

**功能：**
- 初始稳定版本
- 状态驱动架构
- 双模式支持（stable/free）
