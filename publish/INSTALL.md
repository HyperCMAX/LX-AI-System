# LX-AI Installation Guide

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