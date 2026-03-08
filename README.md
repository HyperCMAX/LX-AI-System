# LX-AI 系统 - 完整文件目录与技术文档

**版本**: 1.2  
**作者**: ArXav (eurexon@outlook.com)  
**许可证**: MIT License  
**分发方式**: 预编译可执行文件分发

---

## 📖 项目概述

**LX-AI 系统** 是一个基于状态驱动的 AI 指令披露框架，专为与大型语言模型（LLMs）交互而设计。它通过状态机管理命令集的可见性，实现安全、可控的 AI 交互，提供全面的 AI 驱动交互和数据管理解决方案。

### 核心特性

| 特性 | 说明 |
| :--- | :--- |
| **状态驱动** | 命令集根据当前状态动态披露，确保交互可控 |
| **双模式支持** | **稳定模式**（预设流程）+ **自由模式**（AI 动态生成） |
| **双对象交互** | 面向用户（自然语言）+ 面向系统（结构化命令） |
| **项目制管理** | 每个项目独立配置，支持自定义路径与插件 |
| **交互式 CLI** | 用户友好的命令行界面，无缝交互体验 |
| **数据持久化** | 稳健的本地对话历史与配置存储 |
| **返回值追踪** | 完整的 HTTP/API 返回值等待与超时处理机制 |
| **并发返回管理** | 支持多个命令同时等待返回值，独立追踪状态 |
| **CLI 配置分离** | CLI 展示信息与 AI 模型数据完全隔离 |

---

## 🚀 快速开始

### 方式一：使用预编译可执行文件（推荐）

1. **下载安装包**：从发布页面下载对应系统的 ZIP 压缩包
2. **解压并设置权限**（Mac/Linux）：
   ```bash
   unzip LX_AI_mac.zip
   chmod +x LX_AI
   ```
3. **运行程序**：
   ```bash
   ./LX_AI
   ```

### 方式二：源代码运行（开发者）

#### 1. 环境要求

确保已安装 **Python 3.9+**。

```bash
python3 --version
```

#### 2. 安装依赖

克隆仓库后，在项目根目录安装所需依赖：

```bash
pip install -r requirements.txt
```

#### 3. 运行程序

进入 `src` 目录并启动 CLI 主程序：

```bash
cd src
python3 cli.py
```

*注：程序启动后进入菜单界面，选择"❌ 退出"可关闭程序。*

#### 4. 初始配置

1. **配置全局 API**: 在主菜单选择 `⚙️ 系统设置` → `全局 API 配置`，输入 API Key、Base URL 和模型名称。
2. **设置超时时间**: 在 `⚙️ 系统设置` → `命令超时时间` 中设置返回值等待超时（默认 30 秒）。
3. **新建项目**: 在主菜单选择 `➕ 新建项目`，输入项目名称并选择保存位置。
4. **运行项目**: 打开项目后，选择 `💬 对话管理` → `新建对话` 开始交互。

---

## 📁 完整文件目录结构

```
LX/
├── README.md                         # 项目说明文档
├── PACKAGING_README.md               # 打包版说明文档
├── requirements.txt                  # Python 依赖列表
├── build.py                          # PyInstaller 打包脚本
├── setup.py                          # Python 包安装脚本
├── publish/                          # 发布目录
│   ├── INSTALL.md                    # 安装说明
│   ├── LX_AI                         # 可执行文件（发布版）
│   └── README.md                     # 发布版说明
└── src/                              # 源代码目录
    ├── cli.py                        # 主程序入口（CLI 界面）
    ├── core/                         # 核心模块
    │   ├── __init__.py               # 包初始化
    │   ├── command_handlers.py       # 命令处理器（HTTP/命令/插件等）
    │   ├── config_manager.py         # 配置管理器（全局 + 项目级）
    │   ├── config.py                 # 系统配置常量
    │   ├── controller.py             # 系统控制器（核心编排）
    │   ├── executor.py               # 命令执行器
    │   ├── logger.py                 # 事件日志器
    │   ├── message_protocol.py       # 通讯协议定义
    │   ├── models.py                 # 数据模型定义（Pydantic）
    │   ├── parser.py                 # LLM 响应解析器
    │   ├── project_loader.py         # 项目加载器（YAML 解析）
    │   ├── project_manager.py        # 项目管理器（CRUD 操作）
    │   ├── prompt_templates.py       # 提示词模板
    │   ├── registry.py               # 命令注册中心
    │   └── state_machine.py          # 状态机管理
    └── projects/                     # 项目存储目录（运行时生成）
        └── <项目名>/
            ├── project.yaml          # 状态和命令编排
            ├── config.json           # 项目级 API 配置（可选）
            ├── handlers.py           # 自定义 Python 插件（可选）
            └── conversations/        # 对话历史目录
                ├── <对话 ID>.json    # 对话记录
                └── returns/          # 外部返回值文件（可选）
```

