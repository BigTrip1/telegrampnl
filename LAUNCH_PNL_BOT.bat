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

echo [1/7] 🔄 Shutting Down Existing Bot Instances...
echo.

:: Check for existing Python processes that might be running the bot
tasklist /FI "IMAGENAME eq python.exe" /FO CSV | find /I "python.exe" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  Found existing Python processes, terminating them...
    
    :: Kill python.exe processes
    taskkill /IM "python.exe" /F /T >nul 2>&1
    
    :: Kill py.exe processes
    taskkill /IM "py.exe" /F /T >nul 2>&1
    
    echo ✅ Existing bot processes terminated
    echo Waiting 3 seconds for cleanup...
    timeout /t 3 /nobreak >nul
) else (
    echo ✅ No existing bot processes found
)

echo.
echo [2/7] 🔍 Checking Virtual Environment...
echo.

:: Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ ERROR: Virtual environment not found!
    echo.
    echo Please run the setup first by following these steps:
    echo   1. Open command prompt in this directory
    echo   2. Run: py -m venv venv
    echo   3. Run: venv\Scripts\activate
    echo   4. Run: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo ✅ Virtual environment found
echo.

echo [3/7] 🔄 Activating Virtual Environment...
echo.

:: Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERROR: Failed to activate virtual environment
    echo.
    pause
    exit /b 1
)

echo ✅ Virtual environment activated
python --version

echo.
echo [4/7] 📦 Checking Dependencies...
echo.

:: Check if key dependencies are installed
python -c "import telegram; print('✅ python-telegram-bot:', telegram.__version__)" 2>nul
if errorlevel 1 (
    echo ❌ ERROR: python-telegram-bot not installed
    echo.
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo ✅ Dependencies verified
)

echo.
echo [5/7] 🗄️ Testing Database Connection...
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
echo [6/7] ⚙️ Verifying Bot Configuration...
echo.

:: Check if main bot file exists
if not exist "run_bot.py" (
    echo ❌ ERROR: run_bot.py not found!
    echo.
    echo Please make sure you're in the correct directory
    pause
    exit /b 1
)

echo ✅ Bot files verified
echo.

:: Quick syntax check
python -m py_compile run_bot.py
if errorlevel 1 (
    echo ❌ ERROR: Bot code has syntax errors
    echo.
    echo Please check run_bot.py for issues
    pause
    exit /b 1
)

echo ✅ Bot code syntax verified
echo.

echo [7/7] 🏛️ Starting PNL Trading Bot...
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

:: Create a unique identifier for this bot instance
echo %TIME% - %DATE% > bot_instance.lock

:: Start the bot using the correct launcher
python run_bot.py

:: Cleanup on exit
if exist "bot_instance.lock" del "bot_instance.lock" >nul 2>&1

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
    echo   • Another bot instance running elsewhere
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