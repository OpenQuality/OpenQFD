#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
#  OpenQFD软件 - Linux / macOS 一键部署脚本
#  用法: chmod +x setup_unix.sh && ./setup_unix.sh
# ═══════════════════════════════════════════════════════════════

set -e

APP_NAME="OpenQFD"
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$APP_DIR/.venv"
MAIN_PY="$APP_DIR/main.py"

echo ""
echo "============================================"
echo "  OpenQFD软件 - 部署脚本"
echo "============================================"
echo ""

# ── 1. Check Python ──────────────────────────────────────────────
echo "[1/5] 检测 Python 环境..."
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+')
        major=$(echo "$ver" | cut -d. -f1)
        minor=$(echo "$ver" | cut -d. -f2)
        if [ "$major" -eq 3 ] && [ "$minor" -ge 10 ]; then
            PYTHON="$cmd"
            echo "  ✓ 找到: $("$cmd" --version)"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "  ✗ 未找到 Python 3.10+"
    echo ""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  macOS 安装方式:"
        echo "    brew install python@3.12"
    else
        echo "  Linux 安装方式:"
        echo "    Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
        echo "    Fedora:        sudo dnf install python3"
        echo "    Arch:          sudo pacman -S python"
    fi
    exit 1
fi

# ── 2. Create virtual environment ────────────────────────────────
echo "[2/5] 创建虚拟环境..."
if [ ! -d "$VENV_DIR" ]; then
    "$PYTHON" -m venv "$VENV_DIR"
    echo "  ✓ 虚拟环境创建完成"
else
    echo "  ✓ 虚拟环境已存在"
fi

# ── 3. Install dependencies ──────────────────────────────────────
echo "[3/5] 安装依赖包..."
"$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt" -q 2>/dev/null || \
"$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt" -q -i "https://pypi.tuna.tsinghua.edu.cn/simple" 2>/dev/null
echo "  ✓ 依赖安装完成"

# ── 4. Create launcher script ────────────────────────────────────
echo "[4/5] 创建启动脚本..."
LAUNCHER="$APP_DIR/qfd.sh"
cat > "$LAUNCHER" << LAUNCHER_EOF
#!/usr/bin/env bash
cd "$APP_DIR"
exec "$VENV_DIR/bin/python" main.py "\$@"
LAUNCHER_EOF
chmod +x "$LAUNCHER"
echo "  ✓ 启动脚本: $LAUNCHER"

# ── 5. Create desktop entry (Linux) / alias (macOS) ──────────────
echo "[5/5] 创建桌面快捷方式..."
ICON_PATH="$APP_DIR/assets/icon_256.png"

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS: create a small .app wrapper
    APP_BUNDLE="$HOME/Desktop/$APP_NAME.command"
    cat > "$APP_BUNDLE" << MACOS_EOF
#!/usr/bin/env bash
cd "$APP_DIR"
exec "$VENV_DIR/bin/python" main.py
MACOS_EOF
    chmod +x "$APP_BUNDLE"
    echo "  ✓ macOS 桌面启动器: $APP_BUNDLE"
else
    # Linux: create .desktop file
    DESKTOP_FILE="$HOME/Desktop/$APP_NAME.desktop"
    mkdir -p "$HOME/Desktop"
    cat > "$DESKTOP_FILE" << DESKTOP_EOF
[Desktop Entry]
Name=$APP_NAME
Comment=Quality Function Deployment
Exec=$LAUNCHER
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Office;Engineering;
StartupWMClass=qfd
DESKTOP_EOF
    chmod +x "$DESKTOP_FILE"
    # Also install to applications menu
    APPS_DIR="$HOME/.local/share/applications"
    mkdir -p "$APPS_DIR"
    cp "$DESKTOP_FILE" "$APPS_DIR/"
    echo "  ✓ 桌面快捷方式已创建"
    echo "  ✓ 应用菜单项已添加"
fi

# ── Done ─────────────────────────────────────────────────────────
echo ""
echo "============================================"
echo "  ✅ 部署完成!"
echo "============================================"
echo ""
echo "  启动方式:"
echo "    1. 双击桌面快捷方式"
echo "    2. 或运行: $LAUNCHER"
echo "    3. 或运行: $VENV_DIR/bin/python $MAIN_PY"
echo ""
