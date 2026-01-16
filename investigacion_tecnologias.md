# Investigación de Tecnologías para Escritorio Remoto

## 1. Protocolos de Escritorio Remoto

### 1.1 Protocolo RFB (Remote Framebuffer)

El protocolo **RFB** es el fundamento de VNC (Virtual Network Computing) y representa una solución simple pero efectiva para acceso remoto a interfaces gráficas. Este protocolo opera a nivel de framebuffer, lo que lo hace aplicable a cualquier sistema de ventanas, incluyendo Windows, Linux y macOS.

#### Características Principales del RFB

El protocolo RFB se basa en una primitiva gráfica fundamental: colocar un rectángulo de datos de píxeles en una posición (x,y) específica. Aunque esto pueda parecer ineficiente, la flexibilidad en las codificaciones de datos de píxeles permite optimizar el balance entre ancho de banda, velocidad de renderizado del cliente y procesamiento del servidor.

El protocolo funciona mediante un modelo **demand-driven** (impulsado por demanda), donde las actualizaciones solo se envían del servidor al cliente en respuesta a solicitudes explícitas. Esta característica adaptativa permite que el protocolo ajuste automáticamente su rendimiento según la velocidad del cliente y la red.

#### Tipos de Mensajes RFB

El protocolo define varios tipos de mensajes críticos:

**Mensajes Cliente → Servidor:**
- **SetPixelFormat**: Establece el formato de píxeles deseado
- **SetEncodings**: Especifica las codificaciones soportadas
- **FramebufferUpdateRequest**: Solicita actualización del framebuffer
- **KeyEvent**: Eventos de teclado
- **PointerEvent**: Eventos de ratón
- **ClientCutText**: Sincronización del portapapeles

**Mensajes Servidor → Cliente:**
- **FramebufferUpdate**: Envía rectángulos de píxeles actualizados
- **ServerCutText**: Contenido del portapapeles del servidor
- **Bell**: Notificación de sonido

#### Codificaciones Disponibles

El protocolo RFB soporta múltiples esquemas de codificación para optimizar la transmisión:

- **Raw**: Datos de píxeles sin comprimir
- **CopyRect**: Copia un rectángulo de una posición a otra (muy eficiente)
- **RRE/CoRRE**: Codificación Run-Length para áreas uniformes
- **Hextile**: División en tiles de 16x16 píxeles
- **Tight**: Compresión JPEG + zlib (excelente balance)
- **ZRLE**: Zlib + Run-Length Encoding
- **zlib**: Compresión zlib estándar

Para nuestra aplicación, las codificaciones **Tight** y **ZRLE** son las más prometedoras, ya que ofrecen ratios de compresión de 3:1 hasta 10:1 con buena calidad visual.

#### Seguridad en RFB

El protocolo incluye varios tipos de seguridad:
- **None**: Sin autenticación (útil para redes locales confiables)
- **VNC Authentication**: Autenticación con contraseña usando DES
- **Tight Security**: Extensión con múltiples opciones de seguridad

### 1.2 Comparación RFB vs RDP

| Aspecto | RFB/VNC | RDP (Microsoft) |
|---------|---------|-----------------|
| Complejidad | Simple, fácil de implementar | Complejo, protocolo propietario |
| Rendimiento | Bueno (con codificaciones modernas) | Excelente (optimizado para Windows) |
| Multiplataforma | Totalmente multiplataforma | Principalmente Windows |
| Documentación | Abierta y completa | Limitada (ingeniería inversa) |
| Extensibilidad | Muy extensible | Limitada |

Para nuestro proyecto, **RFB es la mejor opción** debido a su simplicidad, documentación completa y facilidad de implementación en Python.

## 2. Bibliotecas Python Recomendadas

### 2.1 Captura de Pantalla

#### DXcam (Recomendado para Windows)

**DXcam** es una biblioteca de captura de pantalla de alto rendimiento para Windows que utiliza la **Desktop Duplication API**. Sus características principales incluyen:

