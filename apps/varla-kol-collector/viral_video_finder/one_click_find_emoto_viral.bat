@echo off
cd /d "%~dp0"

set PYTHON_CMD=python
python --version >nul 2>nul
if errorlevel 1 (
  set PYTHON_CMD=py
)

%PYTHON_CMD% -c "import openpyxl" >nul 2>nul
if errorlevel 1 (
  echo Missing openpyxl, installing...
  %PYTHON_CMD% -m pip install openpyxl
)

%PYTHON_CMD% "%~dp0one_click_find_emoto_viral.py"
pause
