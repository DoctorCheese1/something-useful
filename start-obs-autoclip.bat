@echo off
setlocal

REM Starts the OBS auto-clipping companion on Windows.
REM Edit the values below if your OBS WebSocket or clip settings differ.

set "SCRIPT_DIR=%~dp0"
set "OBS_HOST=localhost"
set "OBS_PORT=4455"
set "OBS_PASSWORD="
set "CLIP_LENGTH=30"
set "OUTPUT_FOLDER=%SCRIPT_DIR%clips"
set "NAME_FORMAT={date}-{time}-{scene}.mp4"
set "ENABLED_FOR=both"
set "AUTO_CLIP_INTERVAL=300"
set "AUTO_CLIP_COOLDOWN=10"

if not exist "%OUTPUT_FOLDER%" mkdir "%OUTPUT_FOLDER%"

set "PYTHONPATH=%SCRIPT_DIR%src;%PYTHONPATH%"

python -c "import obsws_python" >nul 2>nul
if errorlevel 1 (
  echo Installing required Python package obsws-python...
  python -m pip install -e "%SCRIPT_DIR%"
  if errorlevel 1 (
    echo.
    echo Failed to install dependencies. Install them manually with:
    echo python -m pip install -e "%SCRIPT_DIR%"
    pause
    exit /b 1
  )
)

set "PASSWORD_ARGS="
if not "%OBS_PASSWORD%"=="" set "PASSWORD_ARGS=--password %OBS_PASSWORD%"

python -m obs_autoclip.cli ^
  --host "%OBS_HOST%" ^
  --port "%OBS_PORT%" ^
  %PASSWORD_ARGS% ^
  --clip-length "%CLIP_LENGTH%" ^
  --output-folder "%OUTPUT_FOLDER%" ^
  --name-format "%NAME_FORMAT%" ^
  --enabled-for "%ENABLED_FOR%" ^
  --auto-clip-on-scene-change ^
  --auto-clip-interval "%AUTO_CLIP_INTERVAL%" ^
  --auto-clip-cooldown "%AUTO_CLIP_COOLDOWN%" ^
  watch

if errorlevel 1 (
  echo.
  echo obs-autoclip stopped with an error. Check that Python is installed and OBS WebSocket is enabled.
  pause
)
