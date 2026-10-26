@echo off
chcp 65001 >nul
set CHROME=C:\Program Files\Google\Chrome\Application\chrome.exe
set PROFILE=%LOCALAPPDATA%\Google\Chrome\User Data

echo Starting Chrome with remote debugging on port 9222...
echo.
echo If Chrome is already open and this does not work:
echo 1. Close all Chrome windows manually
echo 2. Run this file again
echo.

start "" "%CHROME%" --remote-debugging-port=9222 --profile-directory="Default" --user-data-dir="%PROFILE%" "https://www.instagram.com/explore/tags/ebike/"

echo Chrome opened. Keep it open while scraping.
pause
