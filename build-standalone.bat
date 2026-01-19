@echo off
REM Script de Compilación Local de APK Standalone
REM ISR Remote Desktop - Android (Sin Expo) - Windows

echo ========================================
echo ISR Remote Desktop - Compilacion Local
echo ========================================
echo.

REM Verificar Node.js
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js no esta instalado
    echo Descarga desde: https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Node.js encontrado
node --version

REM Verificar Java
where java >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Java JDK no esta instalado
    echo Descarga desde: https://adoptium.net/
    pause
    exit /b 1
)

echo [OK] Java encontrado
java -version

REM Verificar ANDROID_HOME
if "%ANDROID_HOME%"=="" (
    echo [ERROR] ANDROID_HOME no esta configurado
    echo.
    echo Por favor, instala Android Studio y configura:
    echo   ANDROID_HOME=C:\Users\TuUsuario\AppData\Local\Android\Sdk
    echo.
    echo Agrega esta variable de entorno en:
    echo   Panel de Control ^> Sistema ^> Configuracion avanzada ^> Variables de entorno
    pause
    exit /b 1
)

echo [OK] ANDROID_HOME: %ANDROID_HOME%

REM Verificar SDK
if not exist "%ANDROID_HOME%\platforms" (
    echo [ERROR] Android SDK no encontrado en %ANDROID_HOME%
    echo Instala Android Studio y el SDK de Android
    pause
    exit /b 1
)

echo [OK] Android SDK encontrado
echo.

REM Instalar dependencias
echo Instalando dependencias...
call pnpm install

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Error al instalar dependencias
    pause
    exit /b 1
)

echo [OK] Dependencias instaladas
echo.

REM Preguntar tipo de build
echo Selecciona el tipo de APK:
echo 1) Debug (con herramientas de desarrollo)
echo 2) Release (optimizado para produccion)
echo.
set /p BUILD_TYPE="Selecciona (1-2): "

if "%BUILD_TYPE%"=="1" (
    set BUILD_VARIANT=assembleDebug
    set APK_PATH=android\app\build\outputs\apk\debug\app-debug.apk
    echo.
    echo Compilando APK Debug...
) else if "%BUILD_TYPE%"=="2" (
    set BUILD_VARIANT=assembleRelease
    set APK_PATH=android\app\build\outputs\apk\release\app-release-unsigned.apk
    echo.
    echo Compilando APK Release...
) else (
    echo [ERROR] Opcion invalida
    pause
    exit /b 1
)

echo.

REM Navegar a android
cd android

REM Limpiar builds anteriores
echo Limpiando builds anteriores...
call gradlew.bat clean

REM Compilar APK
echo Compilando APK (esto puede tardar varios minutos)...
echo.

call gradlew.bat %BUILD_VARIANT%

if %ERRORLEVEL% EQ 0 (
    cd ..
    echo.
    echo ========================================
    echo [OK] Compilacion exitosa!
    echo ========================================
    echo.
    echo APK generado en:
    echo   %APK_PATH%
    echo.
    
    REM Mostrar tamaño
    for %%A in ("%APK_PATH%") do echo Tamano: %%~zA bytes
    echo.
    
    echo Para instalar en tu movil:
    echo.
    echo 1. Conecta tu movil por USB y habilita 'Depuracion USB'
    echo 2. Ejecuta:
    echo    adb install %APK_PATH%
    echo.
    echo O transfiere el APK a tu movil y abrelo para instalarlo
    echo.
    
    if "%BUILD_TYPE%"=="2" (
        echo [AVISO] El APK Release no esta firmado
        echo Para distribuirlo, debes firmarlo con tu keystore
        echo.
    )
    
    echo Listo!
    pause
) else (
    cd ..
    echo.
    echo [ERROR] Error en la compilacion
    echo.
    echo Revisa los errores arriba para mas detalles
    pause
    exit /b 1
)
