#!/bin/bash

# Script de Compilación Local de APK Standalone
# ISR Remote Desktop - Android (Sin Expo)

echo "🚀 ISR Remote Desktop - Compilación Local de APK"
echo "================================================"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js no está instalado${NC}"
    echo "Descarga desde: https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✓${NC} Node.js: $(node --version)"

# Verificar Java
if ! command -v java &> /dev/null; then
    echo -e "${RED}❌ Java JDK no está instalado${NC}"
    echo "Instala Java JDK 17:"
    echo "  - Windows: https://adoptium.net/"
    echo "  - Linux: sudo apt install openjdk-17-jdk"
    echo "  - macOS: brew install openjdk@17"
    exit 1
fi

JAVA_VERSION=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}')
echo -e "${GREEN}✓${NC} Java: $JAVA_VERSION"

# Verificar ANDROID_HOME
if [ -z "$ANDROID_HOME" ]; then
    echo -e "${YELLOW}⚠${NC}  ANDROID_HOME no está configurado"
    echo ""
    echo "Por favor, instala Android Studio y configura:"
    echo ""
    echo "  export ANDROID_HOME=\$HOME/Android/Sdk"
    echo "  export PATH=\$PATH:\$ANDROID_HOME/emulator"
    echo "  export PATH=\$PATH:\$ANDROID_HOME/platform-tools"
    echo "  export PATH=\$PATH:\$ANDROID_HOME/tools"
    echo "  export PATH=\$PATH:\$ANDROID_HOME/tools/bin"
    echo ""
    echo "Añade estas líneas a ~/.bashrc o ~/.zshrc"
    exit 1
fi

echo -e "${GREEN}✓${NC} ANDROID_HOME: $ANDROID_HOME"

# Verificar que exista el SDK
if [ ! -d "$ANDROID_HOME/platforms" ]; then
    echo -e "${RED}❌ Android SDK no encontrado en $ANDROID_HOME${NC}"
    echo "Instala Android Studio y el SDK de Android"
    exit 1
fi

echo -e "${GREEN}✓${NC} Android SDK encontrado"
echo ""

# Instalar dependencias
echo "📦 Instalando dependencias..."
pnpm install

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error al instalar dependencias${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Dependencias instaladas"
echo ""

# Preguntar tipo de build
echo "📱 Selecciona el tipo de APK:"
echo "1) Debug (con herramientas de desarrollo)"
echo "2) Release (optimizado para producción)"
echo ""
read -p "Selecciona (1-2): " BUILD_TYPE

case $BUILD_TYPE in
    1)
        BUILD_VARIANT="assembleDebug"
        APK_PATH="android/app/build/outputs/apk/debug/app-debug.apk"
        echo -e "${BLUE}🔨 Compilando APK Debug...${NC}"
        ;;
    2)
        BUILD_VARIANT="assembleRelease"
        APK_PATH="android/app/build/outputs/apk/release/app-release-unsigned.apk"
        echo -e "${BLUE}🔨 Compilando APK Release...${NC}"
        ;;
    *)
        echo -e "${RED}❌ Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""

# Navegar al directorio android
cd android

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
./gradlew clean

# Compilar APK
echo "⚙️  Compilando APK (esto puede tardar varios minutos)..."
echo ""

./gradlew $BUILD_VARIANT

if [ $? -eq 0 ]; then
    cd ..
    echo ""
    echo -e "${GREEN}✅ ¡Compilación exitosa!${NC}"
    echo ""
    echo "📦 APK generado en:"
    echo -e "${BLUE}   $APK_PATH${NC}"
    echo ""
    
    # Mostrar tamaño del APK
    APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
    echo "📊 Tamaño: $APK_SIZE"
    echo ""
    
    # Instrucciones de instalación
    echo "📱 Para instalar en tu móvil:"
    echo ""
    echo "1. Conecta tu móvil por USB y habilita 'Depuración USB'"
    echo "2. Ejecuta:"
    echo -e "${BLUE}   adb install $APK_PATH${NC}"
    echo ""
    echo "O transfiere el APK a tu móvil y ábrelo para instalarlo"
    echo ""
    
    # Si es release, mostrar advertencia sobre firma
    if [ "$BUILD_TYPE" == "2" ]; then
        echo -e "${YELLOW}⚠${NC}  El APK Release no está firmado"
        echo "Para distribuirlo, debes firmarlo con tu keystore:"
        echo ""
        echo "  jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \\"
        echo "    -keystore my-release-key.keystore \\"
        echo "    $APK_PATH alias_name"
        echo ""
    fi
    
    echo -e "${GREEN}🎉 ¡Listo!${NC}"
else
    cd ..
    echo ""
    echo -e "${RED}❌ Error en la compilación${NC}"
    echo ""
    echo "Revisa los errores arriba para más detalles"
    exit 1
fi
