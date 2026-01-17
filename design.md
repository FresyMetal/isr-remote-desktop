# ISR Remote Desktop - Diseño de Aplicación Android

## 📱 Orientación y Uso

**Orientación**: Vertical (9:16) y horizontal (16:9) - la app debe funcionar en ambas orientaciones
**Uso**: Una mano para navegación, dos manos para control remoto activo
**Plataforma**: Android nativo con React Native + Expo

---

## 🎨 Principios de Diseño

### Inspiración: Apple Human Interface Guidelines (HIG)

La aplicación seguirá los principios de diseño de iOS para crear una experiencia premium:

1. **Claridad**: Texto legible, iconos precisos, adornos sutiles
2. **Deferencia**: El contenido es lo primero, la UI no compite
3. **Profundidad**: Capas visuales y movimiento realista

### Paleta de Colores

```
Primary: #0a7ea4 (Azul ISR)
Background Light: #ffffff
Background Dark: #151718
Surface Light: #f5f5f5
Surface Dark: #1e2022
Foreground Light: #11181C
Foreground Dark: #ECEDEE
Muted Light: #687076
Muted Dark: #9BA1A6
Success: #22C55E / #4ADE80
Error: #EF4444 / #F87171
```

---

## 📱 Estructura de Pantallas

### 1. Pantalla Principal (Home)

**Propósito**: Conectar rápidamente a equipos remotos

**Contenido**:
- **Sección superior**: Logo ISR + título de la app
- **Campo de entrada grande**: "Introduce código ISR-XXXXXXXX o IP:puerto"
- **Botón principal**: "Conectar" (grande, destacado)
- **Lista de conexiones recientes**: Cards con:
  - Nombre/código del equipo
  - IP y puerto
  - Última conexión
  - Botón de reconexión rápida
- **Botón flotante**: "+" para agregar conexión manual

**Layout**:
```
┌─────────────────────┐
│  🖥️  ISR Remote     │
│                     │
│ ┌─────────────────┐ │
│ │ ISR-12345678    │ │ ← Input grande
│ └─────────────────┘ │
│                     │
│  [  Conectar  ]     │ ← Botón principal
│                     │
│ Recientes:          │
│ ┌─────────────────┐ │
│ │ PC Oficina      │ │
│ │ 192.168.0.97    │ │
│ │ Hace 2 horas    │ │
│ └─────────────────┘ │
│                     │
│ ┌─────────────────┐ │
│ │ Servidor Casa   │ │
│ │ ISR-68356941    │ │
│ │ Hace 1 día      │ │
│ └─────────────────┘ │
│                     │
│              [+]    │ ← FAB
└─────────────────────┘
```

---

### 2. Pantalla de Conexión (Connecting)

**Propósito**: Feedback durante el proceso de conexión

**Contenido**:
- Indicador de progreso animado
- Mensaje de estado:
  - "Resolviendo código..."
  - "Conectando a 192.168.0.97:5900..."
  - "Estableciendo conexión segura..."
- Botón "Cancelar"

**Layout**:
```
┌─────────────────────┐
│                     │
│                     │
│      ⏳             │
│                     │
│  Conectando a       │
│  ISR-68356941...    │
│                     │
│                     │
│   [ Cancelar ]      │
│                     │
└─────────────────────┘
```

---

### 3. Pantalla de Escritorio Remoto (Remote Desktop)

**Propósito**: Visualizar y controlar el escritorio remoto

**Contenido Principal**:
- **Área de visualización**: Escritorio remoto (pantalla completa)
- **Barra superior** (semi-transparente, se oculta automáticamente):
  - Nombre de la conexión
  - Indicador de latencia
  - Botón de menú (⋮)
- **Controles táctiles**:
  - Toque simple = clic izquierdo
  - Toque prolongado = clic derecho
  - Dos dedos = scroll
  - Pellizco = zoom
- **Botón flotante de teclado**: Muestra/oculta teclado virtual

