
@echo off
cd /d "%~dp0"

py -3.13 sigma_ui.py

if errorlevel 1 (
    echo.
    echo Application failed to start.
    pause
)
