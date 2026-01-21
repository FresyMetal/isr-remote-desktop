# 🔨 Guía de Compilación Local - ISR Remote Desktop Android

## 📋 Requisitos Previos

### 1. Instalar Node.js
- Descargar desde: https://nodejs.org/
- Versión recomendada: 18.x o superior
- Verificar instalación: `node --version`

### 2. Instalar Android Studio
- Descargar desde: https://developer.android.com/studio
- Durante la instalación, asegúrate de instalar:
  - Android SDK
  - Android SDK Platform
  - Android Virtual Device (opcional, para emulador)

### 3. Configurar Variables de Entorno

Agregar a las variables de entorno de Windows:

```
ANDROID_HOME=C:\Users\TU_USUARIO\AppData\Local\Android\Sdk
JAVA_HOME=C:\Program Files\Android\Android Studio\jbr
```

Agregar al PATH:
```
%ANDROID_HOME%\platform-tools
%ANDROID_HOME%\tools
%JAVA_HOME%\bin
```

---

## 🚀 Pasos para Compilar

### 1. Descargar el Proyecto

Descarga el proyecto desde Manus o clona el repositorio.

### 2. Instalar Dependencias

```cmd
cd isr-remote-android
npm install
```

O si usas pnpm:
```cmd
pnpm install
```

### 3. Generar Proyecto Android Nativo

```cmd
npx expo prebuild --platform android --clean
```

Este comando genera la carpeta `android/` con el proyecto nativo.

### 4. Compilar el APK

```cmd
cd android
gradlew assembleRelease
```

O en Windows:
```cmd
cd android
.\gradlew.bat assembleRelease
```

### 5. Encontrar el APK

El APK se generará en:
```
android\app\build\outputs\apk\release\app-release.apk
```

---

## 📱 Instalar en Android

### Opción A: Transferir por USB

1. Habilita "Depuración USB" en tu Android:
   - Ajustes → Acerca del teléfono → Toca 7 veces en "Número de compilación"
   - Ajustes → Opciones de desarrollador → Habilitar "Depuración USB"

2. Conecta el teléfono al PC

3. Instala directamente:
   ```cmd
   cd android
   gradlew installRelease
   ```

### Opción B: Transferir el APK

1. Copia `app-release.apk` a tu teléfono
2. Abre el archivo en el teléfono
3. Permite "Instalar desde fuentes desconocidas" si te lo pide
4. Instala la app

---

## 🔧 Solución de Problemas

### Error: "SDK location not found"

Crea el archivo `android/local.properties`:
```
sdk.dir=C:\\Users\\TU_USUARIO\\AppData\\Local\\Android\\Sdk
```

### Error: "Java version incompatible"

Asegúrate de usar Java 17:
```cmd
java -version
```

Si no es Java 17, actualiza `JAVA_HOME`.

### Error: "Gradle build failed"

Limpia el proyecto:
```cmd
cd android
gradlew clean
gradlew assembleRelease
```

### Error: "Out of memory"

Edita `android/gradle.properties` y agrega:
```
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=512m
```

---

## ✅ Verificar Instalación

Una vez instalada la app:

1. Abre "ISR Remote Desktop"
2. Introduce un código ISR o IP:puerto
3. Conecta a un servidor remoto
4. Verifica que puedas ver y controlar el escritorio

---

## 📝 Notas

- **Primera compilación:** Puede tardar 10-20 minutos (descarga dependencias)
- **Compilaciones posteriores:** 2-5 minutos
- **Tamaño del APK:** ~50-80 MB
- **Android mínimo:** Android 7.0 (API 24)

---

## 🆘 Ayuda

Si tienes problemas:
1. Verifica que todas las variables de entorno estén configuradas
2. Reinicia el CMD después de configurar variables
3. Asegúrate de tener espacio en disco (mínimo 10 GB libres)
4. Revisa los logs de error en la consola

---

**Última actualización:** 21 de enero de 2026
