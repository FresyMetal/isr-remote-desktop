# Historial de Cambios

## Versión 3.0.5 - 16 de enero de 2026

### 🐛 Corrección de Error Crítico

**Problema**: 
La aplicación fallaba al iniciar con error en la línea 33 de `isr_remote.py`. El error era causado por una dependencia circular en `connection_code.py` donde el método `_detect_registry_server()` llamaba a `self.get_local_ip()` durante la inicialización de la clase, pero ese método aún no estaba disponible.

**Solución**:
Reescrito el método `_detect_registry_server()` para obtener la IP local directamente usando sockets, sin depender de `self.get_local_ip()`.

**Código corregido**:
```python
def _detect_registry_server(self) -> str:
    # Obtener IP local sin usar self.get_local_ip()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    
    if local_ip.startswith("192.168.0."):
        return "http://192.168.0.57:8080"
    else:
        return "http://77.225.201.4:8080"
```

---

### 🐧 Soporte para Servidor Linux

**Agregados**:
- ✅ `CONFIGURAR_SERVIDOR_LINUX.md` - Guía completa de configuración
- ✅ `test_server_linux.py` - Script de verificación del servidor

**Características del script de verificación**:
- Verifica versión de Python y dependencias
- Verifica que el servidor esté corriendo localmente
- Verifica que el puerto 8080 esté escuchando
- Verifica configuración del firewall
- Obtiene IP pública del servidor
- Verifica acceso desde Internet
- Prueba registro y resolución de códigos
- Verifica servicio systemd

**Uso**:
```bash
cd /opt/isr-remote-desktop
python3 test_server_linux.py
```

---

### 🔧 Archivos Modificados

- ✅ `connection_code.py` - Corregido método `_detect_registry_server()`
- ✅ `isr_remote.py` - Actualizada versión a 3.0.5
- ✅ `CHANGELOG.md` - Documentados cambios de v3.0.5

### 🆕 Archivos Nuevos

- ✅ `CONFIGURAR_SERVIDOR_LINUX.md` - Guía de configuración del servidor
- ✅ `test_server_linux.py` - Script de verificación del servidor

---

## Versión 3.0.4 - 16 de enero de 2026

### 🌐 Detección Automática de Servidor Central

**Problema**: 
Desde dentro de la red local no se podía acceder al servidor central usando la IP pública (77.225.201.4:8080) debido a NAT loopback. El servidor está en la red local (192.168.0.57) pero tiene IP pública.

**Solución**:
Implementada detección automática que:
- Detecta si el cliente está en la red local (192.168.0.x)
- Usa **IP local** (192.168.0.57:8080) cuando está en la misma red
- Usa **IP pública** (77.225.201.4:8080) cuando está fuera de la red

**Código agregado**:
```python
def _detect_registry_server(self) -> str:
    local_server = "http://192.168.0.57:8080"
    public_server = "http://77.225.201.4:8080"
    
    local_ip = self.get_local_ip()
    
    if local_ip.startswith("192.168.0."):
        return local_server  # Misma red
    else:
        return public_server  # Fuera de la red
```

**Resultado**: 
✅ El sistema ahora funciona tanto desde la red local como desde Internet sin configuración manual

---

### 🔧 Archivos Modificados

- ✅ `connection_code.py` - Agregada detección automática de servidor
- ✅ `test_connection.py` - Actualizado para usar detección automática
- ✅ `isr_remote.py` - Actualizada versión a 3.0.4

---

## Versión 3.0.3 - 16 de enero de 2026

### 🐛 Correcciones de Bugs Críticos

#### Bug de Cierre del Servidor

**Problema**: 
La aplicación se colgaba al hacer clic en "Detener Servidor" y había que forzar el cierre.

**Causa**: 
- El servidor tenía un `accept()` bloqueante en el socket
- Cuando se llamaba a `stop()`, solo se cambiaba `running = False` pero el socket seguía esperando conexiones
- El thread nunca terminaba, causando que la aplicación se colgara

**Solución**:
- Agregado `socket.shutdown(socket.SHUT_RDWR)` antes de `socket.close()` para desbloquear `accept()`
- Implementado timeout de 3 segundos en `thread.wait(3000)`
- Agregada terminación forzosa con `thread.terminate()` si el thread no responde

**Resultado**: 
✅ El servidor ahora se detiene correctamente sin colgar la aplicación

---

### 📚 Documentación Nueva

#### Guía de Port Forwarding

**Nuevo archivo**: `CONFIGURAR_PORT_FORWARDING.md`

