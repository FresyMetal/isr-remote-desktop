@echo off
REM Script para compilar solo el servidor

REM Cambiar al directorio donde está el script
cd /d "%~dp0"

echo ========================================
echo   COMPILANDO SERVIDOR
echo ========================================
echo.
echo Directorio: %CD%
echo.
echo IMPORTANTE: NO ejecutes este script como administrador.
echo PyInstaller debe ejecutarse como usuario normal.
echo.
echo Si ejecutaste como administrador, cierra esta ventana
echo y ejecuta con doble clic (sin administrador).
echo.
echo ========================================
echo.

REM Limpiar compilaciones anteriores
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist RemoteDesktopServer.spec del /q RemoteDesktopServer.spec

echo Limpiando archivos anteriores...
echo.

REM Compilar con PyInstaller
echo Compilando servidor...
echo Esto puede tardar varios minutos...
echo.

py -m PyInstaller ^
    --name=RemoteDesktopServer ^
    --onefile ^
    --console ^
    --hidden-import=mss ^
    --hidden-import=mss.windows ^
    --hidden-import=pynput ^
    --hidden-import=pynput.keyboard ^
    --hidden-import=pynput.mouse ^
    --hidden-import=pyperclip ^
    --hidden-import=zstandard ^
    --hidden-import=cryptography ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --collect-all=mss ^
    --collect-all=pynput ^
    server.py

echo.
echo ========================================
if exist dist\RemoteDesktopServer.exe (
    echo   EXITO: Servidor compilado
    echo   Ubicacion: dist\RemoteDesktopServer.exe
    echo.
    echo   Para ejecutar:
    echo   1. Clic derecho en dist\RemoteDesktopServer.exe
    echo   2. "Ejecutar como administrador"
) else (
    echo   ERROR: No se pudo compilar el servidor
    echo.
    echo   Posibles causas:
    echo   - PyInstaller no esta instalado: py -m pip install pyinstaller
    echo   - Falta alguna dependencia: py -m pip install -r requirements.txt
    echo   - Ejecutaste como administrador (no hagas eso)
)
echo ========================================
echo.
pause
