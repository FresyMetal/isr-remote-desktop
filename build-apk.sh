#!/bin/bash

# Script de Compilación Automatizada de APK
# ISR Remote Desktop - Android

echo "🚀 ISR Remote Desktop - Compilación de APK"
echo "=========================================="
echo ""

# Colores para output
RED='\033[0:31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar si Node.js está instalado
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Error: Node.js no está instalado${NC}"
    echo "Por favor, instala Node.js desde: https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✓${NC} Node.js encontrado: $(node --version)"

# Verificar si pnpm está instalado
if ! command -v pnpm &> /dev/null; then
    echo -e "${YELLOW}⚠${NC}  pnpm no encontrado, instalando..."
    npm install -g pnpm
fi

echo -e "${GREEN}✓${NC} pnpm encontrado: $(pnpm --version)"

# Verificar si EAS CLI está instalado
if ! command -v eas &> /dev/null; then
    echo -e "${YELLOW}⚠${NC}  EAS CLI no encontrado, instalando..."
    npm install -g eas-cli
fi

echo -e "${GREEN}✓${NC} EAS CLI encontrado: $(eas --version)"
echo ""

# Verificar si el usuario está logueado en Expo
echo "🔐 Verificando sesión de Expo..."
if ! eas whoami &> /dev/null; then
    echo -e "${YELLOW}⚠${NC}  No has iniciado sesión en Expo"
    echo "Por favor, inicia sesión:"
    eas login
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Error al iniciar sesión${NC}"
        exit 1
    fi
fi

EXPO_USER=$(eas whoami)
echo -e "${GREEN}✓${NC} Sesión activa como: $EXPO_USER"
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

# Preguntar qué tipo de build quiere el usuario
echo "📱 Selecciona el tipo de compilación:"
echo "1) Desarrollo (con debugging, más grande)"
echo "2) Producción (optimizado, más pequeño)"
echo "3) Preview (para pruebas internas)"
echo "4) Local (compila en este equipo, requiere Android SDK)"
echo ""
read -p "Selecciona una opción (1-4): " BUILD_TYPE

case $BUILD_TYPE in
    1)
        PROFILE="development"
        echo -e "${YELLOW}📱 Compilando APK de Desarrollo...${NC}"
        ;;
    2)
        PROFILE="production"
        echo -e "${YELLOW}📱 Compilando APK de Producción...${NC}"
        ;;
    3)
        PROFILE="preview"
        echo -e "${YELLOW}📱 Compilando APK de Preview...${NC}"
        ;;
    4)
        PROFILE="preview"
        LOCAL_FLAG="--local"
        echo -e "${YELLOW}📱 Compilando APK Localmente...${NC}"
        echo -e "${YELLOW}⚠${NC}  Esto requiere Android Studio y Android SDK instalados"
        ;;
    *)
        echo -e "${RED}❌ Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo "🔨 Iniciando compilación..."
echo "Esto puede tardar 10-20 minutos..."
echo ""

# Ejecutar build
eas build --platform android --profile $PROFILE $LOCAL_FLAG

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ ¡Compilación exitosa!${NC}"
    echo ""
    echo "📥 Descarga el APK desde el enlace proporcionado arriba"
    echo "📱 Transfiere el APK a tu móvil Android"
    echo "⚙️  Habilita 'Fuentes desconocidas' en Ajustes → Seguridad"
    echo "📲 Abre el APK en tu móvil y toca 'Instalar'"
    echo ""
    echo "🎉 ¡Listo! La app ISR Remote Desktop estará instalada"
else
    echo ""
    echo -e "${RED}❌ Error en la compilación${NC}"
    echo ""
    echo "Para ver los detalles del error:"
    echo "  eas build:list"
    echo "  eas build:view [BUILD_ID]"
    echo ""
    echo "Consulta COMPILAR_APK.md para solución de problemas"
    exit 1
fi
