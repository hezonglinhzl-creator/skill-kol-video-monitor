@echo off
cd /d "%~dp0"

set PYTHON_CMD=python
python --version >nul 2>nul
if errorlevel 1 (
  set PYTHON_CMD=py
  py --version >nul 2>nul
  if errorlevel 1 (
    echo Python is not installed or not added to PATH.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo During installation, tick: Add Python to PATH
    pause
    exit /b 1
  )
)

%PYTHON_CMD% -c "import openpyxl" >nul 2>nul
if errorlevel 1 (
  echo Missing Python package: openpyxl
  echo Installing openpyxl now...
  %PYTHON_CMD% -m pip install openpyxl
)

echo Starting KOL recorder...
echo Keep this window open while using the Chrome extension.
%PYTHON_CMD% "%~dp0kol_recorder_server.py"
pause
