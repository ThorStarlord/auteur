@echo off
setlocal
cd /d "%~dp0"

where auteur >nul 2>nul
if %errorlevel%==0 (
  auteur open --project "%CD%"
  exit /b %errorlevel%
)

set "PYTHONPATH=%CD%\src;%PYTHONPATH%"
python -m auteur.cli open --project "%CD%"
exit /b %errorlevel%
