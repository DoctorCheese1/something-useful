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

set "PASSWORD_ARGS="
if not "%OBS_PASSWORD%"=="" set "PASSWORD_ARGS=--password %OBS_PASSWORD%"

python -m obs_autoclip.cli watch ^
  --host "%OBS_HOST%" ^
  --port "%OBS_PORT%" ^
  %PASSWORD_ARGS% ^
  --clip-length "%CLIP_LENGTH%" ^
  --output-folder "%OUTPUT_FOLDER%" ^
  --name-format "%NAME_FORMAT%" ^
  --enabled-for "%ENABLED_FOR%" ^
  --auto-clip-on-scene-change ^
  --auto-clip-interval "%AUTO_CLIP_INTERVAL%" ^
  --auto-clip-cooldown "%AUTO_CLIP_COOLDOWN%"

if errorlevel 1 (
  echo.
  echo obs-autoclip stopped with an error. Check that Python is installed and OBS WebSocket is enabled.
  pause
)
