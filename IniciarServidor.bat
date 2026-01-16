@echo off
REM Script para iniciar el servidor sin compilar

REM Cambiar al directorio donde está el script
cd /d "%~dp0"

echo ========================================
echo   SERVIDOR DE ESCRITORIO REMOTO
echo ========================================
echo.
echo Directorio: %CD%
echo.
echo Iniciando servidor en puerto 5900...
echo Presiona Ctrl+C para detener el servidor
echo.
echo ========================================
echo.

py server.py

pause