- **Velocidad excepcional**: Capaz de capturar a más de 240 FPS
- **Captura de aplicaciones exclusivas DirectX**: Puede capturar juegos en pantalla completa sin interrumpir
- **Manejo automático de resoluciones escaladas**: Gestiona automáticamente diferentes escalas de DPI
- **Integración perfecta con NumPy**: Devuelve arrays NumPy directamente
- **Soporte multi-monitor**: Puede capturar de múltiples monitores simultáneamente

**Instalación:**
```bash
pip install dxcam
```

**Ejemplo de uso:**
```python
import dxcam

# Crear instancia de cámara
camera = dxcam.create()

# Captura única
frame = camera.grab()  # Devuelve numpy.ndarray (H, W, 3)

# Captura continua a 60 FPS
camera.start(target_fps=60)
while capturing:
    frame = camera.get_latest_frame()
    # Procesar frame
camera.stop()
```

**Ventajas:**
- Rendimiento superior a mss y PIL
- API simple y limpia
- Soporte para captura de regiones específicas
- Buffer de video integrado

**Desventajas:**
- Solo funciona en Windows
- Requiere Windows 8 o superior

#### mss (Alternativa multiplataforma)

**python-mss** es una biblioteca de captura de pantalla multiplataforma con buen rendimiento.

**Rendimiento:**
- Captura completa 1920x1080: ~16-30ms
- Más lento que DXcam pero más rápido que PIL

**Instalación:**
```bash
pip install mss
```

### 2.2 Interfaz Gráfica

#### PyQt6 (Recomendado)

**PyQt6** es un binding de Python para Qt 6, el framework GUI más completo y profesional disponible.

**Ventajas:**
- Interfaz nativa en Windows
- Excelente rendimiento
- Widgets avanzados (tabs, docks, toolbars)
- Soporte para múltiples ventanas
- Sistema de señales/slots robusto
- Amplia documentación y comunidad

**Instalación:**
```bash
pip install PyQt6
```

**Características relevantes para nuestro proyecto:**
- `QTabWidget`: Para gestionar múltiples sesiones
- `QLabel` con `QPixmap`: Para mostrar el escritorio remoto
- `QFileDialog`: Para transferencia de archivos
- `QSystemTrayIcon`: Para minimizar a bandeja del sistema

### 2.3 Control de Entrada

#### pynput (Recomendado)

**pynput** permite controlar y monitorear dispositivos de entrada (teclado y ratón).

**Instalación:**
```bash
pip install pynput
```

**Características:**
- Control de ratón (mover, click, scroll)
- Control de teclado (teclas, combinaciones)
- Monitoreo de eventos de entrada
- Multiplataforma

**Ejemplo:**
```python
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController

mouse = MouseController()
keyboard = KeyboardController()

# Mover ratón
mouse.position = (100, 200)

# Click
mouse.click(Button.left, 1)

# Escribir texto
keyboard.type('Hola mundo')
```

### 2.4 Gestión del Portapapeles

#### pyperclip

**pyperclip** es una biblioteca simple para operaciones de portapapeles multiplataforma.

**Instalación:**
```bash
pip install pyperclip
```

**Uso:**
```python
import pyperclip

# Copiar al portapapeles
pyperclip.copy('Texto a copiar')

# Leer del portapapeles
texto = pyperclip.paste()
```

### 2.5 Compresión

#### Zstandard (Recomendado)

**Zstandard (zstd)** es un algoritmo de compresión moderno desarrollado por Facebook que ofrece excelente velocidad y ratios de compresión.

**Ventajas:**
- Muy rápido (compresión y descompresión)
- Ratios de compresión ajustables (nivel 1-22)
- Mejor que zlib en la mayoría de casos
- Streaming support

**Instalación:**
```bash
pip install zstandard
```

**Ejemplo:**
```python
import zstandard as zstd

compressor = zstd.ZstdCompressor(level=3)
compressed = compressor.compress(data)

decompressor = zstd.ZstdDecompressor()
original = decompressor.decompress(compressed)
```

