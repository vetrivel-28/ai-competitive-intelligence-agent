@echo off
echo ========================================
echo YOUTUBE LAPTOP REVIEW SCRAPER
echo ========================================
echo.
echo Installing required packages...
C:\Users\amird\AppData\Local\Programs\Python\Python313\python.exe -m pip install selenium webdriver-manager pandas --quiet
echo.
C:\Users\amird\AppData\Local\Programs\Python\Python313\python.exe scrape_youtube_detailed.py
echo.
pause
