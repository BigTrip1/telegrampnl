@echo off
setlocal enabledelayedexpansion
:: Set UTF-8 encoding for proper emoji display
chcp 65001 >nul 2>&1
color 0A
title PNL Trading Bot - Python Terminal

:: Ensure this opens in a new dedicated terminal window
if not "%1"=="NEWWINDOW" (
    start "PNL Trading Bot - Python Terminal" /max cmd /k "%~f0" NEWWINDOW
    exit /b
)

echo.
echo ===============================================================
echo.
echo     🏛️  PNL TRADING BOT - PYTHON TERMINAL  ⚔️
echo.
echo     Complete Trading Analytics + Epic Battle System
echo     Running in dedicated Python environment
echo.
echo ===============================================================
echo.

:: Set working directory to script location
cd /d "%~dp0"

:: Show Python environment info
echo.
echo 🐍 PYTHON TERMINAL ENVIRONMENT 🐍
echo Working Directory: %CD%
echo.
python --version 2>nul || echo Python: Not detected (will be checked below)
echo.

echo [1/6] 🔍 Checking System Requirements...
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python detected
python --version

echo.
echo [2/6] 📦 Installing/Updating Dependencies...
echo.

:: First, update pip to latest version
echo Updating pip to latest version...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo ⚠️  Pip update failed, continuing with current version...
) else (
    echo ✅ Pip updated successfully
)

echo.
echo Installing required packages...

:: Try normal installation first
pip install -r requirements.txt --upgrade --quiet
if errorlevel 1 (
    echo ⚠️  Standard installation failed, trying alternative methods...
    echo.
    
    :: Try with --force-reinstall to handle conflicts
    echo Attempting force reinstall...
    pip install -r requirements.txt --upgrade --force-reinstall --quiet
    if errorlevel 1 (
        echo ⚠️  Force reinstall failed, trying user installation...
        
        :: Try user installation to avoid permission issues
        pip install -r requirements.txt --upgrade --user --quiet
        if errorlevel 1 (
            echo ❌ All installation methods failed
            echo.
            echo This might be due to:
            echo   • Permission issues with Python installation
            echo   • Package conflicts
            echo   • Network connectivity problems
            echo.
            echo 💡 SOLUTIONS:
            echo   1. CONTINUING ANYWAY - Bot might work with existing packages
            echo   2. Use manual installer: Double-click MANUAL_INSTALL_DEPENDENCIES.bat
            echo   3. Or install manually: pip install -r requirements.txt --user
            echo.
        ) else (
            echo ✅ Dependencies installed using user directory
        )
    ) else (
        echo ✅ Dependencies installed using force reinstall
    )
) else (
    echo ✅ All dependencies installed/updated successfully
)
echo.

echo [3/6] 🗄️ Testing Database Connection...
echo.

:: Test database connection
python -c "from database import DatabaseManager; db = DatabaseManager(); result = db.connect(); print('✅ Database connected successfully' if result else '❌ Database connection failed'); db.close_connection()" 2>nul
if errorlevel 1 (
    echo ⚠️  Database connection test failed
    echo Starting MongoDB service...
    
    :: Try to start MongoDB service
    net start MongoDB >nul 2>&1
    if errorlevel 1 (
        echo ❌ Could not start MongoDB service
        echo.
        echo Please ensure MongoDB is installed and configured
        echo Or check your database configuration in database.py
        echo.
        echo Continuing anyway... (bot will show connection status)
    ) else (
        echo ✅ MongoDB service started
    )
)

echo.
echo [4/6] ⚙️ Verifying Bot Configuration...
echo.

:: Check if main bot file exists
if not exist "telegram_bot.py" (
    echo ❌ ERROR: telegram_bot.py not found!
    echo.
    echo Please make sure you're in the correct directory
    pause
    exit /b 1
)

echo ✅ Bot files verified
echo.

echo [5/6] 🚀 Checking Bot Token...
echo.

:: Quick syntax check
python -m py_compile telegram_bot.py
if errorlevel 1 (
    echo ❌ ERROR: Bot code has syntax errors
    echo.
    echo Please check telegram_bot.py for issues
    pause
    exit /b 1
)

echo ✅ Bot code syntax verified
echo.

echo [6/6] 🏛️ Starting PNL Trading Bot...
echo.
echo ===============================================================
echo.
echo        🎯 STARTING COMPLETE PNL + BATTLE SYSTEM 🎯
echo.
echo ===============================================================
echo.
echo Features Available:
echo   📊 Complete PNL Analytics (49+ commands)
echo   ⚔️ Epic Gladiator Battle System
echo   🏆 Battle Points ^& Leaderboards
echo   📸 Auto Photo Detection
echo   🔄 Real-time Battle Monitoring
echo   🏛️ Multi-channel Posting
echo.
echo Commands Ready:
echo   • /submit - Submit trades with screenshots
echo   • /profitbattle - Start profit battles
echo   • /tradewar - Start trade count battles
echo   • /battlerules - Battle system guide
echo   • /leaderboard - View rankings
echo   • /mystats - Personal analytics
echo   • +43 more commands available!
echo.
echo ===============================================================
echo.
echo 🎺 THE ARENA IS READY! Press Ctrl+C to stop the bot
echo.
echo ===============================================================
echo.

:: Start the bot
python telegram_bot.py

:: If bot stops, show exit message
echo.
echo ===============================================================
echo.
echo        🛑 PNL TRADING BOT STOPPED 🛑
echo.
echo ===============================================================
echo.

:: Check exit code
if errorlevel 1 (
    echo ❌ Bot exited with errors
    echo.
    echo Common issues:
    echo   • Invalid bot token in configuration
    echo   • Network connectivity problems
    echo   • Database connection issues
    echo   • Python package conflicts
    echo.
    echo Check the error messages above for details.
    echo.
) else (
    echo ✅ Bot exited cleanly
    echo.
    echo Thank you for using the PNL Trading Bot!
    echo.
)

echo.
echo ===============================================================
echo.
echo 💡 TIP: This Python terminal will stay open for you to:
echo    • View any error messages
echo    • Run manual Python commands
echo    • Restart the bot easily
echo.
echo 🔄 To restart the bot: Just run this file again
echo 🐍 To use Python directly: Type "python" and press Enter
echo 🔚 To close this terminal: Type "exit" or close the window
echo.
echo ===============================================================
echo.
echo Python terminal ready for your commands...
echo. 