---

## 🏗 核心架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户界面 (CLI)                           │
│   - 项目管理  - 对话管理  - 命令配置  - 状态编排  - 系统设置      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        系统控制器                                │
│                    (SystemController)                           │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│   状态机    │   命令注册   │   命令执行   │   返回值追踪        │
│ StateMachine│  Registry   │  Executor   │  Return Tracker     │
└─────────────┴─────────────┴─────────────┴─────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        LLM 集成层                                │
│              (架构师 AI + 执行者 AI 双模型)                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        外部系统                                  │
│   - HTTP API  - 系统命令  - Python 插件  - 文件回调              │
└─────────────────────────────────────────────────────────────────┘
```

### 核心模块说明

| 模块 | 文件 | 功能描述 |
| :--- | :--- | :--- |
| **配置** | `core/config.py` | 系统常量定义（正则、深度限制、历史长度） |
| **模型** | `core/models.py` | Pydantic 数据模型（CommandDefinition, StateNode, SystemFeedback 等） |
| **注册** | `core/registry.py` | 命令注册与查询，统一管理所有可执行命令 |
| **状态** | `core/state_machine.py` | 状态流转、深度计算、命令披露控制 |
| **协议** | `core/message_protocol.py` | LLM 输入输出数据结构定义（ModelAction, ModelActionType） |
| **提示词** | `core/prompt_templates.py` | 系统提示词模板生成（含返回值状态说明） |
| **解析** | `core/parser.py` | LLM JSON 输出解析与验证 |
| **执行** | `core/executor.py` | 命令执行调度与结果返回 |
| **日志** | `core/logger.py` | 系统事件记录（滑动窗口，最多 100 条） |
| **控制器** | `core/controller.py` | 核心编排（状态机 + 命令注册 + 命令执行 +LLM+ 返回值追踪） |
| **项目管理** | `core/project_manager.py` | 项目创建、打开、保存、对话管理 |
| **项目加载** | `core/project_loader.py` | YAML 项目配置解析与应用到控制器 |
| **命令处理** | `core/command_handlers.py` | 命令处理器实现（echo/http_request/run_command/plugin/wait 等） |

---

## ⚙️ 配置说明

### 1. 全局 API 配置 (`~/.lx_ai/api_config.json`)
```json
{
    "api": {
        "key": "YOUR_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo"
    }
}
```

### 2. 全局系统配置 (`~/.lx_ai/config.json`)
```json
{
    "last_project": "/Users/hypercmax/.lx_ai/projects/A",
    "projects": [
        "/Users/hypercmax/.lx_ai/projects/A",
        "/Users/hypercmax/.lx_ai/projects/B"
    ],
    "context_length": 5,
    "command_timeout": 30
}
```

### 3. 项目配置 (`projects/<项目名>/project.yaml`)
```yaml
project:
  name: "客服助手"
  version: "1.0"
  created: "2024-01-01T00:00:00"
  updated: "2024-01-01T00:00:00"

initial_state: "root"

commands:
  - id: "help"
    description: "显示帮助信息"
    return_settings:
      has_return: false
      wait_for_return: false
    handler:
      type: "echo"
      config:
        text: "欢迎使用客服助手"
  
  - id: "search"
    description: "搜索外部数据"
    return_settings:
      has_return: true
      wait_for_return: false
    handler:
      type: "http_request"
      config:
        url: "https://api.example.com/search"
        method: "GET"
        timeout: 30

states:
  - id: "root"
    description: "主菜单"
    mode: "stable"
    parent_id: null
    available_commands: ["help", "search"]
    command_transitions:
      search: "search_state"

  - id: "search_state"
    description: "搜索结果展示"
    mode: "stable"
    parent_id: "root"
    available_commands: ["back", "detail"]
    command_transitions:
      back: "root"
