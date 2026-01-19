# ISR Remote Desktop Android - Lista de Tareas

## 🎯 MVP (Mínimo Viable Product)

### Pantalla Principal
- [x] Diseñar layout de pantalla principal con input grande
- [x] Implementar campo de entrada para código ISR o IP:puerto
- [x] Agregar botón "Conectar" con feedback visual
- [x] Crear componente de card para conexiones recientes
- [x] Implementar lista de conexiones recientes desde AsyncStorage
- [ ] Agregar botón flotante "+" para conexión manual

### Resolución de Códigos ISR
- [x] Crear módulo `code-resolver.ts` para resolver códigos
- [x] Implementar conexión al servidor central (77.225.201.4:8080)
- [x] Manejar respuesta de resolución de código
- [x] Implementar detección de IP directa vs código ISR
- [x] Agregar manejo de errores de resolución

### Conexión TCP
- [x] Crear módulo `tcp-client.ts`
- [x] Implementar conexión TCP al servidor remoto
- [x] Implementar handshake con el servidor
- [x] Manejar estados de conexión (conectando, conectado, error)
- [x] Implementar reconexión automática
- [x] Agregar timeout de conexión (10 segundos)

### Visualización del Escritorio Remoto
- [x] Crear componente `remote-desktop-view.tsx`
- [x] Implementar recepción de frames de video (JPEG)
- [x] Decodificar y mostrar frames en tiempo real
- [x] Implementar escalado de imagen para ajustar a pantalla
- [ ] Optimizar rendimiento para 30+ FPS

### Controles Táctiles Básicos
- [x] Implementar detección de toque simple (clic izquierdo)
- [x] Calcular coordenadas relativas del toque
- [x] Enviar eventos de ratón al servidor
- [ ] Implementar feedback visual al tocar

### Historial de Conexiones
- [x] Crear módulo `storage.ts` con AsyncStorage
- [x] Implementar guardado de conexiones recientes
- [x] Implementar carga de conexiones recientes
- [x] Limitar historial a 10 conexiones
- [x] Agregar timestamp de última conexión

### Pantallas de Estado
- [x] Crear pantalla de "Conectando" con spinner
- [x] Crear pantalla de error con mensajes claros
- [x] Implementar navegación entre pantallas
- [x] Agregar botones "Cancelar" y "Reintentar"

---

## 🚀 Fase 2 (Mejoras)

### Gestos Avanzados
- [x] Implementar toque prolongado (clic derecho) - SOLICITADO
- [x] Implementar arrastrar (mover ratón)
- [x] Implementar scroll con dos dedos - SOLICITADO
- [x] Implementar zoom con pellizco - SOLICITADO
- [ ] Implementar doble toque (doble clic)

### Teclado Virtual
- [x] Crear componente `virtual-keyboard.tsx` - SOLICITADO
- [x] Mostrar/ocultar teclado nativo de Android - SOLICITADO
- [x] Enviar teclas al servidor en tiempo real - SOLICITADO
- [x] Soportar flechas y teclas de función
- [ ] Soportar teclas especiales (Ctrl, Alt, Shift)

### Menú de Opciones
- [ ] Crear overlay de menú de opciones
- [ ] Agregar opción "Cambiar monitor"
- [ ] Agregar opción "Ajustar calidad"
- [ ] Agregar opción "Pantalla completa"
- [ ] Agregar opción "Desconectar"

### Calidad de Imagen
- [ ] Implementar detección automática de calidad (WiFi/4G/3G)
- [x] Agregar selector manual de calidad (Baja/Media/Alta) - SOLICITADO
- [ ] Implementar ajuste de FPS según calidad
- [ ] Optimizar uso de ancho de banda

---

## 🎨 Fase 3 (Pulido)

### Animaciones
- [ ] Agregar animación de press en botones
- [ ] Agregar fade in/out en transiciones de pantalla
- [ ] Agregar slide up/down en barra superior
- [ ] Agregar animación de entrada de cards

### Feedback Háptico
- [ ] Implementar haptic en botón "Conectar"
- [ ] Implementar haptic en toques en escritorio remoto
- [ ] Implementar haptic en gestos (clic derecho, scroll)

### Modo Oscuro
- [ ] Verificar que todos los colores usen tokens de tema
- [ ] Probar en modo oscuro
- [ ] Ajustar contrastes si es necesario

### Características Adicionales
- [ ] Implementar captura de pantalla
- [ ] Agregar indicador de latencia en tiempo real
- [ ] Agregar estadísticas de conexión
- [ ] Implementar modo de solo visualización (sin control)

---

## 🔧 Configuración y Branding

### App Branding
- [x] Generar logo personalizado para ISR Remote Desktop
- [x] Actualizar `app.config.ts` con nombre de app
- [x] Copiar logo a `assets/images/icon.png`
- [x] Copiar logo a `assets/images/splash-icon.png`
- [x] Copiar logo a `assets/images/favicon.png`
- [x] Copiar logo a `assets/images/android-icon-foreground.png`

### Configuración de Tema
- [x] Actualizar colores en `theme.config.js` con paleta ISR
- [x] Verificar que todos los componentes usen colores del tema

---

## 📝 Documentación

- [ ] Crear README.md con instrucciones de uso
- [ ] Documentar cómo compilar la app
- [ ] Documentar cómo instalar en Android
- [ ] Crear guía de usuario básica
- [ ] Documentar protocolo de comunicación con servidor

---

## ✅ Testing y Entrega

- [ ] Probar conexión con código ISR
- [ ] Probar conexión con IP directa
- [ ] Probar reconexión desde historial
- [ ] Probar en orientación vertical
- [ ] Probar en orientación horizontal
- [ ] Probar manejo de errores
- [ ] Probar rendimiento (FPS, latencia)
- [ ] Crear checkpoint final
- [ ] Generar APK para instalación

---

**Creado**: 17 de enero de 2026  
**Última actualización**: 17 de enero de 2026

## Selector de Monitores - SOLICITADO

- [x] Actualizar protocolo TCP con mensajes de monitores
- [x] Crear componente MonitorSelector en la app móvil
- [x] Actualizar servidor Python para detectar monitores
- [x] Implementar cambio de monitor en tiempo real
- [x] Agregar botón de selector de monitores en la barra de controles

## Portapapeles Bidireccional - SOLICITADO

- [x] Implementar sincronización automática móvil → PC
- [x] Implementar recepción PC → móvil
- [x] Agregar notificación visual al sincronizar
- [x] Agregar botones manuales de copiar/pegar
- [x] Probar sincronización bidireccional

## Build APK Nativo - SOLICITADO

- [x] Configurar EAS Build (eas.json)
- [x] Generar proyecto Android nativo con prebuild
- [x] Configurar Gradle para compilación standalone
- [x] Crear script de compilación local (Windows y Linux)
- [x] Generar APK independiente
- [x] Documentar instalación del APK

## Modo Kiosko - SOLICITADO

- [x] Implementar estado de modo kiosko en viewer
- [x] Ocultar barra de estado y navegación en modo kiosko
- [x] Ocultar todos los controles permanentemente
- [x] Agregar botón para activar/desactivar modo kiosko
- [x] Implementar gesto de deslizar desde borde para salir
- [x] Optimizar visualización para uso como monitor secundario
