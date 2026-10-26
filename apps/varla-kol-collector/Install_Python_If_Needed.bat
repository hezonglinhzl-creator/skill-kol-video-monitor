@echo off
python --version >nul 2>nul
if not errorlevel 1 (
  echo Python is already available.
  python --version
  pause
  exit /b 0
)

py --version >nul 2>nul
if not errorlevel 1 (
  echo Python launcher is already available.
  py --version
  pause
  exit /b 0
)

echo Python is not available on this computer.
echo Trying to install Python 3.12 with winget...
winget --version >nul 2>nul
if errorlevel 1 (
  echo winget is not available. Opening Python download page.
  start https://www.python.org/downloads/
  echo Please install Python 3.10+ and tick "Add Python to PATH".
  pause
  exit /b 1
)

winget install --id Python.Python.3.12 --exact --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
  echo winget install failed. Opening Python download page.
  start https://www.python.org/downloads/
  echo Please install Python 3.10+ and tick "Add Python to PATH".
  pause
  exit /b 1
)

echo Python install finished. Close and reopen this folder, then run Start_Varla_Collector.bat.
pause