```

### 4. 项目级 API 配置 (`projects/<项目名>/config.json`)
项目可独立配置 API，覆盖全局设置。如不存在则使用全局配置。
```json
{
    "api": {
        "key": "",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo"
    }
}
```

### 5. 对话历史 (`projects/<项目名>/conversations/<对话 ID>.json`)
```json
{
    "id": "20260309_120000",
    "name": "对话 20260309_120000",
    "created": "2026-03-09T12:00:00",
    "updated": "2026-03-09T12:30:00",
    "messages": [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！有什么可以帮你的？"}
    ],
    "context_length": 5
}
```

---

## 🛠 功能详解

### 1. 运行模式

| 模式 | 说明 | 适用场景 |
| :--- | :--- |
| **稳定模式 (stable)** | 命令集预设，不可动态更改。状态跳转由 `command_transitions` 配置。 | 固定业务流程（如支付、审批、客服流程） |
| **自由模式 (free)** | 架构师 AI 动态生成状态描述和命令集。深度限制最多 5 层。 | 探索性任务（如调研、创意、数据分析） |

### 2. 处理器类型

| 类型 | 处理器 | 说明 | 返回值行为 |
| :--- | :--- | :--- |
| **回复类** | `echo` | 返回固定文本或模板消息 | 自动返回 |
| **系统类** | `state_jump` | 执行状态跳转 | 自动返回 |
| **外部请求类** | `http_request` | HTTP/HTTPS API 调用 | 自动返回 HTTP 响应 |
| **外部请求类** | `run_command` | 执行系统 Shell 命令 | 自动返回 stdout/stderr |
| **外部请求类** | `plugin` | 调用 Python 插件函数 | 可配置自动/手动返回 |
| **数据输出类** | `output` | 向外部系统传递结构化数据 | 自动返回 |
| **等待类** | `wait_for_user` | 等待用户输入返回值 | 手动返回 |
| **等待类** | `wait_for_external` | 等待外部文件回调返回值 | 手动返回 |

### 3. 返回值设置（CLI 配置界面）

在 CLI 的命令配置界面中，可为每个命令设置返回值参数：

| 设置项 | 选项 | 说明 |
| :--- | :--- | :--- |
| **是否有返回值** | 是/否 | 命令执行后是否产生返回值（对应 `has_return`） |
| **返回值类型** | 自动/手动 | 自动：HTTP/命令输出；手动：用户输入/外部回调 |
| **是否等待返回值** | 是/否 | AI 是否需要等待返回值后再回复用户（对应 `wait_for_return`） |

**注意**：CLI 配置中的 `processor_category` 字段仅用于前端分类显示，不会传递给 AI 模型。

### 4. 返回值状态流转

| 状态 | 触发条件 | 显示给 AI | 显示次数 | 后续处理 |
| :--- | :--- | :--- | :--- | :--- |
| **等待中 (pending)** | `has_return=true, wait_for_return=false` | ✅ 是 | 每次都显示 | 继续追踪 |
| **阻塞等待 (waiting)** | `has_return=true, wait_for_return=true` | ✅ 是 | 每次都显示 | 阻塞用户输入 |
| **已返回 (completed)** | 收到返回值 | ✅ 是 | 只通知一次 | 清理出待处理队列 |
| **已超时 (timeout)** | 超过 `command_timeout` 秒无返回 | ✅ 是 | 只通知一次 | 清理出待处理队列 |

### 5. 数据模型示例

**命令定义 (`CommandDefinition`)** - AI 可见的数据结构
```python
{
    "id": "search",
    "description": "搜索文件",
    "parameters_schema": {"query": {"type": "string", "description": "搜索关键词"}},
    "has_return": true,
    "wait_for_return": false
}
```

**系统反馈 (`SystemFeedback`)** - 每次用户输入时构建的上下文
```python
{
    "current_state": {
        "id": "root",
        "description": "主菜单",
        "mode": "stable"
    },
    "event_history": [
        {"type": "success", "message": "Command help executed", "cmd_id": "help"}
    ],  # 最多 100 条
    "data_payload": null,
    "disclosed_commands": [
        {"id": "help", "description": "显示帮助", ...},
        {"id": "search", "description": "搜索文件", ...}
    ]  # 仅当前状态可用命令
}
```

**返回值状态（附带在用户输入中发送给 AI）**
```text
[系统返回值状态]
  [等待中] search: 已等待 10 秒/30 秒
  [已返回] query: HTTP 200: {"status": "success", "data": [...]}
  [已超时] notify: 超过 30 秒无返回值
