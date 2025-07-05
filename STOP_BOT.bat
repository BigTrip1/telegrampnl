@echo off
setlocal enabledelayedexpansion
color 0C
title Stop PNL Trading Bot

echo.
echo ===============================================================
echo.
echo     🛑 STOP PNL TRADING BOT 🛑
echo.
echo ===============================================================
echo.

echo [1/3] 🔍 Searching for Bot Processes...
echo.

:: Check for Python processes that might be running the bot
set "found_processes=0"

:: Check for python.exe processes
for /f "tokens=1,2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO TABLE /NH 2^>nul') do (
    if "%%a"=="python.exe" (
        set /a found_processes+=1
        echo Found: %%a (PID: %%b)
    )
)

:: Check for py.exe processes
for /f "tokens=1,2" %%a in ('tasklist /FI "IMAGENAME eq py.exe" /FO TABLE /NH 2^>nul') do (
    if "%%a"=="py.exe" (
        set /a found_processes+=1
        echo Found: %%a (PID: %%b)
    )
)

if !found_processes! equ 0 (
    echo ✅ No Python processes found running
    echo.
    echo The bot appears to already be stopped.
    echo.
    pause
    exit /b 0
)

echo.
echo Found !found_processes! Python process(es) that might be running the bot.
echo.

echo [2/3] 🔄 Terminating Bot Processes...
echo.

:: Kill python.exe processes
echo Stopping python.exe processes...
taskkill /IM "python.exe" /F /T >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Some python.exe processes might still be running
) else (
    echo ✅ python.exe processes terminated
)

:: Kill py.exe processes
echo Stopping py.exe processes...
taskkill /IM "py.exe" /F /T >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Some py.exe processes might still be running
) else (
    echo ✅ py.exe processes terminated
)

echo.
echo [3/3] 🧹 Cleaning Up...
echo.

:: Wait for processes to fully terminate
echo Waiting for processes to fully terminate...
timeout /t 2 /nobreak >nul

:: Remove any lock files
if exist "bot_instance.lock" (
    del "bot_instance.lock" >nul 2>&1
    echo ✅ Removed bot instance lock file
)

echo.
echo ===============================================================
echo.
echo     ✅ BOT SHUTDOWN COMPLETE ✅
echo.
echo ===============================================================
echo.
echo The PNL Trading Bot has been stopped.
echo You can now safely start a new instance.
echo.
echo 🔄 To start the bot again: Run LAUNCH_PNL_BOT.bat
echo.
pause 