@echo off
REM Script para compilar solo el cliente

REM Cambiar al directorio donde está el script
cd /d "%~dp0"

echo ========================================
echo   COMPILANDO CLIENTE
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
if exist RemoteDesktopClient.spec del /q RemoteDesktopClient.spec

echo Limpiando archivos anteriores...
echo.

REM Compilar con PyInstaller
echo Compilando cliente...
echo Esto puede tardar varios minutos...
echo.

py -m PyInstaller ^
    --name=RemoteDesktopClient ^
    --onefile ^
    --windowed ^
    --hidden-import=PyQt6 ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=pyperclip ^
    --hidden-import=zstandard ^
    --hidden-import=cryptography ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --collect-all=PyQt6 ^
    client.py

echo.
echo ========================================
if exist dist\RemoteDesktopClient.exe (
    echo   EXITO: Cliente compilado
    echo   Ubicacion: dist\RemoteDesktopClient.exe
    echo.
    echo   Para ejecutar:
    echo   - Doble clic en dist\RemoteDesktopClient.exe
    echo   - NO necesita ejecutarse como administrador
) else (
    echo   ERROR: No se pudo compilar el cliente
    echo.
    echo   Posibles causas:
    echo   - PyInstaller no esta instalado: py -m pip install pyinstaller
    echo   - Falta alguna dependencia: py -m pip install -r requirements.txt
    echo   - Ejecutaste como administrador (no hagas eso)
)
echo ========================================
echo.
pause
