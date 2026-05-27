@echo off
setlocal
title W-MIDI
set "REPO_ROOT=%~dp0..\.."
pushd "%REPO_ROOT%"
py -3 -m midi_wled_bridge.gui
set "EXIT_CODE=%ERRORLEVEL%"
popd
pause
exit /b %EXIT_CODE%
