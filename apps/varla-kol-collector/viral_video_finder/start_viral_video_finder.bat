@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "PYTHON_CMD="

if defined VARLA_PYTHON_CMD (
  "%VARLA_PYTHON_CMD%" --version >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=%VARLA_PYTHON_CMD%"
)

if not defined PYTHON_CMD (
  set "CODEX_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
  if exist "!CODEX_PYTHON!" (
    "!CODEX_PYTHON!" --version >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=!CODEX_PYTHON!"
  )
)

if not defined PYTHON_CMD (
  python --version >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
  py --version >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=py"
)

if not defined PYTHON_CMD (
  echo Python is not installed or not available.
  echo Tried VARLA_PYTHON_CMD, Codex bundled Python, python, and py.
  echo Please install Python 3.10+ and tick "Add Python to PATH".
  pause
  exit /b 1
)

"%PYTHON_CMD%" -c "import openpyxl" >nul 2>nul
if errorlevel 1 (
  echo Missing Python package: openpyxl
  echo Installing openpyxl now...
  "%PYTHON_CMD%" -m pip install openpyxl
)

echo Starting viral video control center...
echo Keep this window open while using the local website.
"%PYTHON_CMD%" "%~dp0viral_video_control_center.py"
pause
