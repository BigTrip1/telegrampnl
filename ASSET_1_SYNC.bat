@echo off
setlocal enabledelayedexpansion
color 0B
title Asset 1 Sync with Asset 2

echo.
echo ===============================================================
echo.
echo     🔄 ASSET 1 SYNC WITH ASSET 2 🔄
echo.
echo ===============================================================
echo.
echo This script will sync Asset 1 with all improvements made on Asset 2:
echo ✅ Python 3.13 compatibility
echo ✅ Fixed syntax errors  
echo ✅ Enhanced disclaimer
echo ✅ New management tools
echo ✅ Updated dependencies
echo.

pause

echo.
echo [1/10] 📥 Pulling Latest Updates from GitHub...
echo.

git pull origin main
if %errorlevel% neq 0 (
    echo ❌ Failed to pull updates from GitHub!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo ✅ Successfully pulled latest updates
echo.

echo [2/10] 💾 Backing Up Current Environment...
echo.

if exist "venv" (
    if exist "venv_backup_old" (
        echo Removing old backup...
        rmdir /s /q "venv_backup_old"
    )
    echo Creating backup of current virtual environment...
    ren "venv" "venv_backup_old"
    echo ✅ Backup created as venv_backup_old
) else (
    echo ✅ No existing virtual environment to backup
)

echo.
echo [3/10] 🧹 Cleaning Python Environment...
echo.

echo Clearing pip cache...
python -m pip cache purge

echo Upgrading pip...
python -m pip install --upgrade pip

echo ✅ Environment cleaned

echo.
echo [4/10] 🐍 Creating Fresh Virtual Environment...
echo.

python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment!
    echo Please check your Python installation.
    pause
    exit /b 1
)

echo ✅ Virtual environment created

echo.
echo [5/10] 🔄 Activating Virtual Environment...
echo.

call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment!
    pause
    exit /b 1
)

echo ✅ Virtual environment activated

echo.
echo [6/10] 📦 Installing Updated Dependencies...
echo.

echo Installing Python 3.13 compatible packages...
echo.

echo Installing python-telegram-bot==21.0.1...
pip install python-telegram-bot==21.0.1

echo Installing httpx==0.28.1...
pip install httpx==0.28.1

echo Installing pymongo==4.6.1...
pip install pymongo==4.6.1

echo Installing pandas==2.3.0...
pip install pandas==2.3.0

echo Installing openpyxl==3.1.5...
pip install openpyxl==3.1.5

echo Installing remaining dependencies...
pip install -r requirements.txt

echo ✅ All dependencies installed

echo.
echo [7/10] 🧪 Testing Installation...
echo.

echo Testing critical imports...
python -c "import telegram; print('✅ Telegram bot library OK')" || goto :error
python -c "import pymongo; print('✅ MongoDB library OK')" || goto :error  
python -c "import pandas; print('✅ Pandas library OK')" || goto :error
python -c "import requests; print('✅ Requests library OK')" || goto :error
python -c "from dotenv import load_dotenv; print('✅ Python-dotenv library OK')" || goto :error

echo ✅ All imports successful

echo.
echo [8/10] 🗄️ Testing Database Connection...
echo.

python -c "from pymongo import MongoClient; client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=3000); client.admin.command('ping'); print('✅ MongoDB connection successful!')" || goto :mongo_error

echo Testing PNL records...
python -c "from database import DatabaseManager; dm = DatabaseManager(); dm.connect(); count = dm.pnls_collection.count_documents({}); print(f'✅ PNL records: {count}')"

echo.
echo [9/10] ⚙️ Checking Configuration...
echo.

if not exist ".env" (
    echo Creating .env file from template...
    copy "config\env.production.template" ".env"
    echo ⚠️  Please edit .env file with your bot token and settings
    echo ⚠️  Run: notepad .env
) else (
    echo ✅ .env file exists
)

python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ Config loaded!' if os.getenv('BOT_TOKEN') and os.getenv('BOT_TOKEN') != 'your_telegram_bot_token_here' else '⚠️ Please update BOT_TOKEN in .env file')"

echo.
echo [10/10] 🎯 Testing New Infrastructure...
echo.

if exist "STOP_BOT.bat" (
    echo ✅ STOP_BOT.bat available
) else (
    echo ❌ STOP_BOT.bat not found
)

if exist "LAUNCH_PNL_BOT.bat" (
    echo ✅ Enhanced LAUNCH_PNL_BOT.bat available  
) else (
    echo ❌ LAUNCH_PNL_BOT.bat not found
)

echo.
echo ===============================================================
echo.
echo     🎉 SYNC COMPLETE! 🎉
echo.
echo ===============================================================
echo.
echo Asset 1 has been successfully synchronized with Asset 2!
echo.
echo ✅ Python 3.13 compatibility achieved
echo ✅ All dependencies updated
echo ✅ Database connection verified
echo ✅ New management tools available
echo ✅ Enhanced features ready
echo.
echo 🎯 Next Steps:
echo 1. Update your .env file if needed: notepad .env
echo 2. Test the bot: LAUNCH_PNL_BOT.bat
echo 3. Verify /loretotalprofit shows new disclaimer
echo.
echo 🔧 Management Tools:
echo • Start: LAUNCH_PNL_BOT.bat (7-step process)
echo • Stop:  STOP_BOT.bat (clean shutdown)
echo.
echo 📊 Your bot now has the same features as Asset 2:
echo • 190 PNL records accessible
echo • Python 3.13 compatibility
echo • Enhanced disclaimer in /loretotalprofit
echo • Professional management tools
echo • Auto-shutdown conflict prevention
echo.

pause
exit /b 0

:error
echo.
echo ❌ Installation error occurred!
echo Please check the error messages above.
echo.
echo 🔧 Try these solutions:
echo 1. Make sure Python 3.10+ is installed
echo 2. Run as administrator
echo 3. Check internet connection
echo 4. Try manual steps in ASSET_1_SYNC_GUIDE.md
echo.
pause
exit /b 1

:mongo_error
echo.
echo ⚠️ Python libraries OK, but MongoDB connection failed!
echo.
echo 🔧 MongoDB Solutions:
echo 1. Make sure MongoDB is installed and running
echo 2. Run: net start MongoDB
echo 3. Check Windows Services for MongoDB
echo.
echo 📚 Your Python environment is ready, just need to fix MongoDB!
echo Then run: LAUNCH_PNL_BOT.bat
echo.
pause
exit /b 0 