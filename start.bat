@echo off
echo ================================================
echo   BioDockify MD Universal
echo   Multi-GPU Molecular Dynamics Framework
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if needed
if not exist "venv\Lib\site-packages\pyqt6" (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo WARNING: Some dependencies may have failed to install
    )
)

echo.
echo Starting BioDockify MD Universal...
echo.

REM Run the application
python main.py %*

if errorlevel 1 (
    echo.
    echo ERROR: Application exited with errors
    pause
    exit /b 1
)

pause
