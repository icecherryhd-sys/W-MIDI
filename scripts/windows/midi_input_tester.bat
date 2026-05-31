@echo off
setlocal

set "REPO_ROOT=%~dp0..\.."

set "PY_EXE="
if exist "C:\Users\maier\AppData\Local\Programs\Python\Launcher\py.exe" (
  set "PY_EXE=C:\Users\maier\AppData\Local\Programs\Python\Launcher\py.exe"
) else if exist "C:\Users\maier\AppData\Local\Programs\Python\Python312\python.exe" (
  set "PY_EXE=C:\Users\maier\AppData\Local\Programs\Python\Python312\python.exe"
) else (
  set "PY_EXE=python"
)

echo MIDI Input Tester
echo =================
echo.
echo 1) List available MIDI input ports
echo 2) Monitor a specific MIDI input port
echo.
set /p "MODE=Choose 1 or 2: "

pushd "%REPO_ROOT%"

if "%MODE%"=="1" (
  call "%PY_EXE%" -m midi_wled_bridge.midi_tester --list-only
  set "EXIT_CODE=%ERRORLEVEL%"
  popd
  pause
  exit /b %EXIT_CODE%
)

if "%MODE%"=="2" (
  echo.
  call "%PY_EXE%" -m midi_wled_bridge.midi_tester --list-only
  echo.
  set /p "PORT_NAME=Type port name (or substring, e.g. loopMIDI): "
  echo.
  call "%PY_EXE%" -m midi_wled_bridge.midi_tester --port "%PORT_NAME%"
  set "EXIT_CODE=%ERRORLEVEL%"
  popd
  pause
  exit /b %EXIT_CODE%
)

popd
echo Invalid selection.
pause
exit /b 1
