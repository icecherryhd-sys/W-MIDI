@echo off
setlocal

set "WLED_IP=192.168.178.116"
set "WLED_PORT=21324"
set "UDP_TIMEOUT=2"
set "LED_COUNT=89"
set "COLOR_R=0"
set "COLOR_G=120"
set "COLOR_B=255"

set "PY_EXE="
if exist "C:\Users\maier\AppData\Local\Programs\Python\Launcher\py.exe" (
  set "PY_EXE=C:\Users\maier\AppData\Local\Programs\Python\Launcher\py.exe"
) else if exist "C:\Users\maier\AppData\Local\Programs\Python\Python312\python.exe" (
  set "PY_EXE=C:\Users\maier\AppData\Local\Programs\Python\Python312\python.exe"
) else (
  set "PY_EXE=python"
)

echo Sending UDP DRGB test frame to %WLED_IP%:%WLED_PORT% ...
echo LEDs: %LED_COUNT%  Color: %COLOR_R%,%COLOR_G%,%COLOR_B%
echo.

call "%PY_EXE%" -c "import socket; ip='%WLED_IP%'; port=int('%WLED_PORT%'); timeout=int('%UDP_TIMEOUT%'); n=int('%LED_COUNT%'); r=int('%COLOR_R%'); g=int('%COLOR_G%'); b=int('%COLOR_B%'); payload=bytes([2, timeout])+bytes([r,g,b])*n; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.sendto(payload,(ip,port)); s.close(); print('Sent', len(payload), 'bytes to', ip, port, 'timeout', timeout)"
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if not "%EXIT_CODE%"=="0" (
  echo Test failed with error code %EXIT_CODE%.
) else (
  echo Test packet sent. If WLED did not change, check IP, UDP Realtime, and firewall.
)
pause
exit /b %EXIT_CODE%
