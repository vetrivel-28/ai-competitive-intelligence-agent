@echo off
echo ========================================
echo REDDIT LAPTOP DISCUSSION SCRAPER
echo ========================================
echo.
echo Installing required packages...
C:\Users\amird\AppData\Local\Programs\Python\Python313\python.exe -m pip install requests pandas --quiet
echo.
C:\Users\amird\AppData\Local\Programs\Python\Python313\python.exe scrape_reddit_detailed.py
echo.
pause
