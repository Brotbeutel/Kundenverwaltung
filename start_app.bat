@echo off
setlocal
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0App\setup_dev_env.ps1"
if errorlevel 1 (
    exit /b %errorlevel%
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "cd /d C:\GitHub\Kundenverwaltung; .\App\.venv\Scripts\python.exe .\App\init_db.py"
if errorlevel 1 (
    exit /b %errorlevel%
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "cd /d C:\GitHub\Kundenverwaltung; .\App\.venv\Scripts\python.exe .\App\app.py"
