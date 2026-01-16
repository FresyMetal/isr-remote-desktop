@echo off
setlocal enabledelayedexpansion

REM Cambiar al directorio del script
cd /d "%~dp0"

echo ========================================
echo   COMPILAR ISR REMOTE DESKTOP
echo   Aplicacion Unificada v3.0
echo ========================================
echo.
echo Directorio: %CD%
echo.

REM Verificar que PyInstaller esté instalado
py -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Instalando PyInstaller...
    py -m pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: No se pudo instalar PyInstaller
        pause
        exit /b 1
    )
)

REM Limpiar archivos anteriores
echo Limpiando archivos anteriores...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
if exist *.spec del /q *.spec 2>nul

REM Crear directorios
mkdir build 2>nul
mkdir dist 2>nul

echo.
echo ========================================
echo   COMPILANDO APLICACION UNIFICADA
echo ========================================
echo.
echo Esto puede tardar 5-10 minutos, por favor espera...
echo.

REM Compilar aplicación unificada
py -m PyInstaller --onefile --windowed --name ISR_Remote_Desktop --icon=icon.ico isr_remote.py >build\build.log 2>&1

if exist dist\ISR_Remote_Desktop.exe (
    echo.
    echo ========================================
    echo   COMPILACION EXITOSA
    echo ========================================
    echo.
    echo Archivo generado:
    echo   ISR_Remote_Desktop.exe
    echo.
    echo Ubicacion:
    echo   %CD%\dist\ISR_Remote_Desktop.exe
    echo.
    echo Tamano:
    for %%F in (dist\ISR_Remote_Desktop.exe) do echo   %%~zF bytes
    echo.
    echo ========================================
    echo   COMO USAR
    echo ========================================
    echo.
    echo 1. Ve a la carpeta: dist\
    echo 2. Ejecuta: ISR_Remote_Desktop.exe
    echo.
    echo NOTA: Para permitir control remoto (servidor),
    echo       ejecuta como administrador.
    echo.
    echo ========================================
    echo.
) else (
    echo.
    echo ========================================
    echo   ERROR EN LA COMPILACION
    echo ========================================
    echo.
    echo No se pudo compilar la aplicacion.
    echo.
    echo Revisa el log en: build\build.log
    echo.
    echo Ultimos errores:
    type build\build.log | findstr /i "error"
    echo.
    pause
    exit /b 1
)

REM Limpiar archivos temporales opcionales
choice /c SN /n /m "Deseas limpiar archivos temporales (build, spec)? [S/N]: "
if errorlevel 2 goto :end
if errorlevel 1 (
    echo.
    echo Limpiando archivos temporales...
    rmdir /s /q build 2>nul
    del /q *.spec 2>nul
    echo Listo.
)

:end
echo.
pause
