
@echo off
cd /d "%~dp0"

::py -3.13 sigma_ui.py  ::remove this line

:: Points to virtual environment python that has all the installs inside
..\.venv\Scripts\python.exe sigma_ui.py

if errorlevel 1 (
    echo.
    echo Application failed to start.
    pause
)