**Contenido**:
- Instrucciones paso a paso para configurar port forwarding en el router
- Configuración específica por marca (TP-Link, Netgear, D-Link, Asus, Linksys)
- Guía de configuración de IP estática
- Verificación de puerto abierto
- Recomendaciones de seguridad
- Solución de problemas comunes

**Propósito**: 
Permitir conexiones desde Internet (no solo red local)

---

#### Script de Verificación de Conectividad

**Nuevo archivo**: `test_connection.py`

**Funcionalidad**:
- ✓ Prueba IP local
- ✓ Prueba IP pública
- ✓ Verifica conexión con servidor central (77.225.201.4:8080)
- ✓ Prueba registro de códigos
- ✓ Prueba resolución de códigos
- ✓ Verifica servidor local activo
- ✓ Verifica configuración de firewall
- ✓ Genera reporte completo de diagnóstico

**Uso**:
```bash
python test_connection.py
```

**Resultado**: 
Reporte completo del estado de conectividad

---

### 🌐 Mejoras de Conectividad

#### Instrucciones en la Interfaz

**Agregado**: 
Mensaje informativo en la pestaña "Permitir Control" sobre port forwarding:

> "Para permitir conexiones desde otras redes (Internet), necesitas configurar Port Forwarding en tu router. Lee el archivo CONFIGURAR_PORT_FORWARDING.md para instrucciones detalladas."

**Propósito**: 
Informar al usuario que el sistema ya soporta conexión desde Internet, pero requiere configuración del router

---

### 🔧 Cambios Técnicos

#### server.py
```python
def stop(self):
    self.running = False
    
    # Cerrar socket del servidor (shutdown primero para desbloquear accept())
    if self.server_socket:
        try:
            self.server_socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.server_socket.close()
        except:
            pass
```

#### isr_remote.py
```python
def stop_server(self):
    if self.server_thread:
        self.server_thread.stop()
        # Esperar máximo 3 segundos para que el thread termine
        self.server_thread.wait(3000)
        if self.server_thread.isRunning():
            # Si aún está corriendo, terminarlo forzosamente
            self.server_thread.terminate()
            self.server_thread.wait(1000)
        self.server_thread = None
```

---

### 📝 Archivos Actualizados

- ✅ `server.py` - Corregido método `stop()`
- ✅ `isr_remote.py` - Corregido método `stop_server()` con timeout
- ✅ `LEEME.txt` - Actualizado con información de v3.0.3
- ✅ `CHANGELOG.md` - Este archivo

### 📝 Archivos Nuevos

- ✅ `CONFIGURAR_PORT_FORWARDING.md` - Guía de port forwarding
- ✅ `test_connection.py` - Script de verificación

---

## Versión 3.0.2 - 16 de enero de 2026

### 🐛 Correcciones

- **Corregido**: Error "ModuleNotFoundError: No module named 'mss'" al ejecutar .exe compilado
  - Agregados hidden-imports en PyInstaller para `mss`, `pynput`, `PIL`, `zstandard`
  - Actualizado `compilar_unificado.bat` con parámetros correctos

### 📚 Documentación

- **Nuevo**: `SOLUCION_CONEXION.md` - Guía de solución de problemas de conexión

---

## Versión 3.0.1 - 16 de enero de 2026

### 🔧 Mejoras

- Optimizaciones menores en la interfaz
- Mejoras en mensajes de error

---

## Versión 3.0.0 - 16 de enero de 2026

### ✨ Características Principales

- **Aplicación Unificada**: Fusión de servidor y cliente en una sola aplicación
- **Configuración desde GUI**: Configuración de contraseña desde la interfaz
- **Servidor Central de Registro**: Implementado en 77.225.201.4:8080

---

## Versión 1.2 - 15 de enero de 2026

### 🐛 Correcciones Críticas

#### 1. Mapeo Incorrecto de Coordenadas del Ratón

**Problema**: 
El ratón apuntaba más arriba y a la izquierda de donde realmente estaba el cursor.

**Causa**: 
El cliente estaba escalando la imagen del escritorio remoto, pero las coordenadas del ratón no se estaban ajustando correctamente a la escala.

**Solución**:
- Deshabilitado el escalado automático de la imagen (`setWidgetResizable(False)`)
- La imagen ahora se muestra en su tamaño real 1:1
- Las coordenadas del ratón se envían directamente sin transformación
- Se usa QScrollArea para permitir scroll si la pantalla remota es más grande

**Resultado**: 
✅ El cursor ahora apunta exactamente donde debe

---

#### 2. Eventos de Clic No Funcionaban

