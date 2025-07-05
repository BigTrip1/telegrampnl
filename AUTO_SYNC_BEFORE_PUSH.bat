@echo off
setlocal enabledelayedexpansion

echo.
echo ==========================================
echo   AUTO DATABASE SYNC BEFORE GIT PUSH
echo ==========================================
echo.

:: Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Please run ASSET_1_SYNC.bat first to set up the environment.
    pause
    exit /b 1
)

:: Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

:: Check if MongoDB is running
echo 🔄 Checking MongoDB connection...
python -c "from pymongo import MongoClient; MongoClient('localhost', 27017, serverSelectionTimeoutMS=5000).admin.command('ping')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ MongoDB is not running or not accessible!
    echo Please start MongoDB before syncing.
    pause
    exit /b 1
)

:: Create backup directory if it doesn't exist
if not exist "database_backup" mkdir database_backup

:: Export current database
echo 🔄 Exporting current database...
python sync_database.py --export
if %errorlevel% neq 0 (
    echo ❌ Database export failed!
    pause
    exit /b 1
)

:: Copy latest export to backup folder for git tracking
echo 🔄 Preparing database for git commit...
if exist "database_sync\latest_database_export.json" (
    copy "database_sync\latest_database_export.json" "database_backup\latest_sync.json" >nul
    if %errorlevel% equ 0 (
        echo ✅ Database export copied to backup folder
    ) else (
        echo ❌ Failed to copy database export
        pause
        exit /b 1
    )
) else (
    echo ❌ Database export file not found!
    pause
    exit /b 1
)

:: Get database statistics
echo 🔄 Getting database statistics...
python sync_database.py --stats

:: Add database backup to git
echo 🔄 Adding database backup to git...
git add database_backup\latest_sync.json
if %errorlevel% neq 0 (
    echo ❌ Failed to add database backup to git!
    pause
    exit /b 1
)

:: Show git status
echo 🔄 Current git status:
git status --porcelain

:: Prompt for commit message
echo.
echo ✅ Database export completed successfully!
echo.
echo The database has been exported and is ready for git push.
echo Latest database backup has been added to git staging.
echo.
echo NEXT STEPS:
echo 1. Review the changes with: git status
echo 2. Commit your changes: git commit -m "Your commit message"
echo 3. Push to repository: git push origin master
echo.
echo The receiving asset will automatically sync with this database.
echo.
pause 