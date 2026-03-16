@echo off
echo Opening your portfolio...
start "" "http://localhost:8080"
timeout /t 2 >nul
echo If that didn't work, trying direct file...
start "" "index.html"
echo Portfolio should open in your browser now!
pause
