@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

where node >nul 2>nul || (
  echo Missing required command: node
  exit /b 1
)

node "%SCRIPT_DIR%\scripts\configure-openclaw-uninstall.mjs" %*
exit /b %ERRORLEVEL%
