@echo off
cd /d "%~dp0"
title JARVIS (text)
.venv\Scripts\python.exe -m jarvis --text %*
pause
