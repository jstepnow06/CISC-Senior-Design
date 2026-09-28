@echo off
cd /d "%~dp0"

:: Makes sure script runs inside the same local virtual environment even on different pc
.venv\Scripts\python.exe .\SigmaMusic\sigma_ui.py