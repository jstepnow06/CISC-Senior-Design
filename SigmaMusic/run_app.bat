@echo off
cd /d "%~dp0"

:: Makes sure script runs inside the same local virtual environment even on different pc
::.venv\Scripts\python.exe .\SigmaMusic\sigma_ui.py
:: Use ".." to step up to the CISC-Senior-Design folder to find the virtual environment
..\.venv\Scripts\python.exe sigma_ui.py