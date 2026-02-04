@echo off
REM AI Operations Assistant - Local Startup Script (Windows)

echo === AI Operations Assistant Startup ===
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please create .env file from .env.example and add your API keys:
    echo   copy .env.example .env
    echo   # Then edit .env with your API keys
    echo.
    pause
)

REM Get port from environment or use default
if "%PORT%"=="" set PORT=8000

echo.
echo Starting AI Operations Assistant on port %PORT%...
echo API will be available at: http://localhost:%PORT%
echo API docs available at: http://localhost:%PORT%/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
uvicorn main:app --reload --port %PORT%
