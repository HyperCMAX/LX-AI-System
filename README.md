# LX-AI 系统 - 完整文件目录与技术文档

**版本**: 1.2  
**作者**: ArXav (eurexon@outlook.com)  
**许可证**: MIT License  
**分发方式**: 源代码分发 / 可执行文件分发

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
| **对话历史管理** | 💬 完整的对话历史保存与加载，支持多对话切换 |
| **多窗口运行** | 🪟 支持同时打开多个对话窗口，并行处理任务 |
| **上下文控制** | 📏 可配置的上下文长度（1-50 轮），平衡效果与成本 |
| **打包分发** | 📦 支持打包为独立可执行文件，无需 Python 环境 |

---

## 🚀 快速开始

本项目提供**源代码**和**可执行文件**两种分发方式。

### 方式一：使用可执行文件（推荐）

#### macOS
```
# 下载后直接运行
./LX_AI
```

#### Windows
``cmd
# 双击 LX_AI.exe 或在命令行运行
LX_AI.exe
```

#### Linux
```bash
# 赋予执行权限后运行
chmod +x LX_AI
./LX_AI
```

### 方式二：源代码运行

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

### 初始配置

1.  **配置全局 API**: 在主菜单选择 `⚙️ 系统设置` → `🔑 全局 API 配置`，输入 API Key、Base URL 和模型名称。
2.  **新建项目**: 在主菜单选择 `📁 打开项目` → `➕ 新建项目`，输入项目名称并选择保存位置。
3.  **运行项目**: 打开项目后，选择 `💬 对话管理` → `➕ 新建对话`，然后选择打开方式（当前窗口/新窗口）。

---

## 💡 新增功能（v1.2）

### 1. 对话历史管理 💬

**功能说明**：
- ✅ 自动保存对话历史到本地 JSON 文件
- ✅ 支持多个项目独立管理对话
- ✅ 支持多个对话随时切换
- ✅ 显示对话消息数量和更新时间

**使用方法**：
```bash
# 在项目中选择"💬 对话管理"
# - 新建对话：输入对话名称（可选），选择打开方式
# - 打开对话：从列表选择已有对话
# - 删除对话：选择不需要的对话并确认
```

**存储位置**：
```
projects/
└── 项目名/
    └── conversations/
        ├── 20240308_123456.json    # 对话 1
        ├── 20240308_134527.json    # 对话 2
        └── ...
```

### 2. 多窗口并行运行 🪟

**功能说明**：
- ✅ 支持同时打开多个对话窗口
- ✅ 每个窗口独立运行，互不干扰
- ✅ 适合多任务并行处理场景

**使用方法**：
1. 在对话管理中创建或选择对话
2. 选择"🪟 新窗口打开"
3. 系统自动在新 Terminal 窗口启动对话
4. 原窗口可继续操作其他项目或对话

**技术实现**：
- macOS: 使用 AppleScript 控制 Terminal
- Windows: 使用 `start` 命令创建新进程组
- Linux: 手动打开多个终端

### 3. 上下文长度控制 📏

**功能说明**：
- ✅ 可配置保留最近 N 轮对话（1-50 轮）
- ✅ 平衡对话质量与 API Token 消耗
- ✅ 全局统一配置，所有项目共享

**配置方法**：
```bash
# 在主菜单选择：
⚙️ 系统设置 → 📏 上下文长度 → 输入数值（如 10）
```

**推荐设置**：
- 简单问答：3-5 轮
- 复杂任务：10-20 轮
- 深度研究：30-50 轮

### 4. 打包优化与分发 📦

**改进内容**：
- ✅ 完全移除相对导入问题
- ✅ 自动包含所有核心模块
- ✅ 支持跨平台打包（macOS/Windows/Linux）
- ✅ 生成的可执行文件无需 Python 环境

**打包步骤**：
```bash
# 1. 清理旧文件
rm -rf build dist

# 2. 执行打包
python3 build.py

