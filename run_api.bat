@echo off
echo Starting FastAPI backend on http://localhost:8000
C:\Users\amird\AppData\Local\Programs\Python\Python313\python.exe -m uvicorn api.main:app --reload --port 8000
