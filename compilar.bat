@echo off
setlocal enabledelayedexpansion

REM Cambiar al directorio del script
cd /d "%~dp0"

echo ========================================
echo   COMPILAR APLICACION DE ESCRITORIO REMOTO
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
echo   COMPILANDO SERVIDOR
echo ========================================
echo.
echo Esto puede tardar varios minutos, por favor espera...
echo.

REM Compilar servidor usando ruta corta
py -m PyInstaller --onefile --console --name RemoteDesktopServer --icon=icon.ico server.py >build\server_build.log 2>&1

if exist dist\RemoteDesktopServer.exe (
    echo [OK] Servidor compilado correctamente
    echo      Ubicacion: dist\RemoteDesktopServer.exe
) else (
    echo [ERROR] No se pudo compilar el servidor
    echo.
    echo Revisa el log en: build\server_build.log
    echo.
    type build\server_build.log | findstr /i "error"
    pause
    exit /b 1
)

echo.
echo ========================================
echo   COMPILANDO CLIENTE
echo ========================================
echo.
echo Esto puede tardar varios minutos, por favor espera...
echo.

REM Compilar cliente
py -m PyInstaller --onefile --windowed --name RemoteDesktopClient --icon=icon.ico client.py >build\client_build.log 2>&1

if exist dist\RemoteDesktopClient.exe (
    echo [OK] Cliente compilado correctamente
    echo      Ubicacion: dist\RemoteDesktopClient.exe
) else (
    echo [ERROR] No se pudo compilar el cliente
    echo.
    echo Revisa el log en: build\client_build.log
    echo.
    type build\client_build.log | findstr /i "error"
    pause
    exit /b 1
)

echo.
echo ========================================
echo   COMPILACION COMPLETADA EXITOSAMENTE
echo ========================================
echo.
echo Archivos generados:
echo.
dir /b dist\*.exe 2>nul
echo.
echo Ubicacion completa:
echo %CD%\dist\
echo.
echo ========================================
echo   COMO EJECUTAR
echo ========================================
echo.
echo SERVIDOR:
echo   1. Ve a la carpeta: dist\
echo   2. Clic derecho en: RemoteDesktopServer.exe
echo   3. Selecciona: "Ejecutar como administrador"
echo.
echo CLIENTE:
echo   1. Ve a la carpeta: dist\
echo   2. Doble clic en: RemoteDesktopClient.exe
echo.
echo ========================================
echo.

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