# 3. 验证产物
ls -lh dist/LX_AI
```

**分发包内容**：
```
dist/
├── LX_AI              # macOS 可执行文件
├── LX_AI.exe          # Windows 可执行文件
└── api_config.json.template  # API 配置模板
```

---

## 📁 完整文件目录结构

```
LX/
├── README.md                         # 项目说明文档
├── setup.py                          # Python 包安装脚本
├── build.py                          # PyInstaller 打包脚本
├── lx_ai.spec                        # PyInstaller 配置文件
├── .gitignore                        # Git 忽略配置
│
├── src/                              # 源代码目录
│   ├── cli.py                        # 主程序入口（CLI 界面）
│   ├── core/                         # 核心模块
│   │   ├── command_handlers.py       # 命令处理器
│   │   ├── config_manager.py         # 配置管理器
│   │   ├── config.py                 # 系统配置常量
│   │   ├── controller.py             # 系统控制器
│   │   ├── executor.py               # 命令执行器
│   │   ├── logger.py                 # 事件日志器
│   │   ├── message_protocol.py       # 通讯协议定义
│   │   ├── models.py                 # 数据模型定义
│   │   ├── parser.py                 # 响应解析器
│   │   ├── project_loader.py         # 项目加载器
│   │   ├── project_manager.py        # 项目管理器（含对话管理）
│   │   ├── prompt_templates.py       # 提示词模板
│   │   ├── registry.py               # 命令注册中心
│   │   └── state_machine.py          # 状态机管理
│   └── projects/                     # 项目存储目录（含对话历史）
│
└── dist/                             # 打包产物目录
    ├── LX_AI                         # macOS 可执行文件
    ├── LX_AI.exe                     # Windows 可执行文件
    └── api_config.json.template      # API 配置模板
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
| `./LX_AI` | 运行打包后的可执行文件 | `./dist/LX_AI` |
| `python3 cli.py` | 启动主菜单（源码模式） | `cd src && python3 cli.py` |
| `python3 cli.py run-single <path>` | 单窗口运行项目 | `python3 cli.py run-single ./projects/demo` |
| `python3 cli.py run-single <path> <conv_id>` | 打开指定对话 | `python3 cli.py run-single ./projects/demo 20240308_123456` |

### 主菜单功能
*   📁 **打开项目**: 列表选择或手动输入路径
*   ⚙️ **系统设置**: 
    - 🔑 全局 API 配置（Key/URL/Model）
    - 📏 上下文长度设置（1-50 轮）
*   ❌ **退出**: 关闭应用程序

### 项目内功能
*   💬 **对话管理**: 
    - ➕ 新建对话（支持自定义名称）
    - 🗑️ 删除对话
    - 🪟 新窗口打开 / ▶️ 当前窗口打开
*   📝 **命令管理**: 添加 / 编辑 / 删除命令
*   🗂️ **状态编排**: 添加 / 编辑 / 命令绑定 / 跳转配置
*   ⚙️ **项目配置**: API 配置 / 模型配置 / 项目信息

### 对话管理操作流程

```bash
# 1. 打开项目后进入对话管理
💬 对话管理

# 2. 新建对话
➕ 新建对话 → 输入对话名称（可选）→ 选择打开方式：
   - 🪟 新窗口打开（并行处理多任务）
   - ▶️ 当前窗口打开（单任务）
   - ❌ 暂不打开（稍后处理）

# 3. 打开已有对话
选择对话 → 选择打开方式：
   - 🪟 新窗口打开
   - ▶️ 当前窗口打开

# 4. 删除对话
🗑️ 删除对话 → 选择对话 → 确认删除

# 5. 退出对话
输入 "exit" 或 "quit" → 自动保存对话历史
```

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
| **新窗口无法打开** | macOS 需允许 Terminal 的 AppleScript 权限（系统偏好设置 → 安全性与隐私 → 隐私 → AppleScript） |
| **API 调用失败** | 检查 `api_config.json` 中 Key 和 URL 是否正确 |
| **程序启动后无响应** | 正常现象，程序已进入菜单界面等待用户选择 |
| **依赖安装失败** | 确保使用的是 Python 3.9+ 版本，并尝试 `pip install --upgrade pip` |
| **对话加载失败** | 检查 `projects/项目名/conversations/` 目录下对话文件是否存在 |
| **打包后导入错误** | 确保使用最新版的 `lx_ai.spec` 配置文件，并已执行 `rm -rf build dist` 清理缓存 |
| **上下文长度不生效** | 在系统设置中修改后需重启程序，或手动编辑 `~/.lx_ai/config.json` |

