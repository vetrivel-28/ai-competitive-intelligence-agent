@echo off
echo ========================================
echo LAPTOP MARKET ANALYSIS DASHBOARD
echo ========================================
echo.
echo Installing required packages...
C:\Users\amird\AppData\Local\Programs\Python\Python313\python.exe -m pip install streamlit plotly pandas sentence-transformers faiss-cpu --quiet
echo.
echo Starting dashboard...
echo.
echo Dashboard will open in your browser automatically.
echo Press Ctrl+C to stop the dashboard.
echo.
C:\Users\amird\AppData\Local\Programs\Python\Python313\python.exe -m streamlit run dashboard.py
pause
