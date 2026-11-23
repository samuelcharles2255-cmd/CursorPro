@echo off
echo ===================================================
echo Starting Atrium Platform: Django API + Next.js Frontend
echo ===================================================

start "Django Backend API (Port 8000)" cmd /k "python manage.py runserver 0.0.0.0:8000"
timeout /t 2 /nobreak >nul
start "Next.js Luxury Frontend (Port 3000)" cmd /k "cd frontend && npm run dev"

echo.
echo Django API: http://127.0.0.1:8000/api/
echo Next.js Frontend: http://localhost:3000/
echo.
echo Press any key to exit this launcher window...
pause >nul