### 2.6 Criptografía

#### cryptography (Recomendado)

**cryptography** es la biblioteca de criptografía más robusta y moderna para Python.

**Instalación:**
```bash
pip install cryptography
```

**Características:**
- Cifrado simétrico (AES-GCM, ChaCha20)
- Cifrado asimétrico (RSA, ECDH)
- Funciones hash (SHA-256, SHA-512)
- Generación de claves
- Certificados X.509

**Ejemplo de cifrado AES-GCM:**
```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# Generar clave
key = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(key)

# Cifrar
nonce = os.urandom(12)
ciphertext = aesgcm.encrypt(nonce, plaintext, None)

# Descifrar
plaintext = aesgcm.decrypt(nonce, ciphertext, None)
```

## 3. Arquitectura Técnica Recomendada

### 3.1 Stack Tecnológico Final

Basándonos en la investigación, el stack tecnológico recomendado es:

| Componente | Tecnología | Justificación |
|------------|-----------|---------------|
| Lenguaje | Python 3.11+ | Ecosistema rico, desarrollo rápido |
| Protocolo | RFB (VNC) personalizado | Simple, documentado, extensible |
| Captura pantalla | DXcam | Máximo rendimiento en Windows |
| GUI | PyQt6 | Profesional, completo, nativo |
| Control entrada | pynput | Simple, efectivo, multiplataforma |
| Portapapeles | pyperclip | Ligero, confiable |
| Compresión | zstandard | Rápido, eficiente |
| Cifrado | cryptography (AES-GCM) | Seguro, moderno, rápido |
| Networking | asyncio + socket | Asíncrono, escalable |

### 3.2 Protocolo Personalizado

Aunque usaremos RFB como inspiración, crearemos un protocolo personalizado optimizado para nuestras necesidades:

#### Estructura de Mensajes

```
[HEADER: 12 bytes]
├─ Magic Number (2 bytes): 0x5244  ("RD" = Remote Desktop)
├─ Message Type (1 byte): 0x01-0xFF
├─ Flags (1 byte): compresión, cifrado, prioridad
├─ Payload Length (4 bytes): tamaño del payload
└─ Sequence Number (4 bytes): para ordenamiento

[PAYLOAD: variable]
└─ Datos específicos del tipo de mensaje
```

#### Tipos de Mensajes

| Código | Tipo | Dirección | Descripción |
|--------|------|-----------|-------------|
| 0x01 | HANDSHAKE | Bidireccional | Negociación inicial |
| 0x02 | AUTH_REQUEST | Cliente → Servidor | Solicitud de autenticación |
| 0x03 | AUTH_RESPONSE | Servidor → Cliente | Respuesta de autenticación |
| 0x10 | VIDEO_FRAME | Servidor → Cliente | Frame de video comprimido |
| 0x11 | VIDEO_REQUEST | Cliente → Servidor | Solicitud de actualización |
| 0x20 | INPUT_MOUSE | Cliente → Servidor | Evento de ratón |
| 0x21 | INPUT_KEYBOARD | Cliente → Servidor | Evento de teclado |
| 0x30 | FILE_METADATA | Bidireccional | Metadatos de archivo |
| 0x31 | FILE_CHUNK | Bidireccional | Chunk de archivo |
| 0x32 | FILE_COMPLETE | Bidireccional | Transferencia completada |
| 0x40 | CLIPBOARD_TEXT | Bidireccional | Texto del portapapeles |
| 0x41 | CLIPBOARD_IMAGE | Bidireccional | Imagen del portapapeles |
| 0xF0 | PING | Bidireccional | Keep-alive |
| 0xF1 | DISCONNECT | Bidireccional | Desconexión ordenada |

### 3.3 Optimizaciones de Rendimiento

#### Detección de Cambios (Dirty Regions)

En lugar de capturar y enviar toda la pantalla en cada frame, implementaremos detección de regiones modificadas:

```python
def detect_changes(current_frame, previous_frame):
    """Detecta regiones que han cambiado entre frames"""
    diff = cv2.absdiff(current_frame, previous_frame)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
    
    # Encontrar contornos de áreas cambiadas
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, 
                                     cv2.CHAIN_APPROX_SIMPLE)
    
    dirty_regions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        dirty_regions.append((x, y, w, h))
    
    return dirty_regions
```

#### Compresión Adaptativa

Ajustaremos dinámicamente el nivel de compresión según la latencia de red:

```python
def adjust_compression_level(latency_ms):
    """Ajusta nivel de compresión según latencia"""
    if latency_ms < 20:  # LAN
        return 1  # Compresión mínima, priorizar velocidad
    elif latency_ms < 100:  # WAN
        return 5  # Balance
    else:  # Internet lento
        return 9  # Máxima compresión
```

#### Threading Model

```
[Servidor]
├─ Main Thread: GUI y coordinación
├─ Capture Thread: Captura de pantalla continua
├─ Network Thread: Envío/recepción de datos
├─ Clipboard Monitor Thread: Monitoreo del portapapeles
└─ File Transfer Thread Pool: Transferencias de archivos

[Cliente]
├─ Main Thread: GUI
├─ Network Thread: Envío/recepción de datos
├─ Render Thread: Renderizado del escritorio remoto
├─ Clipboard Monitor Thread: Monitoreo del portapapeles
└─ File Transfer Thread Pool: Transferencias de archivos
```

## 4. Consideraciones de Seguridad

### 4.1 Cifrado de Extremo a Extremo

Implementaremos un esquema híbrido de cifrado:

1. **Handshake inicial**: Intercambio de claves usando RSA-2048
2. **Sesión**: Cifrado simétrico con AES-256-GCM
3. **Integridad**: HMAC-SHA256 para verificación de mensajes

### 4.2 Autenticación

Según las preferencias del proyecto, **no implementaremos autenticación de usuario**. En su lugar, usaremos:

- **Clave pre-compartida (PSK)**: Una contraseña simple para conectar
- **Whitelist de IPs**: Opcional, para restringir conexiones

### 4.3 Protección contra Ataques

- **Rate limiting**: Máximo 100 mensajes/segundo por cliente
- **Timeout de conexión**: 30 segundos para handshake
- **Validación de mensajes**: Verificar tamaño y formato

## 5. Estimación de Rendimiento

### 5.1 Ancho de Banda Estimado

Para una resolución de 1920x1080 a 30 FPS:

| Escenario | Datos sin comprimir | Con Tight (5:1) | Con Zstd (7:1) |
|-----------|---------------------|-----------------|----------------|
| Frame completo | 6.2 MB/frame | 1.24 MB/frame | 0.89 MB/frame |
| Bitrate (30 FPS) | 186 MB/s | 37 MB/s | 27 MB/s |
| Solo cambios (20%) | 37 MB/s | 7.4 MB/s | 5.4 MB/s |

Con detección de cambios y compresión Zstd, podemos lograr **5-10 MB/s** en uso típico de escritorio.

### 5.2 Latencia Esperada

| Componente | Latencia |
|------------|----------|
| Captura (DXcam) | 4-8 ms |
| Compresión (Zstd nivel 3) | 5-10 ms |
| Red (LAN) | 1-5 ms |
| Descompresión | 2-5 ms |
| Renderizado | 5-10 ms |
| **Total (LAN)** | **17-38 ms** |

Esto nos da un **rendimiento de 26-59 FPS**, suficiente para una experiencia fluida.

## 6. Próximos Pasos

Con esta investigación completada, podemos proceder a:

1. Implementar el servidor con captura de pantalla usando DXcam
2. Implementar el protocolo de red personalizado
3. Crear el cliente con interfaz PyQt6
4. Agregar transferencia de archivos
5. Implementar sincronización de portapapeles
6. Añadir cifrado y seguridad
7. Optimizar rendimiento
8. Empaquetar y distribuir

La arquitectura propuesta es sólida, escalable y optimizada para Windows, cumpliendo todos los requisitos del proyecto.