**Layout (Vertical)**:
```
┌─────────────────────┐
│ PC Oficina    50ms ⋮│ ← Barra superior
├─────────────────────┤
│                     │
│                     │
│   [Escritorio]      │
│   [  Remoto  ]      │
│                     │
│                     │
│                     │
│                     │
│                     │
│                     │
│                     │
│              [⌨️]   │ ← Botón teclado
└─────────────────────┘
```

**Layout (Horizontal)**:
```
┌───────────────────────────────────────┐
│ PC Oficina                    50ms  ⋮ │
├───────────────────────────────────────┤
│                                       │
│                                       │
│         [Escritorio Remoto]           │
│                                       │
│                                       │
│                                [⌨️]   │
└───────────────────────────────────────┘
```

---

### 4. Menú de Opciones (Overlay)

**Propósito**: Acciones secundarias durante la sesión remota

**Contenido**:
- Cambiar monitor (si hay múltiples)
- Ajustar calidad de imagen
- Pantalla completa
- Captura de pantalla
- Desconectar

**Layout**:
```
┌─────────────────────┐
│ ⚙️  Opciones        │
├─────────────────────┤
│ 🖥️  Cambiar monitor │
│ 📊  Calidad: Alta   │
│ ⛶   Pantalla compl. │
│ 📸  Captura         │
│ 🔌  Desconectar     │
└─────────────────────┘
```

---

### 5. Pantalla de Error

**Propósito**: Informar errores de forma clara

**Contenido**:
- Icono de error
- Mensaje descriptivo
- Sugerencias de solución
- Botón "Reintentar"
- Botón "Volver"

**Layout**:
```
┌─────────────────────┐
│                     │
│       ❌            │
│                     │
│  No se pudo         │
│  conectar           │
│                     │
│  Verifica que:      │
│  • Servidor activo  │
│  • Código correcto  │
│  • Internet OK      │
│                     │
│  [ Reintentar ]     │
│  [   Volver   ]     │
└─────────────────────┘
```

---

## 🎯 Flujos de Usuario Principales

### Flujo 1: Conexión Rápida con Código

1. Usuario abre la app
2. Introduce código ISR-XXXXXXXX
3. Toca "Conectar"
4. App resuelve el código → obtiene IP:puerto
5. App conecta al servidor
6. Muestra escritorio remoto
7. Usuario controla con gestos táctiles

### Flujo 2: Reconexión Rápida

1. Usuario abre la app
2. Ve lista de conexiones recientes
3. Toca una conexión anterior
4. App conecta automáticamente
5. Muestra escritorio remoto

### Flujo 3: Conexión Manual por IP

1. Usuario toca botón "+"
2. Introduce IP:puerto manualmente
3. (Opcional) Introduce nombre descriptivo
4. Toca "Conectar"
5. App conecta directamente
6. Muestra escritorio remoto

### Flujo 4: Control Remoto Activo

1. Usuario ve el escritorio remoto
2. Toca para mover el cursor / hacer clic
3. Toque prolongado para clic derecho
4. Dos dedos para scroll
5. Pellizco para zoom
6. Toca botón de teclado para escribir
7. Toca "⋮" para más opciones

### Flujo 5: Manejo de Errores

1. Usuario intenta conectar
2. Falla la conexión
3. App muestra pantalla de error con:
   - Mensaje claro del problema
   - Sugerencias de solución
   - Opción de reintentar
4. Usuario corrige el problema
5. Toca "Reintentar"

---

## 🎨 Componentes de UI

### Botones

**Primario** (Conectar):
- Fondo: color primary
- Texto: blanco
- Bordes redondeados: 12px
- Padding: 16px vertical
- Ancho: 100% (con margen)
- Feedback: escala 0.97 + haptic

**Secundario** (Cancelar, Volver):
- Fondo: transparente
- Borde: 1px solid border
- Texto: foreground
- Bordes redondeados: 12px
- Padding: 12px vertical
- Feedback: opacity 0.7

