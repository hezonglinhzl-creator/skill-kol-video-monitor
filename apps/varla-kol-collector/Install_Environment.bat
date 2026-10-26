@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo ========================================
echo Varla Collector Environment Installer
echo ========================================
echo.

set "PYTHON_CMD="
python --version >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=python"

if not defined PYTHON_CMD (
  py --version >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=py"
)

if not defined PYTHON_CMD (
  if exist "%~dp0tools\python-3.12.8-amd64.exe" (
    echo Installing bundled Python 3.12.8...
    "%~dp0tools\python-3.12.8-amd64.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1 Include_pip=1
  ) else (
    echo Bundled Python installer was not found.
    echo Opening Python download page...
    start https://www.python.org/downloads/
    echo Please install Python 3.10+ and tick "Add Python to PATH".
    pause
    exit /b 1
  )
)

set "PATH=%LocalAppData%\Programs\Python\Python312;%LocalAppData%\Programs\Python\Python312\Scripts;C:\Program Files\Python312;C:\Program Files\Python312\Scripts;%PATH%"

set "PYTHON_CMD="
python --version >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=python"

if not defined PYTHON_CMD (
  py --version >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=py"
)

if not defined PYTHON_CMD (
  echo Python still cannot be found after install.
  echo Close this window, reopen the folder, then run this installer again.
  pause
  exit /b 1
)

echo.
echo Python:
%PYTHON_CMD% --version

echo.
echo Installing Python package: openpyxl
%PYTHON_CMD% -m pip install openpyxl
if errorlevel 1 (
  echo Failed to install openpyxl. Please check network and run again.
  pause
  exit /b 1
)

if exist "%~dp0tools\ffmpeg\bin\ffmpeg.exe" (
  echo.
  echo FFmpeg bundled at:
  echo %~dp0tools\ffmpeg\bin
  echo Adding bundled FFmpeg to user PATH...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$bin=(Resolve-Path '%~dp0tools\ffmpeg\bin').Path; $p=[Environment]::GetEnvironmentVariable('Path','User'); if (($p -split ';') -notcontains $bin) { [Environment]::SetEnvironmentVariable('Path', (($p.TrimEnd(';') + ';' + $bin).TrimStart(';')), 'User') }"
) else (
  echo.
  echo Bundled FFmpeg was not found. This is optional for the KOL recorder.
)

echo.
echo Environment install finished.
echo Now run Start_Varla_Collector.bat
pause
