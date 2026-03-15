@echo off
echo ========================================
echo STEP 2: SENTIMENT ANALYSIS
echo ========================================
echo.
echo Installing required packages...
C:\Users\amird\AppData\Local\Programs\Python\Python313\python.exe -m pip install textblob pandas numpy --quiet
echo.
echo Downloading TextBlob corpora (one-time setup)...
C:\Users\amird\AppData\Local\Programs\Python\Python313\python.exe -m textblob.download_corpora
echo.
C:\Users\amird\AppData\Local\Programs\Python\Python313\python.exe step2_sentiment_analysis.py
echo.
pause
