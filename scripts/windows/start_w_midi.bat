@echo off
setlocal
title W-MIDI
set "REPO_ROOT=%~dp0..\.."
pushd "%REPO_ROOT%"
<<<<<<< HEAD
py -3 -m midi_wled_bridge.qt_gui
=======
py -3 -m midi_wled_bridge.gui
>>>>>>> eabdd911b25d79a2bbd5c264e3d24a69dda49ce7
set "EXIT_CODE=%ERRORLEVEL%"
popd
pause
exit /b %EXIT_CODE%
