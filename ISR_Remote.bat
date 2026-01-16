@echo off
REM ISR Remote Desktop - Aplicacion Unificada
REM Cambiar al directorio donde esta el script
cd /d "%~dp0"

echo ========================================
echo   ISR REMOTE DESKTOP
echo ========================================
echo.
echo Directorio: %CD%
echo.

REM Ejecutar la aplicacion
py isr_remote.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo   ERROR
    echo ========================================
    echo.
    echo No se pudo iniciar la aplicacion.
    echo.
    echo Posibles causas:
    echo   - Python no esta instalado
    echo   - Faltan dependencias
    echo.
    echo Soluciones:
    echo   1. Instala Python 3.11+ desde python.org
    echo   2. Ejecuta: instalar_dependencias.bat
    echo.
    pause
)
