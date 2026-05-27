@echo off
setlocal
title W-MIDI CLI

set "REPO_ROOT=%~dp0..\.."

REM ==============================
REM W-MIDI Configuration
REM ==============================
set "WLED_IP=192.168.178.117"
set "MIDI_PORT=Mushroom 4"
set "LED_COUNT=64"
set "BASE_NOTE=36"
set "COLOR_MODE=velocity_palette"
set "FIXED_COLOR=0,120,255"
set "VELOCITY_PALETTE_FILE=%REPO_ROOT%\palettes\velocity_palette.txt"
set "VELOCITY_PALETTE=3:255,255,255;5:255,0,0;10:0,120,255;20:255,140,0;30:0,255,120"
set "FRAME_INTERVAL_MS=5"
set "MIDI_READ_BURST=64"

REM Verbose logs: 1 = on, 0 = off
set "VERBOSE=0"

REM ==================================
REM Resolve Python executable
REM ==================================
set "PY_EXE="
if exist "C:\Users\maier\AppData\Local\Programs\Python\Launcher\py.exe" (
  set "PY_EXE=C:\Users\maier\AppData\Local\Programs\Python\Launcher\py.exe"
) else if exist "C:\Users\maier\AppData\Local\Programs\Python\Python312\python.exe" (
  set "PY_EXE=C:\Users\maier\AppData\Local\Programs\Python\Python312\python.exe"
) else (
  set "PY_EXE=python"
)

set "PALETTE_ARG="
if /I "%COLOR_MODE%"=="velocity_palette" (
  if exist "%VELOCITY_PALETTE_FILE%" (
    set "PALETTE_ARG=--velocity-palette-file ^"%VELOCITY_PALETTE_FILE%^""
  ) else (
    set "PALETTE_ARG=--velocity-palette ^"%VELOCITY_PALETTE%^""
  )
)

set "VERBOSE_ARG="
if "%VERBOSE%"=="1" set "VERBOSE_ARG=--verbose"

echo Starting W-MIDI bridge...
echo.
echo "%PY_EXE%" -m midi_wled_bridge.cli --wled-ip %WLED_IP% --midi-port "%MIDI_PORT%" --led-count %LED_COUNT% --base-note %BASE_NOTE% --frame-interval-ms %FRAME_INTERVAL_MS% --midi-read-burst %MIDI_READ_BURST% --color-mode %COLOR_MODE% --fixed-color %FIXED_COLOR% %PALETTE_ARG% %VERBOSE_ARG%
echo.

pushd "%REPO_ROOT%"
call "%PY_EXE%" -m midi_wled_bridge.cli --wled-ip %WLED_IP% --midi-port "%MIDI_PORT%" --led-count %LED_COUNT% --base-note %BASE_NOTE% --frame-interval-ms %FRAME_INTERVAL_MS% --midi-read-burst %MIDI_READ_BURST% --color-mode %COLOR_MODE% --fixed-color %FIXED_COLOR% %PALETTE_ARG% %VERBOSE_ARG%
set "EXIT_CODE=%ERRORLEVEL%"
popd

echo.
if not "%EXIT_CODE%"=="0" (
  echo Bridge exited with error code %EXIT_CODE%.
) else (
  echo Bridge stopped.
)
pause
exit /b %EXIT_CODE%
