# Guía para Compilar APK de ISR Remote Desktop

Esta guía te ayudará a generar un APK nativo de Android para instalar la aplicación directamente en tu móvil sin necesidad de Expo Go.

## 📋 Requisitos Previos

1. **Node.js** instalado (versión 18 o superior)
2. **Cuenta de Expo** (gratuita) - [Crear cuenta](https://expo.dev/signup)
3. **EAS CLI** instalado globalmente

## 🚀 Paso 1: Instalar EAS CLI

Abre una terminal y ejecuta:

```bash
npm install -g eas-cli
```

## 🔐 Paso 2: Iniciar Sesión en Expo

```bash
eas login
```

Introduce tu email y contraseña de Expo.

## ⚙️ Paso 3: Configurar el Proyecto

Navega a la carpeta del proyecto:

```bash
cd /ruta/a/isr-remote-android
```

Configura EAS Build:

```bash
eas build:configure
```

Esto creará automáticamente el archivo `eas.json` (ya está incluido en el proyecto).

## 📱 Paso 4: Generar el APK

### Opción A: APK de Desarrollo (Recomendado para pruebas)

```bash
eas build --platform android --profile development
```

### Opción B: APK de Producción (Para distribución)

```bash
eas build --platform android --profile production
```

### Opción C: APK Local (Sin servidores de Expo)

```bash
eas build --platform android --profile preview --local
```

**Nota:** La compilación local requiere tener Android Studio y el SDK de Android instalados.

## ⏱️ Paso 5: Esperar la Compilación

- La compilación en servidores de Expo tarda **10-20 minutos**
- Recibirás un enlace de descarga cuando termine
- Puedes ver el progreso en: https://expo.dev/accounts/[tu-usuario]/projects/isr-remote-android/builds

## 📥 Paso 6: Descargar e Instalar el APK

1. **Descarga el APK** desde el enlace proporcionado
2. **Transfiere el APK** a tu móvil Android (por cable USB, email, Drive, etc.)
3. **Habilita instalación de fuentes desconocidas**:
   - Ajustes → Seguridad → Fuentes desconocidas → Activar
4. **Abre el APK** en tu móvil y toca "Instalar"

## 🔧 Solución de Problemas

### Error: "No Android credentials found"

EAS Build necesita credenciales para firmar el APK. Ejecuta:

```bash
eas credentials
```

Y sigue las instrucciones para generar o subir tus credenciales.

### Error: "Build failed"

Revisa los logs de compilación en:

```bash
eas build:list
```

Y luego:

```bash
eas build:view [BUILD_ID]
```

### Compilación Local Falla

Asegúrate de tener instalado:

1. **Android Studio**
2. **Android SDK** (API Level 34)
3. **Java JDK 17**

Variables de entorno necesarias:

```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

## 🎯 Método Alternativo: Compilación con Android Studio

Si prefieres compilar localmente sin EAS Build:

1. **Genera el proyecto nativo**:

```bash
npx expo prebuild --platform android
```

2. **Abre el proyecto en Android Studio**:

```bash
cd android
studio .
```

3. **Compila el APK**:
   - Build → Build Bundle(s) / APK(s) → Build APK(s)
   - El APK se generará en: `android/app/build/outputs/apk/release/`

## 📦 Archivos Generados

- **APK de desarrollo**: `app-development.apk` (~50-80 MB)
- **APK de producción**: `app-release.apk` (~30-50 MB)
- **AAB (Google Play)**: `app-release.aab` (~25-40 MB)

## 🔒 Notas de Seguridad

- El APK de desarrollo incluye herramientas de debugging
- El APK de producción está optimizado y firmado
- **No compartas** tus credenciales de firma de Android

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs de compilación
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de tener la última versión de EAS CLI: `npm install -g eas-cli@latest`

## 🎉 ¡Listo!

Una vez instalado el APK, podrás usar ISR Remote Desktop sin necesidad de Expo Go.

**Características incluidas en el APK:**

- ✅ Conexión TCP nativa al servidor de escritorio remoto
- ✅ Visualización en tiempo real del escritorio
- ✅ Controles táctiles (tap, arrastrar, scroll, zoom)
- ✅ Teclado virtual con teclas especiales
- ✅ Selector de calidad de video
- ✅ Selector de monitores (si el PC tiene múltiples pantallas)
- ✅ Portapapeles bidireccional
- ✅ Funciona sin conexión a Internet (solo necesita red local)

---

**Versión:** 1.0.0  
**Última actualización:** Enero 2026
