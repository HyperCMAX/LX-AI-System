# LX_AI 打包版使用说明

## 📦 安装说明

### 1. 文件位置
- **可执行文件**: `dist/LX_AI` (11MB)
- **配置文件模板**: `api_config.json.template`

### 2. 设置执行权限（首次使用）
```bash
chmod +x dist/LX_AI
```

## 🚀 快速开始

### 方式一：直接运行
```bash
cd /Users/hypercmax/Documents/Project/LX/dist
./LX_AI
```

### 方式二：从任意位置运行
```bash
/Users/hypercmax/Documents/Project/LX/dist/LX_AI
```

### 方式三：添加到 PATH（可选）
```bash
# 将路径添加到 ~/.zshrc 或 ~/.bash_profile
export PATH="/Users/hypercmax/Documents/Project/LX/dist:$PATH"

# 然后就可以在任何地方直接运行
LX_AI
```

## ⚙️ 首次配置

### 1. 启动应用后，选择"系统设置"
### 2. 配置全局 API：
- **API Key**: 输入你的 OpenAI API 密钥
- **Base URL**: 默认为 `https://api.openai.com/v1`
- **模型名称**: 默认为 `gpt-3.5-turbo`

### 3. 配置文件保存位置：
- **全局配置**: `~/.lx_ai/config.json`
- **项目配置**: `<项目目录>/config.json`

## 📋 主要功能

### 主菜单命令：
- **📁 打开项目**: 从列表选择或手动输入路径
- **➕ 新建项目**: 创建新的 AI 项目
- **⚙️  系统设置**: 配置 API 和项目目录
- **❌ 退出**: 退出应用

### 项目内功能：
- **▶️  当前窗口运行**: 在当前终端窗口运行项目
- **🪟 新窗口运行**: 在新的 Terminal 窗口运行项目（已修复打包版本）
- **📝 命令管理**: 添加、编辑、删除命令
- **🗂️  状态编排**: 管理状态和流程
- **⚙️  项目配置**: 配置项目信息和 API

## 🔧 技术细节

### 打包信息
- **打包工具**: PyInstaller 6.19.0
- **Python 版本**: 3.9.6
- **平台**: macOS ARM64
- **文件大小**: ~11MB
- **打包日期**: 2026-03-08

### 包含的依赖
- typer (CLI 框架)
- questionary (交互式菜单)
- rich (富文本输出)
- pydantic (数据验证)
- pyyaml (YAML 解析)
- requests (HTTP 请求)
- core 模块（所有核心组件）

### 已知警告（不影响功能）
```
urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+
requests/__init__.py:86: RequestsDependencyWarning: Unable to find acceptable character detection dependency
```

这些警告可以安全忽略，不影响应用功能。

## ✅ 已修复的问题

### 新窗口运行功能（v2 版本）
**问题**：打包后的可执行文件无法正确调用 `.py` 文件路径

**解决方案**：
- 添加了运行时环境检测（`sys.frozen`）
- 打包环境下直接使用 `sys.executable` 作为可执行文件
- 开发环境下使用 `python cli.py` 方式运行
- macOS AppleScript 命令已适配两种模式

**测试方法**：
```bash
# 测试主程序
./LX_AI

# 测试子命令
./LX_AI run-single /path/to/project

# 在 GUI 中测试新窗口运行
# 1. 打开项目
# 2. 选择"🪟 新窗口运行"
# 3. 应能正常打开新 Terminal 窗口并运行项目
```

## 🛠️ 重新打包

如需重新打包，在项目根目录运行：
```bash
python3 build.py
```

打包产物将生成在 `dist/` 目录。

## 📞 技术支持

如有问题，请联系：
- 用户：ArXav
- 邮箱：eurexon@outlook.com
- 项目位置：`/Users/hypercmax/Documents/Project/LX`

---

*最后更新时间：2026-03-08*
