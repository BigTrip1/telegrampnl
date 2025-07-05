@echo off
setlocal enabledelayedexpansion
:: Set UTF-8 encoding for proper emoji display
chcp 65001 >nul 2>&1
color 0A
title PNL Trading Bot - Ultimate Launcher

:: Ensure this opens in a new dedicated terminal window
if not "%1"=="NEWWINDOW" (
    start "PNL Trading Bot - Ultimate Launcher" /max cmd /k "%~f0" NEWWINDOW
    exit /b
)

echo.
echo ===============================================================
echo.
echo     🚀 PNL TRADING BOT - ULTIMATE LAUNCHER 🚀
echo.
echo     Complete Setup, Sync, and Launch System
echo     One-Click Solution for Everything
echo.
echo ===============================================================
echo.

:: Set working directory to script location
cd /d "%~dp0"

:: Show environment info
echo.
echo 🎯 ULTIMATE LAUNCHER ENVIRONMENT 🎯
echo Working Directory: %CD%
echo.

:: Main menu
:MAIN_MENU
echo.
echo ===============================================================
echo.
echo                   🎮 MAIN MENU 🎮
echo.
echo ===============================================================
echo.
echo Choose an option:
echo.
echo   1️⃣  🚀 QUICK START - Launch Bot (Recommended)
echo   2️⃣  🔧 FULL SETUP - Complete Environment Setup
echo   3️⃣  🔄 SYNC DATABASE - Sync with other assets
echo   4️⃣  🛑 STOP BOT - Stop all running instances
echo   5️⃣  📦 INSTALL DEPS - Install/Update dependencies
echo   6️⃣  🧹 CLEANUP - Clean temporary files
echo   7️⃣  ❌ EXIT - Close launcher
echo.
echo ===============================================================
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto QUICK_START
if "%choice%"=="2" goto FULL_SETUP
if "%choice%"=="3" goto SYNC_DATABASE
if "%choice%"=="4" goto STOP_BOT
if "%choice%"=="5" goto INSTALL_DEPS
if "%choice%"=="6" goto CLEANUP
if "%choice%"=="7" goto EXIT
echo Invalid choice. Please try again.
goto MAIN_MENU

:QUICK_START
echo.
echo ===============================================================
echo.
echo     🚀 QUICK START - LAUNCHING BOT 🚀
echo.
echo ===============================================================
echo.

:: Step 1: Stop existing instances
echo [1/8] 🛑 Stopping Existing Bot Instances...
echo.
call :STOP_EXISTING_BOTS

:: Step 2: Check virtual environment
echo [2/8] 🔍 Checking Virtual Environment...
echo.
call :CHECK_VENV

:: Step 3: Activate virtual environment
echo [3/8] 🔄 Activating Virtual Environment...
echo.
call :ACTIVATE_VENV

:: Step 4: Check dependencies
echo [4/8] 📦 Checking Dependencies...
echo.
call :CHECK_DEPS

:: Step 5: Test database
echo [5/8] 🗄️ Testing Database Connection...
echo.
call :TEST_DATABASE

:: Step 6: Verify bot files
echo [6/8] ⚙️ Verifying Bot Configuration...
echo.
call :VERIFY_BOT

:: Step 7: Sync database (optional)
echo [7/8] 🔄 Checking Database Sync...
echo.
if exist "sync_database.py" (
    echo Database sync available - running quick sync...
    python sync_database.py --quick >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Database sync failed, continuing anyway...
    ) else (
        echo ✅ Database sync completed
    )
) else (
    echo ✅ No database sync needed
)

:: Step 8: Launch bot
echo [8/8] 🚀 Launching Bot...
echo.
goto LAUNCH_BOT

:FULL_SETUP
echo.
echo ===============================================================
echo.
echo     🔧 FULL SETUP - COMPLETE ENVIRONMENT 🔧
echo.
echo ===============================================================
echo.

:: Complete setup process
echo [1/10] 🛑 Stopping Existing Processes...
call :STOP_EXISTING_BOTS

echo [2/10] 🗂️ Creating Virtual Environment...
call :CREATE_VENV

echo [3/10] 🔄 Activating Virtual Environment...
call :ACTIVATE_VENV

