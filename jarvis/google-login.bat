@echo off
cd /d "%~dp0"
.venv\Scripts\python.exe -m jarvis.tools.google_workspace --login
pause
