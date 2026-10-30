@echo off
setlocal EnableExtensions

cd /d "%~dp0.."
set "ROOT=%CD%"
set "VENV=%ROOT%\.venv"
set "PYTHON=%VENV%\Scripts\python.exe"

echo ================================
echo Setting up SigmaMusic
echo ================================

py -3.13 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.13 was not found. Install Python 3.13 and try again.
    exit /b 1
)

if not exist "%PYTHON%" (
    echo Creating Python 3.13 virtual environment...
    py -3.13 -m venv "%VENV%"
    if errorlevel 1 (
        echo ERROR: Could not create the virtual environment.
        exit /b 1
    )
) else (
    "%PYTHON%" --version | findstr /b /c:"Python 3.13" >nul
    if errorlevel 1 (
        echo ERROR: The existing .venv is not using Python 3.13.
        echo Delete .venv and run this setup again.
        exit /b 1
    )
)

echo Updating pip...
"%PYTHON%" -m pip install --upgrade pip
if errorlevel 1 exit /b 1

echo Installing application dependencies...
"%PYTHON%" -m pip install -r "%ROOT%\SigmaMusic\requirements.txt"
if errorlevel 1 exit /b 1

echo Detecting GPU support...
set "MODEL_INSTALL_INDEX=https://download.pytorch.org/whl/cpu"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$gpu = Get-CimInstance Win32_VideoController | Where-Object { $_.Name -match 'NVIDIA' }; if ($gpu) { exit 0 } else { exit 1 }" >nul 2>&1
if errorlevel 1 (
    echo No NVIDIA GPU detected. Installing CPU PyTorch...
) else (
    echo NVIDIA GPU detected. Installing PyTorch for GPU...
    set "MODEL_INSTALL_INDEX=https://download.pytorch.org/whl/cu128"
)

"%PYTHON%" -m pip install torch torchaudio --index-url %MODEL_INSTALL_INDEX%
if errorlevel 1 exit /b 1

echo Installing music model packages...
"%PYTHON%" -m pip install yourmt3 beat-this torchcodec
if errorlevel 1 exit /b 1

echo Configuring FFmpeg...
set "FFMPEG_BIN="
if defined FFMPEG_PATH if exist "%FFMPEG_PATH%\ffmpeg.exe" set "FFMPEG_BIN=%FFMPEG_PATH%"
if not defined FFMPEG_BIN (
    for /f "delims=" %%F in ('where ffmpeg 2^>nul') do if not defined FFMPEG_BIN set "FFMPEG_BIN=%%~dpF"
)
if not defined FFMPEG_BIN if exist "%ROOT%\ffmpeg\bin\ffmpeg.exe" set "FFMPEG_BIN=%ROOT%\ffmpeg\bin"

if defined FFMPEG_BIN (
    set "FFMPEG_PATH=%FFMPEG_BIN%"
    set "PATH=%FFMPEG_BIN%;%PATH%"
    echo FFmpeg configured at "%FFMPEG_BIN%".
) else (
    echo WARNING: FFmpeg was not found.
    echo Install FFmpeg, add its bin folder to PATH, and run setup again.
)

echo =========================================
echo Installation complete. Run SigmaMusic\run_app.bat.
echo =========================================
endlocal