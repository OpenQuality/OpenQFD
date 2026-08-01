# OpenQFD 质量功能展开软件 — 部署与卸载方案

---

## 一、手动部署

### 1.1 Windows 环境

#### 环境准备

- Python 3.10+（推荐 3.12）: https://www.python.org/downloads/
- **安装时务必勾选「Add Python to PATH」**

#### 方式 A — PowerShell（推荐）

```powershell
# 打开 PowerShell (Win+X → Windows PowerShell)
cd E:\apps\OpenQFD
python -m venv .venv
.venv\Scripts\Activate.ps1
# 如果提示执行策略错误:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
pip install -r requirements.txt
python main.py
```

#### 方式 B — CMD (命令提示符)

```cmd
cd /d E:\apps\OpenQFD
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python main.py
```

#### 方式 C — Git Bash

```bash
cd /e/apps/OpenQFD
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
python main.py
```

#### Windows 手动设置「双击启动」

手动部署完成后，在 OpenQFD 目录下创建 `OpenQFD.vbs` 文件（完全静默，无黑窗口）:

```vbs
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "E:\apps\OpenQFD"
WshShell.Run """E:\apps\OpenQFD\.venv\Scripts\pythonw.exe"" ""E:\apps\OpenQFD\main.py""", 0, False
```

> 将路径改为你的实际安装目录，然后右键 → 发送到 → 桌面快捷方式。

---

### 1.2 Linux 环境

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install python3 python3-venv python3-pip

# Fedora
sudo dnf install python3 python3-pip

# Arch
sudo pacman -S python python-pip

# 通用部署步骤
cd ~/OpenQFD
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

#### Linux 设置「双击启动」

```bash
# 创建启动脚本
cat > ~/OpenQFD/qfd.sh << 'EOF'
#!/usr/bin/env bash
cd "$(dirname "$0")"
exec .venv/bin/python main.py
EOF
chmod +x ~/OpenQFD/qfd.sh

# 创建桌面快捷方式
cat > ~/Desktop/OpenQFD.desktop << EOF
[Desktop Entry]
Name=OpenQFD
Exec=$HOME/OpenQFD/qfd.sh
Icon=$HOME/OpenQFD/assets/icon_256.png
Terminal=false
Type=Application
EOF
chmod +x ~/Desktop/OpenQFD.desktop
```

---

### 1.3 macOS 环境

```bash
brew install python@3.12          # 如未安装
cd ~/OpenQFD
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

#### macOS 设置「双击启动」

```bash
cat > ~/Desktop/OpenQFD.command << 'EOF'
#!/usr/bin/env bash
cd "$HOME/OpenQFD"
exec .venv/bin/python main.py
EOF
chmod +x ~/Desktop/OpenQFD.command
```

---

## 二、自动部署（一键脚本）

### 2.1 Windows 自动部署

```
操作步骤:
1. 解压 OpenQFD.zip 到目标位置 (如 E:\apps\OpenQFD)
2. 右键 setup_windows.ps1 → 使用 PowerShell 运行
3. 等待自动完成
4. 双击桌面「OpenQFD」图标启动
```

> 如果提示"禁止运行脚本"，先以管理员身份运行:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

脚本自动完成：检测Python → 创建虚拟环境 → 安装依赖 → 创建启动器 → 创建桌面快捷方式(带图标)

### 2.2 Linux / macOS 自动部署

```bash
unzip OpenQFD.zip && cd OpenQFD
chmod +x setup_unix.sh && ./setup_unix.sh
./qfd.sh
```

### 2.3 打包为独立可执行文件（无需 Python 环境）

**推荐：直接下载预编译版**，无需自己打包，见 [GitHub Releases](https://github.com/OpenQuality/OpenQFD/releases/latest)（提供 Windows / macOS / Linux 三平台一键运行包）。

**自行打包**（需在对应平台上执行，PyInstaller 不支持跨平台编译）：

```powershell
.venv\Scripts\Activate.ps1
pip install pyinstaller
python build_installer.py
# Windows → dist\OpenQFD.exe
# macOS   → dist\OpenQFD.app
# Linux   → dist\OpenQFD
```

---

## 三、卸载方案

### 3.1 各部署方式的卸载方法

| 部署方式 | 卸载操作 | 写注册表？ | 系统服务？ |
|----------|----------|:----------:|:----------:|
| 手动部署 (venv) | 删除 OpenQFD 文件夹 + 桌面快捷方式 | ❌ 否 | ❌ 否 |
| 自动部署脚本 | 同上 | ❌ 否 | ❌ 否 |
| PyInstaller .exe | 删除 .exe 文件 | ❌ 否 | ❌ 否 |

**所有部署方式均为绿色安装，不修改注册表、不安装系统服务、不创建开机启动项。**
**直接删除即可完成卸载。**

### 3.2 完整卸载步骤

#### Windows 完整卸载

```powershell
# 1. 删除程序目录
Remove-Item -Recurse -Force "E:\apps\OpenQFD"