---

## 🔄 版本历史

### v1.2 (2024-03) - 新增功能
- ✅ **对话历史管理**: 完整的对话保存、加载、删除功能
- ✅ **多窗口并行运行**: 支持同时打开多个对话窗口
- ✅ **上下文长度控制**: 可配置保留最近 N 轮对话（1-50 轮）
- ✅ **打包优化**: 完全移除相对导入问题，支持跨平台分发
- ✅ **run-single 子命令**: 支持命令行直接打开指定项目和对话
- ✅ **GUI 改进**: 优化对话管理界面，添加打开方式选择

### v1.1 (2024-02) - 初始发布
- ✅ 状态驱动架构实现
- ✅ 双模式支持（稳定/自由）
- ✅ 项目制管理
- ✅ CLI 交互式界面
- ✅ 命令处理器系统
- ✅ LLM 集成（架构师 + 执行者双模型）

---

## 📄 依赖说明

**requirements.txt**:
```
typer>=0.9.0
questionary>=2.0.0
pyyaml>=6.0
rich>=13.0.0
requests>=2.31.0
pydantic>=2.0.0
PyInstaller>=6.0.0  # 打包工具（可选，仅开发者需要）
```

**安装**:
```
# 基础运行环境
pip install -r requirements.txt

# 或包含打包工具
pip install typer questionary pyyaml rich requests pydantic pyinstaller
```

---

## 🛠️ 开发者指南

### 本地开发

```bash
# 1. 克隆仓库
git clone https://github.com/ArXav/LX-AI-System.git
cd LX-AI-System

# 2. 创建虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行程序
cd src
python3 cli.py
```

### 打包发布

```bash
# 1. 清理敏感数据和缓存
rm -rf build dist
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# 2. 执行打包
python3 build.py

# 3. 验证产物
ls -lh dist/
./dist/LX_AI --help

# 4. 分发
# - macOS: dist/LX_AI
# - Windows: dist/LX_AI.exe
# - Linux: dist/LX_AI (需测试)
```

### 添加新功能

#### 添加命令处理器

在 `src/core/command_handlers.py` 中添加：

```python
class MyCustomHandler(BaseCommandHandler):
    def execute(self, params: Dict[str, Any]) -> str:
        # 实现自定义逻辑
        return "处理结果"
```

#### 添加系统设置项

在 `cli.py` 的 `settings_menu()` 函数中添加：

```python
Choice("🎨 新增功能", "new_feature")
```

然后处理逻辑：

```python
elif choice == "new_feature":
    # 实现新功能配置
    pass
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

### 代码规范
- 使用 Python 类型注解
- 遵循 PEP 8 代码风格
- 为新增功能编写文档
- 确保所有测试通过

### 许可证
本项目采用 **MIT License** 许可。

### 联系方式
*   **作者**: ArXav
*   **邮箱**: eurexon@outlook.com
*   **仓库**: [https://github.com/ArXav/LX-AI-System.git](https://github.com/ArXav/LX-AI-System.git)
*   **问题反馈**: 请在 GitHub Issues 中提交

---

## 📊 项目统计

| 指标 | 数值 |
| :--- | :--- |
| **核心模块** | 14 个 Python 文件 |
| **代码行数** | ~2000+ 行 |
| **支持平台** | macOS / Windows / Linux |
| **Python 版本** | 3.9+ |
| **依赖数量** | 6 个核心库 |
| **打包体积** | ~11MB (macOS ARM64) |

---

## 🎯 路线图

### v1.3 计划（开发中）
- [ ] Web UI 界面（基于 Gradio/Streamlit）
- [ ] 数据库支持（SQLite/PostgreSQL）
- [ ] 插件市场系统
- [ ] API 服务端模式
- [ ] Docker 容器化部署

### 未来愿景
- [ ] 可视化状态编排器
- [ ] 多模型自动切换
- [ ] 对话分析与统计
- [ ] 团队协作功能
- [ ] 云端同步服务

---

**感谢使用 LX-AI 系统！** 🎉
