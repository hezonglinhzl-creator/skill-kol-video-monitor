@echo off
cd /d "%~dp0"
python -c "import openpyxl" >nul 2>nul
if errorlevel 1 (
  echo Missing Python package: openpyxl
  echo Installing openpyxl now...
  python -m pip install openpyxl
)
echo Starting KOL recorder...
echo Keep this window open while using the AdsPower extension.
python "%~dp0kol_recorder_server.py"
pause
