@echo off
echo ================================================
echo   BioDockify MD Universal - GUI Mode
echo ================================================
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found
    echo Please run start.bat first
    pause
    exit /b 1
)

echo Starting GUI...
python main.py --ui

pause
