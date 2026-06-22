@echo off
title Rankivo — SEO AI Tools
color 0B

echo.
echo  ============================================
echo   Rankivo — SEO AI Tools
echo  ============================================
echo.

cd /d "%~dp0"

REM --- Find the best Python ---
set "PYTHON="

REM 1) Try the local Python 3.14
if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
    "%LOCALAPPDATA%\Python\bin\python.exe" --version >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON=%LOCALAPPDATA%\Python\bin\python.exe"
    )
)

REM 2) Try Microsoft Store Python 3.13
if "%PYTHON%"=="" (
    for %%P in (
        "%LOCALAPPDATA%\Microsoft\WindowsApps\python3.13.exe"
        "%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe"
        "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
    ) do (
        if "%PYTHON%"=="" (
            %%P --version >nul 2>&1
            if not errorlevel 1 (
                set "PYTHON=%%~P"
            )
        )
    )
)

REM 3) Try system PATH python
if "%PYTHON%"=="" (
    python --version >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON=python"
    )
)

REM --- Check if we found Python ---
if "%PYTHON%"=="" (
    echo  [ERROR] Python not found.
    echo  Install Python 3.10+ from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo  Using: %PYTHON%
echo.

REM --- Auto-install dependencies if Flask is missing ---
"%PYTHON%" -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo  [SETUP] Flask not found — installing dependencies...
    echo.
    "%PYTHON%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo  [ERROR] Failed to install dependencies.
        echo  Try manually: "%PYTHON%" -m pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo.
    echo  [OK] Dependencies installed successfully.
    echo.
) else (
    echo  [OK] Dependencies are up to date.
    echo.
)

REM --- Check if port 5500 is already in use ---
netstat -an | findstr ":5500" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo  [WARNING] Port 5500 is already in use.
    echo  The app may already be running at http://localhost:5500
    echo.
    start http://localhost:5500
    pause
    exit /b 0
)

REM --- Start the server ---
echo  Starting server at http://localhost:5500
echo  Press Ctrl+C to stop the server.
echo  ============================================
echo.

REM Open browser after a short delay
start "" /b cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5500"

REM Set UTF-8 encoding to prevent crashes with Persian/Arabic text
set PYTHONIOENCODING=utf-8

REM Start the Flask app (this blocks until Ctrl+C)
"%PYTHON%" app.py

echo.
echo  Server stopped.
pause