echo [4/10] 📦 Installing Dependencies...
call :INSTALL_DEPENDENCIES

echo [5/10] 🗄️ Setting Up Database...
call :SETUP_DATABASE

echo [6/10] 🔄 Syncing Database...
call :SYNC_DATABASE_FULL

echo [7/10] ⚙️ Verifying Configuration...
call :VERIFY_CONFIG

echo [8/10] 🧹 Cleaning Up...
call :CLEANUP_FILES

echo [9/10] ✅ Testing Everything...
call :TEST_ALL

echo [10/10] 🚀 Ready to Launch!
echo.
echo Setup complete! Press any key to launch the bot...
pause >nul
goto LAUNCH_BOT

:SYNC_DATABASE
echo.
echo ===============================================================
echo.
echo     🔄 DATABASE SYNC - SYNC WITH OTHER ASSETS 🔄
echo.
echo ===============================================================
echo.

if not exist "sync_database.py" (
    echo ❌ Database sync script not found!
    echo Please ensure sync_database.py is in the project directory.
    pause
    goto MAIN_MENU
)

echo Choose sync option:
echo.
echo   1️⃣  🔄 FULL SYNC - Complete database synchronization
echo   2️⃣  ⚡ QUICK SYNC - Fast sync of recent changes
echo   3️⃣  📤 EXPORT - Export database for other assets
echo   4️⃣  📥 IMPORT - Import database from other assets
echo   5️⃣  🔙 BACK - Return to main menu
echo.
set /p sync_choice="Enter your choice (1-5): "

if "%sync_choice%"=="1" (
    echo Running full database sync...
    python sync_database.py --full
) else if "%sync_choice%"=="2" (
    echo Running quick database sync...
    python sync_database.py --quick
) else if "%sync_choice%"=="3" (
    echo Exporting database...
    python export_database.py
) else if "%sync_choice%"=="4" (
    echo Importing database...
    python import_database.py
) else if "%sync_choice%"=="5" (
    goto MAIN_MENU
) else (
    echo Invalid choice.
    pause
    goto SYNC_DATABASE
)

echo.
echo Database sync operation completed!
pause
goto MAIN_MENU

:STOP_BOT
echo.
echo ===============================================================
echo.
echo     🛑 STOP BOT - TERMINATE ALL INSTANCES 🛑
echo.
echo ===============================================================
echo.

call :STOP_EXISTING_BOTS
echo.
echo All bot instances have been stopped.
pause
goto MAIN_MENU

:INSTALL_DEPS
echo.
echo ===============================================================
echo.
echo     📦 INSTALL DEPENDENCIES - UPDATE PACKAGES 📦
echo.
echo ===============================================================
echo.

call :CHECK_VENV
call :ACTIVATE_VENV
call :INSTALL_DEPENDENCIES
echo.
echo Dependencies installation completed!
pause
goto MAIN_MENU

:CLEANUP
echo.
echo ===============================================================
echo.
echo     🧹 CLEANUP - REMOVE TEMPORARY FILES 🧹
echo.
echo ===============================================================
echo.

call :CLEANUP_FILES
echo.
echo Cleanup completed!
pause
goto MAIN_MENU

:: Function definitions
:STOP_EXISTING_BOTS
echo Checking for existing bot processes...
tasklist /FI "IMAGENAME eq python.exe" /FO CSV | find /I "python.exe" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  Found existing Python processes, terminating them...
    taskkill /IM "python.exe" /F /T >nul 2>&1
    taskkill /IM "py.exe" /F /T >nul 2>&1
    echo ✅ Existing bot processes terminated
    echo Waiting 3 seconds for cleanup...
    timeout /t 3 /nobreak >nul
) else (
    echo ✅ No existing bot processes found
)
if exist "bot_instance.lock" del "bot_instance.lock" >nul 2>&1
goto :eof

:CHECK_VENV
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Creating virtual environment...
    call :CREATE_VENV
) else (
    echo ✅ Virtual environment found
)
goto :eof

:CREATE_VENV
echo Creating virtual environment...
py -m venv venv >nul 2>&1
if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    echo Please ensure Python 3.8+ is installed
    pause
    goto MAIN_MENU
) else (
    echo ✅ Virtual environment created
)
goto :eof

