@echo off
echo Stopping SalesIQ backend server on port 5000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a
    echo Terminated process %%a
)
echo.
echo SalesIQ stopped.
pause
