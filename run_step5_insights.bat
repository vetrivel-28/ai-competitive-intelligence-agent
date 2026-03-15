@echo off
echo ========================================
echo STEP 5: MARKET INSIGHT ENGINE
echo ========================================
echo.
echo Installing required packages...
C:\Users\amird\AppData\Local\Programs\Python\Python313\python.exe -m pip install pandas numpy --quiet
echo.
C:\Users\amird\AppData\Local\Programs\Python\Python313\python.exe step5_market_insights.py
echo.
pause
