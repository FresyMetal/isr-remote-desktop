# Guía de Compilación Standalone (Sin Expo)

Esta guía te ayudará a compilar un APK completamente independiente de Expo que podrás instalar en cualquier dispositivo Android sin necesidad de Expo Go ni servidores externos.

## 📋 Requisitos Previos

### 1. Node.js
- **Versión:** 18 o superior
- **Descarga:** https://nodejs.org/

### 2. Java JDK
- **Versión:** 17 (recomendado)
- **Windows:** https://adoptium.net/
- **Linux:** `sudo apt install openjdk-17-jdk`
- **macOS:** `brew install openjdk@17`

### 3. Android Studio
- **Descarga:** https://developer.android.com/studio
- **Componentes necesarios:**
  - Android SDK Platform 34
  - Android SDK Build-Tools 34.0.0
  - Android SDK Platform-Tools
  - Android SDK Tools

### 4. Variables de Entorno

#### Windows:
```cmd
set ANDROID_HOME=C:\Users\TuUsuario\AppData\Local\Android\Sdk
set PATH=%PATH%;%ANDROID_HOME%\platform-tools
set PATH=%PATH%;%ANDROID_HOME%\tools
```

#### Linux/macOS:
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
```

Añade estas líneas a `~/.bashrc` o `~/.zshrc` para que sean permanentes.

## 🚀 Compilación Rápida

### Método 1: Script Automatizado (Recomendado)

#### Windows:
```cmd
build-standalone.bat
```

#### Linux/macOS:
```bash
./build-standalone.sh
```

El script te guiará paso a paso y generará el APK automáticamente.

### Método 2: Compilación Manual

#### Paso 1: Instalar Dependencias
```bash
pnpm install
```

#### Paso 2: Limpiar Builds Anteriores
```bash
cd android
./gradlew clean
```

#### Paso 3: Compilar APK

**APK Debug (con herramientas de desarrollo):**
```bash
./gradlew assembleDebug
```

El APK se generará en:
```
android/app/build/outputs/apk/debug/app-debug.apk
```

**APK Release (optimizado para producción):**
```bash
./gradlew assembleRelease
```

El APK se generará en:
```
android/app/build/outputs/apk/release/app-release-unsigned.apk
```

## 📱 Instalación del APK

### Opción 1: Instalación por USB (ADB)

1. **Habilita Depuración USB** en tu móvil:
   - Ajustes → Acerca del teléfono → Toca 7 veces en "Número de compilación"
   - Ajustes → Opciones de desarrollador → Depuración USB → Activar

2. **Conecta tu móvil** por USB al PC

3. **Verifica la conexión**:
   ```bash
   adb devices
   ```

4. **Instala el APK**:
   ```bash
   adb install android/app/build/outputs/apk/debug/app-debug.apk
   ```

### Opción 2: Instalación Manual

1. **Transfiere el APK** a tu móvil (por cable USB, email, Drive, etc.)

2. **Habilita instalación de fuentes desconocidas**:
   - Ajustes → Seguridad → Fuentes desconocidas → Activar
   - O Ajustes → Aplicaciones → Acceso especial → Instalar aplicaciones desconocidas

3. **Abre el APK** en tu móvil usando un explorador de archivos

4. **Toca "Instalar"**

## 🔒 Firmar APK Release (Para Distribución)

Si quieres distribuir el APK Release, debes firmarlo:

### Paso 1: Crear Keystore

```bash
keytool -genkey -v -keystore my-release-key.keystore \
  -alias my-key-alias \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000
```

### Paso 2: Firmar el APK

```bash
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
  -keystore my-release-key.keystore \
  android/app/build/outputs/apk/release/app-release-unsigned.apk \
  my-key-alias
```

### Paso 3: Alinear el APK (Opcional pero recomendado)

```bash
zipalign -v 4 \
  android/app/build/outputs/apk/release/app-release-unsigned.apk \
  android/app/build/outputs/apk/release/app-release.apk
```

## 🔧 Solución de Problemas

### Error: "ANDROID_HOME is not set"

**Solución:**
1. Instala Android Studio
2. Abre Android Studio → SDK Manager
3. Anota la ruta del SDK (ej: `C:\Users\Usuario\AppData\Local\Android\Sdk`)
4. Configura la variable de entorno `ANDROID_HOME` con esa ruta

### Error: "SDK location not found"

**Solución:**
Crea el archivo `android/local.properties` con:
```
sdk.dir=C:\\Users\\TuUsuario\\AppData\\Local\\Android\\Sdk
```

(En Linux/macOS usa `/` en lugar de `\\`)

### Error: "Gradle build failed"

**Solución:**
1. Limpia el proyecto:
   ```bash
   cd android
   ./gradlew clean
   ```

2. Verifica que tengas instalado:
   - Android SDK Platform 34
   - Android SDK Build-Tools 34.0.0

3. Sincroniza Gradle:
   ```bash
   ./gradlew --refresh-dependencies
   ```

### Error: "Java version incompatible"

**Solución:**
Asegúrate de tener Java JDK 17:
```bash
java -version
```

Si tienes otra versión, instala JDK 17 y configura `JAVA_HOME`.

### APK muy grande (>100 MB)

**Solución:**
Compila el APK Release en lugar del Debug:
```bash
./gradlew assembleRelease
```

El APK Release está optimizado y es mucho más pequeño.

## 📊 Comparación de Tipos de APK

| Tipo | Tamaño | Optimización | Debugging | Uso Recomendado |
|------|--------|--------------|-----------|-----------------|
| **Debug** | ~80 MB | Baja | Sí | Desarrollo y pruebas |
| **Release** | ~40 MB | Alta | No | Distribución final |

## 🎯 APK Generado - Características

El APK standalone incluye:

- ✅ **Totalmente independiente** - No requiere Expo Go
- ✅ **Sin servidores externos** - No usa servidores de Expo
- ✅ **Conexión TCP nativa** - Protocolo binario optimizado
- ✅ **Todas las funcionalidades**:
  - Visualización en tiempo real del escritorio
  - Controles táctiles (tap, arrastrar, scroll, zoom)
  - Teclado virtual con teclas especiales
  - Selector de calidad de video
  - Selector de monitores
  - Portapapeles bidireccional
- ✅ **Funciona offline** - Solo necesita red local con el PC

## 📦 Distribución

### Para Uso Personal:
- Instala el APK Debug directamente en tus dispositivos

### Para Distribución Privada:
- Firma el APK Release con tu keystore
- Comparte el APK firmado por email, Drive, etc.

### Para Google Play Store:
1. Genera un AAB en lugar de APK:
   ```bash
   ./gradlew bundleRelease
   ```

2. El AAB se generará en:
   ```
   android/app/build/outputs/bundle/release/app-release.aab
   ```

3. Sube el AAB a Google Play Console

## 🆘 Soporte

Si encuentras problemas:

1. **Revisa los logs de compilación** - Busca líneas con "ERROR" o "FAILED"
2. **Verifica requisitos** - Asegúrate de tener todo instalado
3. **Limpia y recompila** - `./gradlew clean` y vuelve a compilar

## 🎉 ¡Listo!

Una vez compilado e instalado, tendrás una app completamente independiente que podrás usar para controlar tus PCs remotamente sin necesidad de Expo Go ni servicios externos.

---

**Versión:** 1.0.0  
**Última actualización:** Enero 2026  
**Plataforma:** Android 5.0+ (API Level 21+)