**Problema**: 
No se podía hacer clic en ningún sitio del escritorio remoto.

**Causa**: 
El servidor recibía los eventos de botones del ratón pero no los procesaba. Solo movía el cursor pero no ejecutaba los clics.

**Solución**:
- Implementada detección de cambios de estado de botones
- Se detecta cuando un botón se presiona o se suelta
- Se usa `mouse.press()` y `mouse.release()` de pynput correctamente
- Soporte para botón izquierdo, derecho y medio

**Código agregado**:
```python
# Detectar cambios en los botones
changed = buttons ^ self._last_mouse_buttons

# Botón izquierdo
if changed & 0x01:
    if buttons & 0x01:
        self.mouse.press(Button.left)
    else:
        self.mouse.release(Button.left)
```

**Resultado**: 
✅ Los clics ahora funcionan correctamente

---

#### 3. Teclado No Funcionaba

**Problema**: 
No se podía escribir en el escritorio remoto.

**Causa**: 
La función `_handle_keyboard_event()` estaba vacía (solo tenía `pass`).

**Solución**:
- Implementado mapeo completo de teclas de Qt a pynput
- Mapeo de teclas especiales (Enter, Backspace, Flechas, F1-F12, etc.)
- Mapeo de caracteres ASCII normales
- Soporte para teclas modificadoras (Shift, Ctrl, Alt)

**Teclas soportadas**:
- ✅ Todas las letras y números
- ✅ Teclas especiales (Enter, Tab, Esc, Delete, etc.)
- ✅ Teclas de navegación (Flechas, Home, End, Page Up/Down)
- ✅ Teclas de función (F1-F12)
- ✅ Modificadores (Shift, Ctrl, Alt, Caps Lock)

**Resultado**: 
✅ El teclado ahora funciona completamente

---

#### 4. No Se Veía la Pantalla Entera

**Problema**: 
La pantalla remota no se mostraba completa, estaba cortada o escalada incorrectamente.

**Causa**: 
- `setWidgetResizable(True)` estaba escalando la imagen
- El label no se ajustaba al tamaño real de la imagen

**Solución**:
- Cambiado `setWidgetResizable(False)` para mantener tamaño real
- Deshabilitado `setScaledContents()` para evitar escalado automático
- Usar `setFixedSize(pixmap.size())` para ajustar el label al tamaño exacto
- QScrollArea permite hacer scroll si la pantalla es más grande que la ventana

**Resultado**: 
✅ La pantalla se ve completa en su tamaño real con scroll si es necesario

---

### ✨ Nuevas Características

#### Soporte para Múltiples Monitores

**Funcionalidad**:
- El servidor ahora puede capturar cualquier monitor conectado
- Se muestra la lista de monitores disponibles al iniciar
- Se puede seleccionar el monitor mediante parámetro de línea de comandos

**Uso**:
```bash
# Monitor principal (por defecto)
python server.py

# Segundo monitor
python server.py --monitor 2

# Tercer monitor
python server.py --monitor 3
```

**Salida del servidor**:
```
[Servidor] Monitores disponibles: 2
  Monitor 1: 1920x1080 en (0, 0) (ACTIVO)
  Monitor 2: 1920x1080 en (1920, 0)
```

**Resultado**: 
✅ Soporte completo para múltiples monitores

---

### 📝 Cambios Técnicos

#### Cliente (`client.py`)
1. **RemoteDesktopWidget.init_ui()**:
   - `scroll.setWidgetResizable(False)` - Sin escalado automático
   - `frame_label.setScaledContents(False)` - Sin escalado de contenido

2. **RemoteDesktopWidget.update_frame()**:
   - `setFixedSize(pixmap.size())` - Tamaño fijo igual al pixmap

3. **Eventos del ratón**:
   - Simplificados: coordenadas directas sin transformación
   - Eliminado el cálculo de escala

#### Servidor (`server.py`)
1. **Constructor**:
   - Nuevo parámetro `monitor_index` para seleccionar monitor
   - Variable `available_monitors` para almacenar todos los monitores

2. **_init_monitor()**:
   - Detecta todos los monitores disponibles
   - Valida el índice del monitor
   - Muestra información de todos los monitores

3. **_handle_mouse_event()**:
   - Implementada detección de cambios de estado de botones
   - Llamadas a `mouse.press()` y `mouse.release()`

4. **_handle_keyboard_event()**:
   - Mapeo completo de teclas Qt a pynput
   - Soporte para teclas especiales y modificadores

5. **main()**:
   - Nuevo argumento `--monitor` en línea de comandos

---

