@echo off
chcp 65001 >nul
if exist "%~dp0..\varla-kol-collector\Start_Varla_Collector.bat" (
  call "%~dp0..\varla-kol-collector\Start_Varla_Collector.bat"
) else (
  echo Full collector backend is required. Read README.md in this folder.
  pause
)
