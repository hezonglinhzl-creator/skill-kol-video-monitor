@echo off
if exist "%~dp0apps" (explorer.exe "%~dp0apps") else (explorer.exe "%~dp0skill")
