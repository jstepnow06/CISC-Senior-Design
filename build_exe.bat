@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Please create one first.
    exit /b 1
)

.venv\Scripts\python.exe -m pip install pyinstaller
.venv\Scripts\python.exe -m PyInstaller --noconsole --onefile --name SigmaMusic .\SigmaMusic\sigma_ui.py

echo.
echo Build complete.
echo Output: dist\SigmaMusic.exe
