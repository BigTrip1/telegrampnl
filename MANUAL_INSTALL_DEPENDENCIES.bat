@echo off
setlocal enabledelayedexpansion
:: Set UTF-8 encoding for proper emoji display
chcp 65001 >nul 2>&1
color 0A
title Manual Dependency Installation

echo.
echo ===============================================================
echo.
echo     🛠️  MANUAL DEPENDENCY INSTALLATION  🛠️
echo.
echo     Use this if the main launcher fails to install packages
echo.
echo ===============================================================
echo.

:: Set working directory to script location
cd /d "%~dp0"

echo 🐍 Python Environment:
python --version
echo Working Directory: %CD%
echo.

echo 📦 Installing Dependencies Step by Step...
echo.

:: Update pip first
echo [1/4] Updating pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ❌ Pip update failed
) else (
    echo ✅ Pip updated successfully
)

echo.
echo [2/4] Installing core packages...
pip install python-telegram-bot==20.7
pip install pymongo
pip install requests
pip install python-dotenv
pip install pillow
pip install pytz

echo.
echo [3/4] Installing additional packages...
pip install matplotlib
pip install pandas
pip install asyncio
pip install aiohttp

echo.
echo [4/4] Installing any remaining packages...
pip install -r requirements.txt --user --no-deps

echo.
echo ===============================================================
echo.
echo 🎯 Installation Complete!
echo.
echo Now try running your main launcher:
echo   • Double-click LAUNCH_PNL_BOT.bat
echo   • Or run: python telegram_bot.py
echo.
echo ===============================================================
echo.
echo Press any key to close this window...
pause >nul 