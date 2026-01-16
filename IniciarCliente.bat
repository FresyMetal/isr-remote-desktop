@echo off
REM Script para iniciar el cliente sin compilar

REM Cambiar al directorio donde está el script
cd /d "%~dp0"

echo ========================================
echo   CLIENTE DE ESCRITORIO REMOTO
echo ========================================
echo.
echo Directorio: %CD%
echo.
echo Iniciando cliente...
echo.

py client.py

pause
