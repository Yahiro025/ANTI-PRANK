@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Setup needed: create .venv and install requirements.txt as described in README.md.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" "caught.py"
if errorlevel 1 pause
