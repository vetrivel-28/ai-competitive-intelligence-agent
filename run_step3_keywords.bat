@echo off
echo ========================================
echo STEP 3: KEYWORD EXTRACTION
echo ========================================
echo.
echo Installing required packages...
C:\Users\amird\AppData\Local\Programs\Python\Python313\python.exe -m pip install textblob pandas numpy scikit-learn --quiet
echo.
C:\Users\amird\AppData\Local\Programs\Python\Python313\python.exe step3_keyword_extraction.py
echo.
pause
