@echo off
echo Starting Hostel Management System API Server...
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause