@echo off
echo ====================================================
echo Setting up SalesIQ to automatically start on Windows boot...
echo ====================================================

set SCRIPT_DIR=%~dp0
set VBS_TARGET=%SCRIPT_DIR%start_silent.vbs
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT_NAME=SalesIQ_AutoStart.vbs

copy /Y "%VBS_TARGET%" "%STARTUP_FOLDER%\%SHORTCUT_NAME%" >nul

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] SalesIQ is now set to start automatically whenever your PC boots up!
    echo It will run silently in the background on http://127.0.0.1:5000.
) else (
    echo.
    echo [ERROR] Could not copy to startup folder. Please try running as Administrator.
)

echo.
pause
