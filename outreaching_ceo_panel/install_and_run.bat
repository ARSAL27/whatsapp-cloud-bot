@echo off
title Outreaching CEO Panel - Launcher
echo ==========================================
echo    OUTREACHING CEO PANEL - COMMAND CENTER
echo ==========================================
echo.

:: Try to find Python automatically first
set PYTHON_EXE=python
py --version >nul 2>&1 && set PYTHON_EXE=py
python --version >nul 2>&1 && set PYTHON_EXE=python

:: Fallback to the absolute path if others fail
if "%PYTHON_EXE%"=="python" (
    set PYTHON_EXE="C:\Users\DELL\AppData\Local\Programs\Python\Python312\python.exe"
)

echo Using: %PYTHON_EXE%
echo.

echo [1/3] Checking requirements...
%PYTHON_EXE% -m pip install -r requirements.txt

echo [2/3] Starting Secure Server...
echo Panel will be available at: http://127.0.0.1:5000
echo.
%PYTHON_EXE% app.py

pause
