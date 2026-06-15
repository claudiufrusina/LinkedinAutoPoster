@echo off
set PYTHONIOENCODING=utf-8
cd /d "C:\Users\claudiu.frusina\Dev\External-Projects\LinkedinAutoPosts"

:: Check if the virtual environment exists, otherwise use global python
if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe web.py
) else (
    python web.py
)
