@echo off
echo Starting local server...
echo Your portfolio will be available at: http://localhost:8080
echo Press Ctrl+C to stop the server
echo.

REM Try to find Python
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Using Python server...
    python -m http.server 8080
) else (
    echo Python not found. Trying py launcher...
    py -m http.server 8080
)

pause