```

---

## 💻 CLI 使用指南

### 启动命令

| 命令 | 说明 | 示例 |
| :--- | :--- | :--- |
| `./LX_AI` | 启动主菜单 | 预编译版本 |
| `python3 cli.py` | 启动主菜单 | `cd src && python3 cli.py` |
| `python3 cli.py run-single <path>` | 单窗口运行项目 | `python3 cli.py run-single ./projects/demo` |
| `python3 cli.py run-single <path> --conv <id>` | 打开指定对话 | `python3 cli.py run-single ./projects/A --conv 20260309_120000` |

### 主菜单功能

| 功能 | 说明 |
| :--- | :--- |
| 📁 **打开项目** | 从最近项目列表选择或手动输入路径打开 |
| ➕ **新建项目** | 使用默认目录或自定义路径创建新项目 |
| ⚙️ **系统设置** | 全局 API 配置 / 上下文长度 / 命令超时时间 / 项目目录管理 |
| ❌ **退出** | 关闭应用程序 |

### 项目内功能

| 功能模块 | 子功能 |
| :--- | :--- |
| 💬 **对话管理** | 新建对话 / 查看对话列表 / 删除对话 / 打开对话（当前窗口/新窗口） |
| 📝 **命令管理** | 添加命令 / 编辑命令 / 删除命令 / 配置处理器 / 设置返回值参数 |
| 🗂️ **状态编排** | 添加状态 / 编辑状态 / 绑定可用命令 / 配置命令跳转关系 |
| ⚙️ **项目配置** | API 配置（覆盖全局） / 项目信息查看 |

### 运行中命令（单窗口模式）

| 命令 | 说明 | 示例 |
| :--- | :--- | :--- |
| `exit` / `quit` | 退出当前对话，保存历史记录 | `exit` |
| `history` | 查看当前对话历史（最近 10 条） | `history` |
| `returns` | 查看所有等待中的返回值状态 | `returns` |
| `return <command_id> <值>` | 手动提交返回值 | `return cmd_123 {"status":"ok"}` |
| `clear` | 清理已完成的返回值记录 | `clear` |

---

## 🔒 安全机制

| 机制 | 说明 |
| :--- | :--- |
| **命令 ID 验证** | 正则 `^[a-z][a-z0-9_-]*$`，防止注入攻击，自动转小写兼容 |
| **深度限制** | 自由模式最多 5 层，防止无限嵌套导致 Token 爆炸 |
| **事件历史限制** | 最多 100 条滑动窗口，防止上下文过长 |
| **配置分离** | 全局配置 (`~/.lx_ai/`) 与项目级配置 (`projects/*/`) 独立 |
| **命令披露控制** | AI 只能看到当前状态 `available_commands` 列表中的命令 |
| **返回值超时** | 可配置超时时间（默认 30 秒），防止无限等待 |
| **对话隔离** | 每个对话独立 JSON 文件存储，互不干扰 |
| **CLI 与 AI 数据隔离** | CLI 展示元数据（如 processor_category）不传递给 AI 模型 |

---

## 📦 打包与发布（开发者）

### 打包步骤

1. **清理敏感数据和缓存**:
   ```bash
   cd /Users/hypercmax/Documents/Project/LX
   
   # 删除 Python 缓存
   find . -name "*.pyc" -delete
   find . -name "__pycache__" -type d -exec rm -rf {} +
   
   # 删除构建产物
   rm -rf build dist *.egg-info src/*.egg-info
   
   # 删除虚拟环境（如有）
   rm -rf .venv venv
   ```

2. **执行打包**:
   ```bash
   python3 build.py
   ```
   
   或使用 PyInstaller 直接打包：
   ```bash
   pyinstaller --clean lx_ai.spec
   ```

3. **验证可执行文件**:
   ```bash
   # 测试帮助信息
   ./dist/LX_AI --help
   
   # 测试单项目运行
   ./dist/LX_AI run-single /Users/hypercmax/.lx_ai/projects/A
   ```

4. **清理构建产物**（保留最终可执行文件）:
   ```bash
   rm -rf build lx_ai.spec
   ls -lh dist/LX_AI
   ```

### 打包配置说明

**`build.py`** - 自动化打包脚本
- 创建临时 spec 文件
- 配置单文件模式（无 COLLECT）
- 包含所有隐藏导入（typer, questionary, rich, pydantic 等）
- 设置正确的模块搜索路径

**关键配置项**:
```python
# 单文件 EXE 模式（不生成额外目录）
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],  # 不包含 COLLECT
    name='LX_AI',
    console=True
)
```

### 打包产物

- **位置**: `dist/LX_AI`
- **大小**: 约 11MB（macOS ARM64）
- **权限**: `-rwxr-xr-x`（可执行）
- **依赖**: 无外部依赖（已打包 Python 解释器和所有库）

---

## ❓ 常见问题 (FAQ)

| 问题 | 解决方案 |
| :--- | :--- |
| **Missing command / CLI 启动报错** | 检查 `cli.py` 是否有 `@app.callback()` 装饰器，确保 Typer 版本 >= 0.9.0 |
| **JSON 解析错误** | 删除 `~/.lx_ai/config.json` 和 `api_config.json` 后重启程序 |
| **命令 ID 验证失败** | 确保 ID 以小写字母开头，只含字母、数字、下划线和连字符 |
| **新窗口无法打开（macOS）** | 系统偏好设置 → 安全性与隐私 → 隐私 → 自动化 → 允许 Terminal 控制 AppleScript |
| **API 调用失败** | 检查 `~/.lx_ai/api_config.json` 中 API Key、Base URL 和 Model 是否正确 |
| **程序启动后无响应** | 正常现象，程序已进入菜单界面等待用户选择 |
| **依赖安装失败** | 确保使用 Python 3.9+，尝试 `pip install --upgrade pip` 后重新安装 |
| **返回值状态不显示** | 确认命令配置中 `has_return=true`，检查超时设置是否过短 |
| **对话历史加载不全** | 检查 `conversations/` 目录下 JSON 文件格式是否正确，字段是否完整 |
| **CommandDefinition 字段错误** | 不要传递 `processor_category` 给 AI 模型，该字段仅用于 CLI 前端展示 |
| **打包后运行报错 ImportError** | 确保 spec 文件中包含所有 hiddenimports，特别是 `core.*` 模块 |
| **urllib3/SSL 警告** | 安装兼容版本：`pip install urllib3==1.26.15 chardet`（不影响功能） |

---

## 📄 依赖说明

**requirements.txt**:
```text
typer>=0.9.0              # CLI 框架
questionary>=2.0.0        # 交互式菜单
pyyaml>=6.0               # YAML 配置解析
rich>=13.0.0              # CLI 美化输出
requests>=2.31.0          # HTTP 请求库
pydantic>=2.0.0           # 数据模型验证
```

**安装命令**:
```bash
pip install -r requirements.txt
```

**可选依赖**（消除警告，不影响功能）:
```bash
pip install urllib3==1.26.15 chardet
```

---

## 🤝 贡献与许可

### 贡献指南
我们欢迎贡献！请遵循标准的开源实践：
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 许可证
本项目采用 **MIT License** 许可。详见 [LICENSE](LICENSE) 文件。

### 联系方式
*   **作者**: ArXav
*   **邮箱**: eurexon@outlook.com
*   **仓库**: [https://github.com/ArXav/LX-AI-System.git](https://github.com/ArXav/LX-AI-System.git)

---

## 📝 更新日志

### v1.2 (2026-03-09) - 返回值追踪与 CLI 配置分离
- ✅ **新增返回值追踪机制**：支持并发等待多个命令返回值
- ✅ **新增处理器分类**：回复类/系统类/外部请求类/数据输出类/等待类
- ✅ **新增返回值设置**：has_return / wait_for_return / return_type 三参数控制
- ✅ **新增对话历史管理**：查看/删除/刷新对话历史记录
- ✅ **新增命令超时配置**：系统设置中可调整返回值等待超时时间
- ✅ **修复打包后相对导入问题**：优化 spec 文件和模块路径配置
- ✅ **修复命令 ID 大小写兼容问题**：自动转小写，允许混合输入
- ✅ **优化 AI 可见命令过滤逻辑**：确保状态机只披露可用命令
- ✅ **优化返回值状态通知**：已完成/超时状态只通知一次，避免重复干扰
- ✅ **CLI 配置与 AI 模型数据隔离**：processor_category 仅用于前端展示

### v1.1 (2025-03-09) - 项目制管理与数据持久化
- ✅ **新增项目制管理**：支持多项目独立配置
- ✅ **新增对话历史持久化**：JSON 格式存储，支持上下文长度配置
- ✅ **新增新窗口运行功能**：支持同时打开多个对话窗口
- ✅ **新增上下文长度配置**：可调整发送给 AI 的历史消息数量

### v1.0 (2025-01-01) - 初始版本发布
- ✅ **状态驱动命令披露**：基于状态机控制命令可见性
- ✅ **稳定/自由双模式**：支持固定流程和动态探索两种交互模式
- ✅ **CLI 交互界面**：Typer + Questionary 实现友好用户界面
- ✅ **LLM 集成**：架构师 AI + 执行者 AI 双模型协作

---

**最后更新**: 2026-03-09  
**文档版本**: 1.2  
**当前状态**: ✅ 生产就绪（Production Ready）