**Flotante** (FAB):
- Forma: círculo
- Fondo: primary
- Icono: blanco
- Tamaño: 56x56px
- Sombra: elevación 6
- Posición: bottom-right con margen
- Feedback: escala 0.95 + haptic

### Cards (Conexiones Recientes)

- Fondo: surface
- Bordes redondeados: 16px
- Padding: 16px
- Margen: 8px vertical
- Borde: 1px solid border
- Sombra: sutil
- Feedback al tocar: opacity 0.8

**Contenido del Card**:
- Título (nombre): font-semibold, text-lg, foreground
- Subtítulo (IP): text-sm, muted
- Timestamp: text-xs, muted
- Icono: 🖥️ o 💻

### Inputs

**Campo de texto grande**:
- Fondo: surface
- Bordes redondeados: 12px
- Padding: 16px
- Borde: 2px solid border
- Borde activo: 2px solid primary
- Placeholder: muted
- Texto: foreground
- Font-size: 18px

### Indicadores

**Latencia**:
- Verde (< 50ms): success
- Amarillo (50-150ms): warning
- Rojo (> 150ms): error
- Formato: "50ms"

**Estado de conexión**:
- Conectando: spinner animado
- Conectado: ícono ✓ verde
- Error: ícono ✗ rojo

---

## 🎬 Animaciones y Transiciones

### Principios

- **Duración**: 200-300ms para la mayoría
- **Easing**: ease-out para entradas, ease-in para salidas
- **Propósito**: Feedback visual, no decoración

### Animaciones Específicas

**Botón "Conectar"**:
- Press: escala 0.97 (80ms)
- Release: escala 1.0 (120ms)
- Haptic: light impact

**Cards de conexiones**:
- Press: opacity 0.8 (100ms)
- Entrada: fade in + slide up (250ms)

**Pantalla de escritorio remoto**:
- Entrada: fade in (300ms)
- Barra superior: slide down al tocar, slide up después de 3s

**Teclado virtual**:
- Entrada: slide up (250ms)
- Salida: slide down (200ms)

---

## 📐 Especificaciones Técnicas

### Gestos Táctiles

| Gesto | Acción en PC |
|-------|--------------|
| Toque simple | Clic izquierdo |
| Toque prolongado (500ms) | Clic derecho |
| Arrastrar | Mover ratón |
| Dos dedos vertical | Scroll vertical |
| Dos dedos horizontal | Scroll horizontal |
| Pellizco | Zoom in/out |
| Doble toque | Doble clic |

### Teclado Virtual

- Usar teclado nativo de Android
- Enviar teclas en tiempo real al servidor
- Soportar teclas especiales:
  - Enter, Backspace, Tab
  - Ctrl, Alt, Shift
  - Flechas de dirección
  - Esc, F1-F12

### Calidad de Imagen

**Automática** (por defecto):
- WiFi: Alta (JPEG 90%)
- 4G/5G: Media (JPEG 70%)
- 3G: Baja (JPEG 50%)

**Manual**:
- Alta: JPEG 90%, 60 FPS
- Media: JPEG 70%, 30 FPS
- Baja: JPEG 50%, 15 FPS

### Conexión

