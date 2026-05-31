@echo off
setlocal
title Build W-MIDI Launcher

set "REPO_ROOT=%~dp0..\.."
set "SOURCE=%REPO_ROOT%\tools\windows\GuiLauncher.cs"
set "OUTPUT=%REPO_ROOT%\W-MIDI.exe"
set "ICON=%REPO_ROOT%\assets\windows\w-midi.ico"

set "CSC_EXE="
for %%C in (
  "%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
  "%WINDIR%\Microsoft.NET\Framework\v4.0.30319\csc.exe"
) do (
  if exist "%%~C" set "CSC_EXE=%%~C"
)

if not defined CSC_EXE (
  for /f "delims=" %%C in ('where csc 2^>nul') do if not defined CSC_EXE set "CSC_EXE=%%C"
)

if not defined CSC_EXE (
  echo csc.exe was not found. Install Visual Studio Build Tools or use a Developer Command Prompt.
  exit /b 1
)

if not exist "%ICON%" (
  echo Icon file not found: %ICON%
  exit /b 1
)

"%CSC_EXE%" /nologo /target:winexe /win32icon:"%ICON%" /out:"%OUTPUT%" "%SOURCE%" /reference:System.Windows.Forms.dll
exit /b %ERRORLEVEL%
