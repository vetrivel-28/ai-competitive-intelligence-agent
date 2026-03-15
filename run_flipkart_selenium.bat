@echo off
echo ========================================
echo FLIPKART SCRAPER (SELENIUM - RELIABLE)
echo ========================================
echo.
echo Installing Selenium if needed...
C:\Users\amird\AppData\Local\Programs\Python\Python313\python.exe -m pip install selenium webdriver-manager --quiet
echo.
C:\Users\amird\AppData\Local\Programs\Python\Python313\python.exe scrape_flipkart_selenium.py
echo.
pause
