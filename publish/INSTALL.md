# LX-AI 安装指南

## 方法一：使用预构建可执行文件（推荐）

1. 下载最新发布的安装包
2. 解压ZIP归档文件
3. 进入解压后的目录：
   ```bash
   cd LX_AI_Installer
   ```

4. 使可执行文件可运行（首次运行时）：
   ```bash
   chmod +x LX_AI
   ```

5. 运行应用程序：
   ```bash
   ./LX_AI
   ```

## 方法二：从源码安装

1. 确保已安装Python 3.9+：
   ```bash
   python3 --version
   ```

2. 克隆仓库：
   ```bash
   git clone https://github.com/ArXav/LX-AI-System.git
   cd LX-AI-System
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 直接运行应用程序：
   ```bash
   cd src
   python cli.py
   ```

## Prerequisites

No prerequisites needed! LX-AI is distributed as a standalone executable that contains all necessary dependencies.

## Installation Steps

### macOS

1. Download the `LX_AI_Installer.zip` file from the releases page
2. Extract the ZIP archive by double-clicking on it
3. Open Terminal and navigate to the extracted folder:
   ```bash
   cd /path/to/extracted/folder
   ```
   Or simply open the extracted folder in Finder, right-click on it, select "Services" > "New Terminal at Folder" (if you have this service enabled)
   
4. Make the executable file runnable (only required once):
   ```bash
   chmod +x LX_AI
   ```

5. Run the application:
   ```bash
   ./LX_AI
   ```

Alternatively, you can run the application by double-clicking the `LX_AI` file in Finder, but this may not display command-line prompts properly.

## Troubleshooting

### "Operation not permitted" or "Permission denied"

Run the chmod command to grant execution permissions:
```bash
chmod +x LX_AI
```

### "LX_AI cannot be opened because the developer cannot be verified"

On macOS, you may see a security warning. To resolve this:
1. Go to System Preferences > Security & Privacy
2. Click on the "General" tab
3. Click the lock icon and authenticate with your admin credentials
4. Under "Allow apps downloaded from:", select "App Store and identified developers" or "Anywhere"
5. Try running the application again

Alternatively, you can allow the app to run by executing:
```bash
xattr -d com.apple.quarantine ./LX_AI
```

## Getting Started

Once the application runs successfully, you'll see an interactive menu with options to:
- Open an existing project
- Create a new project
- Configure system settings
- Exit the application

Navigate using the arrow keys and press Enter to select an option.