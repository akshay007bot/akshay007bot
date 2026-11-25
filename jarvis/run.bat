@echo off
cd /d "%~dp0"
title JARVIS
.venv\Scripts\python.exe -m jarvis %*
pause