# 2. 删除桌面快捷方式
Remove-Item "$env:USERPROFILE\Desktop\OpenQFD.lnk" -ErrorAction SilentlyContinue

# 3. (可选) 删除用户配置和授权数据
Remove-Item -Recurse -Force "$env:APPDATA\OpenQFD" -ErrorAction SilentlyContinue

# 4. (可选) 删除项目数据库 (如果在其他位置)
# 数据库文件 qfd_data.db 在程序目录内，第1步已删除
```

或者直接在文件管理器中删除以下内容:
- `E:\apps\OpenQFD\` 整个文件夹
- 桌面上的 `OpenQFD` 快捷方式
- `%APPDATA%\OpenQFD\` 文件夹（授权码和语言偏好，可选）

#### Linux 完整卸载

```bash
# 1. 删除程序目录
rm -rf ~/OpenQFD

# 2. 删除桌面快捷方式
rm -f ~/Desktop/OpenQFD.desktop
rm -f ~/.local/share/applications/OpenQFD.desktop

# 3. (可选) 删除用户配置
rm -rf ~/.config/OpenQFD
```

#### macOS 完整卸载

```bash
rm -rf ~/OpenQFD
rm -f ~/Desktop/OpenQFD.command
rm -rf ~/.config/OpenQFD
```

#### PyInstaller .exe 卸载

```
直接删除 .exe 文件即可。完全不涉及注册表和系统目录。
如需清除授权数据: 删除 %APPDATA%\OpenQFD\ 文件夹。
```

### 3.3 用户数据说明

| 文件/目录 | 位置 | 内容 | 删除影响 |
|-----------|------|------|----------|
| `qfd_data.db` | 程序目录内 | 所有项目数据 | 丢失所有QFD项目 |
| `%APPDATA%\OpenQFD\` (Win) | 用户目录 | 授权码 + 语言偏好 | 需重新激活 |
| `~/.config/OpenQFD/` (Linux/Mac) | 用户目录 | 同上 | 同上 |

> 建议卸载前先通过「报告与导出 → 导出项目数据(JSON)」备份重要项目。

---

## 四、部署验证

| 检查项 | 预期结果 |
|--------|----------|
| 首次启动 | 弹出语言选择与许可协议同意页面，勾选后方可进入软件 |
| 双击启动 | 窗口正常打开，标题栏显示 OpenQFD |
| 加载示例 | 菜单栏「文件 → 新建示例项目」，出现智能手表 QFD 数据 |
| HOQ 矩阵 | 质量屋七区一体化显示（含屋顶钻石格） |
| 中英切换 | 侧栏顶部 中/EN 分段按钮，点击后界面立即刷新切换语言（无需重启） |
| 帮助手册 | 菜单栏「帮助 → 帮助手册」，弹出帮助文档 |
| 授权激活 | 菜单栏「授权 → 授权管理」，输入授权码后界面立即刷新显示授权版（无需重启） |

---

## 五、常见问题

**Q: pip install 网络超时**
A: `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

**Q: PowerShell 提示"禁止运行脚本"**
A: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Q: Linux 上 PySide6 报 xcb 错误**
A: `sudo apt install libxcb-xinerama0 libxkbcommon-x11-0 libegl1`

**Q: 字体显示为方块**
A: Linux: `sudo apt install fonts-wqy-zenhei` / Windows/macOS 系统自带中文字体

**Q: .exe 运行后被杀毒软件拦截**
A: PyInstaller打包的程序可能触发误报，添加信任即可。程序完全安全开源。

---

## 六、授权说明

授权码通过云端服务在线验证，一码一机绑定。如需购买/申请授权码，请打开软件内「授权 → 授权管理」页面查看联系方式。
