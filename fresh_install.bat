@echo off
echo.
echo ===============================================
echo   Fresh Python Installation - Telegram PNL Bot
echo ===============================================
echo.
echo This will perform a COMPLETE fresh installation
echo to fix any Python library conflicts or issues.
echo.

pause

echo.
echo 🧹 Step 1: Cleaning existing environment...
echo.

REM Remove existing virtual environment
if exist "venv" (
    echo Removing existing virtual environment...
    rmdir /s /q venv
)

REM Clear pip cache
echo Clearing pip cache...
python -m pip cache purge

echo.
echo 🔄 Step 2: Upgrading pip...
echo.

python -m pip install --upgrade pip

echo.
echo 🐍 Step 3: Creating fresh virtual environment...
echo.

python -m venv venv

if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment!
    echo Please check your Python installation.
    pause
    exit /b 1
)

echo.
echo 📦 Step 4: Installing dependencies...
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Install exact versions to avoid conflicts
echo Installing python-telegram-bot...
pip install python-telegram-bot==20.7

echo Installing pymongo...
pip install pymongo==4.6.1

echo Installing pandas...
pip install pandas==2.1.4

echo Installing openpyxl...
pip install openpyxl==3.1.2

echo Installing requests...
pip install requests==2.31.0

echo Installing python-dotenv...
pip install python-dotenv==1.0.0

echo Installing additional dependencies...
pip install dnspython==2.4.2
pip install certifi==2023.11.17
pip install urllib3==2.1.0
pip install idna==3.6
pip install charset-normalizer==3.3.2

echo.
echo 🧪 Step 5: Testing installation...
echo.

REM Test critical imports
python -c "import telegram; print('✅ Telegram bot library OK')" || goto :error
python -c "import pymongo; print('✅ MongoDB library OK')" || goto :error
python -c "import pandas; print('✅ Pandas library OK')" || goto :error
python -c "import requests; print('✅ Requests library OK')" || goto :error
python -c "from dotenv import load_dotenv; print('✅ Python-dotenv library OK')" || goto :error

echo.
echo 🔧 Step 6: Testing MongoDB connection...
echo.

python -c "from pymongo import MongoClient; client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=3000); client.admin.command('ping'); print('✅ MongoDB connection successful!')" || goto :mongo_error

echo.
echo ✅ SUCCESS! All libraries installed and tested successfully!
echo.
echo 🎯 Next Steps:
echo 1. Make sure your .env file is configured with your bot token
echo 2. Run: python run_bot.py
echo.
echo 📁 To activate this environment later, run: venv\Scripts\activate
echo.

pause
exit /b 0

:error
echo.
echo ❌ Installation failed! 
echo Please check the error messages above.
echo.
echo 🔧 Try these solutions:
echo 1. Make sure Python 3.10.x is installed
echo 2. Run as administrator
echo 3. Check your internet connection
echo 4. Try the manual installation steps in PYTHON_SETUP_FIX.md
echo.
pause
exit /b 1

:mongo_error
echo.
echo ⚠️ Python libraries installed successfully, but MongoDB connection failed!
echo.
echo 🔧 MongoDB Solutions:
echo 1. Make sure MongoDB is installed and running
echo 2. Run: net start MongoDB
echo 3. Check if MongoDB service is running in Services
echo.
echo 📚 Your Python environment is ready, just fix MongoDB and run the bot!
echo.
pause
exit /b 0 