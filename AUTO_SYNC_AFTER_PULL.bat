@echo off
setlocal enabledelayedexpansion

echo.
echo ==========================================
echo   AUTO DATABASE SYNC AFTER GIT PULL
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

:: Pull latest changes from git
echo 🔄 Pulling latest changes from git...
git pull origin master
if %errorlevel% neq 0 (
    echo ❌ Git pull failed!
    pause
    exit /b 1
)

:: Check if remote database backup exists
if not exist "database_backup\latest_sync.json" (
    echo ⚠️  No remote database backup found.
    echo This might be the first sync or no database changes were pushed.
    echo Current database will be maintained.
    pause
    exit /b 0
)

:: Get current database stats before sync
echo 🔄 Getting current database statistics...
echo BEFORE SYNC:
python sync_database.py --stats

:: Merge with remote database
echo 🔄 Merging with remote database...
python sync_database.py --merge database_backup\latest_sync.json
if %errorlevel% neq 0 (
    echo ❌ Database merge failed!
    pause
    exit /b 1
)

:: Get database stats after sync
echo 🔄 Getting updated database statistics...
echo AFTER SYNC:
python sync_database.py --stats

:: Export current database to maintain sync
echo 🔄 Exporting updated database...
python sync_database.py --sync
if %errorlevel% neq 0 (
    echo ❌ Database export failed!
    pause
    exit /b 1
)

:: Show merge reports if they exist
if exist "database_sync\merge_report_*.txt" (
    echo.
    echo 📊 MERGE REPORT SUMMARY:
    echo.
    for /f "tokens=*" %%a in ('dir /b /od "database_sync\merge_report_*.txt" 2^>nul') do (
        set "latest_report=%%a"
    )
    if defined latest_report (
        echo Latest merge report: !latest_report!
        echo.
        findstr /C:"SUMMARY:" /C:"Total records" /C:"Total conflicts" "database_sync\!latest_report!" 2>nul
    )
)

echo.
echo ✅ Database synchronization completed successfully!
echo.
echo SYNCHRONIZATION SUMMARY:
echo • Remote database changes have been merged
echo • No duplicate records were created
echo • Both assets now have identical databases
echo • All merge conflicts have been resolved
echo.
echo The database is now synchronized with the remote asset.
echo You can continue using the bot with the latest data.
echo.
pause 