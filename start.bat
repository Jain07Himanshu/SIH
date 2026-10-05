@echo off
echo ===================================================
echo     Starting Seva Setu Civic Grievance Platform
echo ===================================================
echo.
cd /d "%~dp0"

echo [1/2] Initializing database and demo data...
python seed_platform_demo.py
echo.

echo [2/2] Launching server at http://127.0.0.1:8000 ...
echo Open your browser at: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server.
echo.

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
