@echo off
echo ========================================
echo STEP 4: COMPETITOR PRICE ANALYSIS
echo ========================================
echo.
echo Installing required packages...
C:\Users\amird\AppData\Local\Programs\Python\Python313\python.exe -m pip install pandas numpy --quiet
echo.
C:\Users\amird\AppData\Local\Programs\Python\Python313\python.exe step4_competitor_analysis.py
echo.
pause