**Protocolo**: WebSocket (ws:// o wss://)
**Puerto por defecto**: 5900
**Timeout de conexión**: 10 segundos
**Reconexión automática**: 3 intentos con backoff exponencial

---

## 🔐 Seguridad y Privacidad

### Sin Autenticación de Usuario

- **NO hay cuentas de usuario**
- **NO hay login/registro**
- **NO hay OAuth**
- Conexión directa a servidores

### Almacenamiento Local

- Historial de conexiones: AsyncStorage
- Formato: JSON con:
  - Nombre/código
  - IP y puerto
  - Timestamp de última conexión
- **NO se almacenan contraseñas**

### Permisos Necesarios

- **Internet**: Para conectar a servidores remotos
- **Vibración**: Para feedback háptico
- **Ningún otro permiso necesario**

---

## 📊 Métricas de Rendimiento

### Objetivos

- Tiempo de inicio: < 2s
- Tiempo de conexión: < 5s
- Latencia de input: < 50ms
- FPS en escritorio remoto: 30-60 FPS
- Uso de memoria: < 200 MB
- Uso de batería: Moderado

---

## 🎯 Prioridades de Desarrollo

### MVP (Mínimo Viable Product)

1. ✅ Pantalla principal con input de código
2. ✅ Resolución de códigos ISR desde servidor central
3. ✅ Conexión WebSocket al servidor remoto
4. ✅ Visualización del escritorio remoto
5. ✅ Controles táctiles básicos (toque = clic)
6. ✅ Historial de conexiones recientes

### Fase 2 (Mejoras)

7. ⏳ Gestos avanzados (scroll, zoom, clic derecho)
8. ⏳ Teclado virtual
9. ⏳ Menú de opciones
10. ⏳ Cambio de monitor
11. ⏳ Ajuste de calidad

### Fase 3 (Pulido)

12. ⏳ Animaciones suaves
13. ⏳ Feedback háptico
14. ⏳ Modo oscuro
15. ⏳ Captura de pantalla
16. ⏳ Estadísticas de conexión

---

## 🎨 Inspiración Visual

La app debe sentirse como:
- **TeamViewer**: Simplicidad en la conexión
- **Chrome Remote Desktop**: Interfaz limpia
- **AnyDesk**: Rendimiento fluido
- **iOS nativo**: Diseño premium y pulido

**NO debe sentirse como**:
- Una app web envuelta
- Una app de Android antigua (Material Design 1)
- Una app con demasiados menús y opciones

---

## 📝 Notas de Implementación

### Tecnologías

- **Framework**: React Native + Expo SDK 54
- **UI**: NativeWind (Tailwind CSS)
- **Estado**: React Context + useReducer
- **Almacenamiento**: AsyncStorage
- **Networking**: Axios + WebSocket nativo
- **Gestos**: react-native-gesture-handler
- **Animaciones**: react-native-reanimated

### Estructura de Código

```
app/
  (tabs)/
    index.tsx          ← Pantalla principal
    history.tsx        ← Historial de conexiones
  remote/
    [code].tsx         ← Pantalla de escritorio remoto
  _layout.tsx          ← Layout raíz

components/
  connection-card.tsx  ← Card de conexión reciente
  remote-viewer.tsx    ← Visor de escritorio remoto
  virtual-keyboard.tsx ← Teclado virtual
  gesture-handler.tsx  ← Manejador de gestos táctiles

lib/
  connection-manager.ts ← Gestión de conexiones
  websocket-client.ts   ← Cliente WebSocket
  code-resolver.ts      ← Resolución de códigos ISR
  storage.ts            ← Almacenamiento local

types/
  connection.ts        ← Tipos de conexión
  protocol.ts          ← Tipos de protocolo
```

---

## ✅ Criterios de Éxito

La aplicación estará completa cuando:

1. ✅ El usuario puede introducir un código ISR y conectar
2. ✅ El usuario puede ver el escritorio remoto en tiempo real
3. ✅ El usuario puede controlar el ratón con toques
4. ✅ El usuario puede escribir con el teclado virtual
5. ✅ El usuario puede reconectar rápidamente desde el historial
6. ✅ La app muestra errores claros y útiles
7. ✅ La app funciona en orientación vertical y horizontal
8. ✅ La app se siente rápida y fluida (30+ FPS)
9. ✅ La app tiene un diseño limpio y profesional
10. ✅ La app NO requiere login ni autenticación

---

**Diseño creado**: 17 de enero de 2026  
**Versión**: 1.0  
**Plataforma**: Android (React Native + Expo)
