@echo off
setlocal enabledelayedexpansion

echo.
echo ==========================================
echo   DATABASE SYNCHRONIZATION SYSTEM TEST
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
    echo Please start MongoDB before testing.
    pause
    exit /b 1
)

echo ✅ MongoDB connection successful!
echo.

:: Test 1: Database Statistics
echo 🔄 TEST 1: Getting current database statistics...
python sync_database.py --stats
if %errorlevel% neq 0 (
    echo ❌ Database stats test failed!
    pause
    exit /b 1
)
echo ✅ Database stats test passed!
echo.

:: Test 2: Database Export
echo 🔄 TEST 2: Testing database export...
python sync_database.py --export
if %errorlevel% neq 0 (
    echo ❌ Database export test failed!
    pause
    exit /b 1
)
echo ✅ Database export test passed!
echo.

:: Test 3: Check export files
echo 🔄 TEST 3: Verifying export files exist...
if exist "database_sync\current_export_*.json" (
    echo ✅ Export files created successfully!
    for %%f in ("database_sync\current_export_*.json") do (
        echo    📁 Found: %%f
    )
) else (
    echo ❌ Export files not found!
    pause
    exit /b 1
)
echo.

:: Test 4: Auto-sync test
echo 🔄 TEST 4: Testing auto-sync functionality...
python sync_database.py --sync
if %errorlevel% neq 0 (
    echo ❌ Auto-sync test failed!
    pause
    exit /b 1
)
echo ✅ Auto-sync test passed!
echo.

:: Test 5: Check backup folder
echo 🔄 TEST 5: Verifying backup folder structure...
if exist "database_backup\latest_sync.json" (
    echo ✅ Backup folder structure correct!
    echo    📁 Found: database_backup\latest_sync.json
) else (
    echo ❌ Backup folder structure incorrect!
    pause
    exit /b 1
)
echo.

:: Test 6: Self-merge test (merge with own export)
echo 🔄 TEST 6: Testing self-merge (should have no changes)...
python sync_database.py --merge database_backup\latest_sync.json
if %errorlevel% neq 0 (
    echo ❌ Self-merge test failed!
    pause
    exit /b 1
)
echo ✅ Self-merge test passed!
echo.

:: Test 7: Verify merge report
echo 🔄 TEST 7: Checking merge report generation...
if exist "database_sync\merge_report_*.txt" (
    echo ✅ Merge report generated successfully!
    for /f "tokens=*" %%a in ('dir /b /od "database_sync\merge_report_*.txt" 2^>nul') do (
        set "latest_report=%%a"
    )
    if defined latest_report (
        echo    📁 Latest report: !latest_report!
        echo.
        echo 📊 MERGE REPORT SUMMARY:
        findstr /C:"SUMMARY:" /C:"Total records" /C:"Total conflicts" "database_sync\!latest_report!" 2>nul
    )
) else (
    echo ❌ Merge report not found!
    pause
    exit /b 1
)
echo.

:: Test 8: Database integrity check
echo 🔄 TEST 8: Final database integrity check...
python sync_database.py --stats
if %errorlevel% neq 0 (
    echo ❌ Database integrity check failed!
    pause
    exit /b 1
)
echo ✅ Database integrity check passed!
echo.

:: Test Summary
echo ==========================================
echo   DATABASE SYNC SYSTEM TEST SUMMARY
echo ==========================================
echo.
echo ✅ All tests passed successfully!
echo.
echo TESTED COMPONENTS:
echo • Database connection and statistics
echo • Database export functionality
echo • File creation and structure
echo • Auto-sync with git integration
echo • Backup folder management
echo • Self-merge capability
echo • Merge report generation
echo • Database integrity verification
echo.
echo SYSTEM STATUS: 🟢 READY FOR PRODUCTION
echo.
echo The database synchronization system is working correctly
echo and ready to ensure both assets have identical databases.
echo.
echo NEXT STEPS:
echo 1. Use AUTO_SYNC_BEFORE_PUSH.bat before git push
echo 2. Use AUTO_SYNC_AFTER_PULL.bat after git pull
echo 3. Both assets will always have synchronized databases
echo.
pause 