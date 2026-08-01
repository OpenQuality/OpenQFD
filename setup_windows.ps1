# OpenQFD - Windows Deployment Script (PowerShell)
# Right-click -> Run with PowerShell
# Or: PowerShell -ExecutionPolicy Bypass -File setup_windows.ps1

$ErrorActionPreference = "Stop"
$APP_NAME = "OpenQFD"
$APP_DIR  = Split-Path -Parent $MyInvocation.MyCommand.Path
$VENV_DIR = Join-Path $APP_DIR ".venv"
$MAIN_PY  = Join-Path $APP_DIR "main.py"
$ICON     = Join-Path $APP_DIR "assets\qfd.ico"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  OpenQFD - Windows Auto Deployment" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# -- 1. Check Python --
Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.(\d+)") {
            $minor = [int]$Matches[1]
            if ($minor -ge 10) {
                $pythonCmd = $cmd
                Write-Host "  OK: $ver" -ForegroundColor Green
                break
            }
        }
    } catch {}
}
if (-not $pythonCmd) {
    Write-Host "  ERROR: Python 3.10+ not found" -ForegroundColor Red
    Write-Host "  Download: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  IMPORTANT: Check 'Add Python to PATH' during install" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# -- 2. Create virtual environment --
Write-Host "[2/5] Creating virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path $VENV_DIR)) {
    & $pythonCmd -m venv $VENV_DIR
    Write-Host "  OK: venv created" -ForegroundColor Green
} else {
    Write-Host "  OK: venv already exists" -ForegroundColor Green
}

# -- 3. Install dependencies --
Write-Host "[3/5] Installing dependencies..." -ForegroundColor Yellow
$pip = Join-Path $VENV_DIR "Scripts\pip.exe"
& $pip install -r (Join-Path $APP_DIR "requirements.txt") -q 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Trying China mirror..." -ForegroundColor Yellow
    & $pip install -r (Join-Path $APP_DIR "requirements.txt") -q -i "https://pypi.tuna.tsinghua.edu.cn/simple" 2>$null
}
Write-Host "  OK: dependencies installed" -ForegroundColor Green

# -- 4. Create launchers --
Write-Host "[4/5] Creating launchers..." -ForegroundColor Yellow

$pythonw = Join-Path $VENV_DIR "Scripts\pythonw.exe"

# BAT launcher
$batPath = Join-Path $APP_DIR "OpenQFD.bat"
$batLines = @(
    "@echo off",
    "cd /d `"$APP_DIR`"",
    "call `".venv\Scripts\activate.bat`"",
    "start `"`" pythonw main.py"
)
[IO.File]::WriteAllLines($batPath, $batLines, [Text.Encoding]::GetEncoding(936))
Write-Host "  OK: OpenQFD.bat" -ForegroundColor Green

# VBS silent launcher (no console window)
$vbsPath = Join-Path $APP_DIR "OpenQFD.vbs"
$vbsLines = @(
    "Set WshShell = CreateObject(""WScript.Shell"")",
    "WshShell.CurrentDirectory = ""$APP_DIR""",
    "WshShell.Run """"$pythonw"""" """"$MAIN_PY"""""", 0, False"
)
[IO.File]::WriteAllLines($vbsPath, $vbsLines, [Text.Encoding]::GetEncoding(936))
Write-Host "  OK: OpenQFD.vbs (silent)" -ForegroundColor Green

# -- 5. Create desktop shortcut --
Write-Host "[5/5] Creating desktop shortcut..." -ForegroundColor Yellow
try {
    $desktop = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = Join-Path $desktop "$APP_NAME.lnk"
    $WScriptShell = New-Object -ComObject WScript.Shell
    $shortcut = $WScriptShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "wscript.exe"
    $shortcut.Arguments = """$vbsPath"""
    $shortcut.WorkingDirectory = $APP_DIR
    if (Test-Path $ICON) {
        $shortcut.IconLocation = $ICON
    }
    $shortcut.Description = "OpenQFD"
    $shortcut.Save()
    Write-Host "  OK: Desktop shortcut created" -ForegroundColor Green
} catch {
    Write-Host "  WARN: Shortcut failed, use OpenQFD.vbs instead" -ForegroundColor Yellow
}

# -- Done --
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  DONE! Deployment complete." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  How to launch:" -ForegroundColor Cyan
Write-Host "    1. Double-click desktop '$APP_NAME' shortcut" -ForegroundColor White
Write-Host "    2. Or double-click OpenQFD.vbs" -ForegroundColor White
Write-Host "    3. Or run: .venv\Scripts\python.exe main.py" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