## Versión 1.1 - 15 de enero de 2026

### 🐛 Correcciones de Errores

#### Error de Threading en Captura de Pantalla (CRÍTICO)

**Problema**: 
```
[Servidor] Error en captura: '_thread._local' object has no attribute 'srcdc'
```

**Causa**: 
La biblioteca `mss` en Windows utiliza objetos thread-local que no pueden compartirse entre threads.

**Solución**:
- Crear una instancia de `mss.mss()` dentro de cada thread de captura
- Usar el patrón `with mss.mss() as sct:` para gestión automática de recursos

**Resultado**: 
✅ Resuelve el crash inmediato al conectar

---

## Versión 1.0 - 15 de enero de 2026

### ✨ Características Iniciales

- ✅ Escritorio remoto en tiempo real
- ✅ Control de ratón y teclado
- ✅ Transferencia de archivos bidireccional
- ✅ Portapapeles compartido bidireccional
- ✅ Múltiples sesiones simultáneas
- ✅ Cifrado AES-256-GCM
- ✅ Compresión Zstandard + JPEG

---

## Problemas Conocidos

### Resueltos en v1.2
- ✅ Mapeo incorrecto de coordenadas del ratón
- ✅ Eventos de clic no funcionaban
- ✅ Teclado no funcionaba
- ✅ Pantalla no se veía completa
- ✅ Sin soporte para múltiples monitores

### Resueltos en v1.1
- ✅ Error de threading en captura de pantalla

### Pendientes
- ⚠️ No hay detección de regiones modificadas (envía frame completo)
- ⚠️ Python 3.13 puede tener problemas de compatibilidad con PyInstaller
- ⚠️ El teclado puede tener problemas con caracteres especiales no ASCII

---

## Notas de Actualización

### De v1.1 a v1.2

**¿Necesito actualizar?**
- **SÍ** si el ratón no apunta donde debe
- **SÍ** si no puedes hacer clic
- **SÍ** si no puedes escribir
- **SÍ** si la pantalla no se ve completa
- **SÍ** si tienes múltiples monitores

**Cómo actualizar**:
1. Descarga la nueva versión
2. Reemplaza `server.py` y `client.py`
3. Reinicia servidor y cliente

**Compatibilidad**:
- ❌ Cliente v1.0/1.1 NO es totalmente compatible con Servidor v1.2
- ❌ Cliente v1.2 NO es totalmente compatible con Servidor v1.0/1.1
- ✅ Se recomienda actualizar ambos (servidor y cliente)

### De v1.0 a v1.1

**Compatibilidad**:
- ✅ Cliente v1.0 es compatible con Servidor v1.1
- ✅ Cliente v1.1 es compatible con Servidor v1.0

---

## Roadmap Futuro

### Versión 1.3 (Próxima)
- [ ] Detección de regiones modificadas (dirty regions)
- [ ] Ajuste dinámico de calidad según latencia
- [ ] Mejoras de rendimiento en compresión
- [ ] Soporte para caracteres Unicode en teclado

### Versión 2.0
- [ ] Aplicación móvil (Android/iOS)
- [ ] Soporte para Linux y macOS
- [ ] Grabación de sesiones
- [ ] Chat integrado
- [ ] Drag & drop para archivos

---

## Uso de Múltiples Monitores

### Servidor

**Ver monitores disponibles**:
```bash
python server.py
```

Salida:
```
[Servidor] Monitores disponibles: 2
  Monitor 1: 1920x1080 en (0, 0) (ACTIVO)
  Monitor 2: 1920x1080 en (1920, 0)
```

**Seleccionar monitor específico**:
```bash
# Segundo monitor
python server.py --monitor 2

# Tercer monitor
python server.py --monitor 3
```

**Con otros parámetros**:
```bash
python server.py --monitor 2 --port 5901 --password mi_contraseña
```

### Cliente

El cliente se conecta normalmente, no necesita saber qué monitor está capturando el servidor.

---

## Resumen de Correcciones v1.2

| Problema | Estado | Solución |
|----------|--------|----------|
| Ratón desalineado | ✅ Corregido | Sin escalado, coordenadas directas |
| Clics no funcionan | ✅ Corregido | Detección de cambios de estado |
| Teclado no funciona | ✅ Corregido | Mapeo completo de teclas |
| Pantalla cortada | ✅ Corregido | Tamaño real + scroll |
| Sin múltiples monitores | ✅ Implementado | Parámetro --monitor |

---

**Fecha de última actualización**: 15 de enero de 2026  
**Versión actual**: 1.2  
**Estado**: Estable y completamente funcional
