@echo off
echo.
echo ========================================
echo   Telegram PNL Bot Migration Export
echo ========================================
echo.

echo 📤 Starting database export process...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

REM Run the export script
echo 🗄️ Exporting MongoDB database...
python export_database.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Export failed! Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✅ Export completed successfully!
echo.
echo 📁 Your database backup is in the 'database_backup' folder.
echo 🔄 You can now push this project to GitHub and migrate to your new computer.
echo.
echo Next steps:
echo 1. Push to GitHub: git push origin main
echo 2. Clone on new computer: git clone your-repo-url
echo 3. Copy the 'database_backup' folder to the new computer
echo 4. Run import_database.py on the new computer
echo 5. Configure your .env file on the new computer
echo.
echo 📖 See MIGRATION_GUIDE.md for detailed instructions!
echo.

pause 