:ACTIVATE_VENV
call venv\Scripts\activate.bat >nul 2>&1
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    goto MAIN_MENU
) else (
    echo ✅ Virtual environment activated
    python --version
)
goto :eof

:CHECK_DEPS
python -c "import telegram; print('✅ python-telegram-bot:', telegram.__version__)" 2>nul
if errorlevel 1 (
    echo ❌ Dependencies not installed
    echo Installing dependencies...
    call :INSTALL_DEPENDENCIES
) else (
    echo ✅ Dependencies verified
)
goto :eof

:INSTALL_DEPENDENCIES
echo Installing/updating dependencies...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    goto MAIN_MENU
) else (
    echo ✅ Dependencies installed successfully
)
goto :eof

:TEST_DATABASE
python -c "from database import DatabaseManager; db = DatabaseManager(); result = db.connect(); print('✅ Database connected successfully' if result else '❌ Database connection failed'); db.close_connection()" 2>nul
if errorlevel 1 (
    echo ⚠️  Database connection test failed
    echo Starting MongoDB service...
    net start MongoDB >nul 2>&1
    if errorlevel 1 (
        echo ❌ Could not start MongoDB service
        echo Please ensure MongoDB is installed and running
        echo Continuing anyway...
    ) else (
        echo ✅ MongoDB service started
    )
) else (
    echo ✅ Database connection verified
)
goto :eof

:VERIFY_BOT
if not exist "run_bot.py" (
    echo ❌ Bot files not found!
    pause
    goto MAIN_MENU
)
python -m py_compile run_bot.py >nul 2>&1
if errorlevel 1 (
    echo ❌ Bot code has syntax errors
    pause
    goto MAIN_MENU
) else (
    echo ✅ Bot configuration verified
)
goto :eof

:SETUP_DATABASE
if exist "database_backup\pnls.json" (
    echo Importing database backup...
    python import_database.py >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Database import failed
    ) else (
        echo ✅ Database backup imported
    )
) else (
    echo ✅ No database backup to import
)
goto :eof

:SYNC_DATABASE_FULL
if exist "sync_database.py" (
    echo Running full database sync...
    python sync_database.py --full >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Database sync failed
    ) else (
        echo ✅ Database sync completed
    )
) else (
    echo ✅ No database sync needed
)
goto :eof

:VERIFY_CONFIG
if not exist ".env" (
    echo ❌ Configuration file (.env) not found!
    echo Please create .env file with your bot token
    pause
    goto MAIN_MENU
) else (
    echo ✅ Configuration file found
)
goto :eof

:CLEANUP_FILES
echo Cleaning temporary files...
if exist "bot_instance.lock" del "bot_instance.lock" >nul 2>&1
if exist "__pycache__" rmdir /s /q "__pycache__" >nul 2>&1
if exist "*.pyc" del "*.pyc" >nul 2>&1
echo ✅ Temporary files cleaned
goto :eof

:TEST_ALL
echo Running comprehensive tests...
call :TEST_DATABASE
call :VERIFY_BOT
echo ✅ All tests passed
goto :eof

:LAUNCH_BOT
echo.
echo ===============================================================
echo.
echo        🎯 LAUNCHING PNL TRADING BOT 🎯
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
echo ===============================================================
echo.
echo 🎺 THE ARENA IS READY! Press Ctrl+C to stop the bot
echo.
echo ===============================================================
echo.

:: Create lock file
echo %TIME% - %DATE% > bot_instance.lock

:: Launch the bot
python run_bot.py

:: Cleanup on exit
if exist "bot_instance.lock" del "bot_instance.lock" >nul 2>&1

:: Show exit message
echo.
echo ===============================================================
echo.
echo        🛑 PNL TRADING BOT STOPPED 🛑
echo.
echo ===============================================================
echo.

if errorlevel 1 (
    echo ❌ Bot exited with errors
    echo Check the error messages above for details.
) else (
    echo ✅ Bot exited cleanly
)

echo.
echo Press any key to return to main menu...
pause >nul
goto MAIN_MENU

:EXIT
echo.
echo ===============================================================
echo.
echo     👋 THANK YOU FOR USING PNL TRADING BOT! 👋
echo.
echo ===============================================================
echo.
echo Goodbye!
echo.
pause
exit /b

:: End of script 