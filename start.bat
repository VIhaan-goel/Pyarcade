@echo off
cd /d "%~dp0"
start "PyArcade backend" cmd /k ".venv\Scripts\activate.bat && cd backend && python app.py"
start "PyArcade frontend" cmd /k ".venv\Scripts\activate.bat && cd frontend && python main.py"
timeout /t 6 >nul
start http://localhost:8080