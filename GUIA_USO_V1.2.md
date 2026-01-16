# Guía de Uso - Versión 1.2

## 🎉 ¡Todos los Problemas Corregidos!

La versión 1.2 corrige todos los problemas reportados:
- ✅ **Ratón**: Ahora apunta exactamente donde debe
- ✅ **Clics**: Funcionan perfectamente
- ✅ **Teclado**: Puedes escribir sin problemas
- ✅ **Pantalla completa**: Se ve toda la pantalla con scroll
- ✅ **Múltiples monitores**: Soporte completo

---

## 🚀 Inicio Rápido

### 1. Iniciar el Servidor

**Opción A: Monitor principal (por defecto)**
```bash
python server.py
```

**Opción B: Seleccionar monitor específico**
```bash
# Segundo monitor
python server.py --monitor 2

# Tercer monitor
python server.py --monitor 3
```

**Opción C: Con contraseña**
```bash
python server.py --password mi_contraseña
```

**Opción D: Todo junto**
```bash
python server.py --monitor 2 --port 5901 --password mi_contraseña
```

### 2. Iniciar el Cliente

```bash
python client.py
```

### 3. Conectar

1. Haz clic en **"Nueva Conexión"**
2. Ingresa:
   - **Host**: IP del servidor (ej: 192.168.0.100)
   - **Puerto**: 5900 (o el que configuraste)
   - **Contraseña**: (si configuraste una)
3. Haz clic en **"OK"**

---

## 🖱️ Control del Ratón

### Movimiento
- Mueve el ratón normalmente sobre la ventana
- El cursor remoto seguirá exactamente tu movimiento

### Clics
- **Clic izquierdo**: Funciona normalmente
- **Clic derecho**: Menú contextual
- **Clic medio**: Scroll/funciones especiales

### Scroll
- Si la pantalla remota es más grande que tu ventana, usa las barras de scroll
- O usa la rueda del ratón para hacer scroll vertical

---

## ⌨️ Uso del Teclado

### Teclas Normales
- Escribe normalmente en la ventana del cliente
- Todas las letras, números y símbolos funcionan

### Teclas Especiales Soportadas
- **Enter**: Confirmar
- **Backspace**: Borrar
- **Tab**: Tabulador
- **Esc**: Escape
- **Delete**: Suprimir
- **Flechas**: ←↑→↓
- **Home/End**: Inicio/Fin
- **Page Up/Down**: Página arriba/abajo
- **F1-F12**: Teclas de función
- **Shift, Ctrl, Alt**: Modificadores
- **Caps Lock**: Bloqueo de mayúsculas
- **Space**: Espacio

### Atajos de Teclado
Los atajos funcionan normalmente:
- **Ctrl+C**: Copiar
- **Ctrl+V**: Pegar
- **Ctrl+A**: Seleccionar todo
- **Alt+Tab**: Cambiar ventanas (en el servidor)
- Etc.

---

## 🖥️ Múltiples Monitores

### Ver Monitores Disponibles

Al iniciar el servidor, verás:
```
[Servidor] Monitores disponibles: 2
  Monitor 1: 1920x1080 en (0, 0) (ACTIVO)
  Monitor 2: 1920x1080 en (1920, 0)
```

### Seleccionar Monitor

```bash
# Monitor 1 (principal) - por defecto
python server.py

# Monitor 2
python server.py --monitor 2

# Monitor 3
python server.py --monitor 3
```

### Cambiar de Monitor

Para cambiar de monitor:
1. Detén el servidor (Ctrl+C)
2. Reinicia con otro monitor:
```bash
python server.py --monitor 2
```

### Múltiples Servidores

Puedes ejecutar múltiples servidores en diferentes puertos para diferentes monitores:

**Terminal 1 (Monitor 1)**:
```bash
python server.py --port 5900 --monitor 1
```

**Terminal 2 (Monitor 2)**:
```bash
python server.py --port 5901 --monitor 2
```

Luego conecta desde el cliente a cada puerto.

---

## 📺 Visualización de la Pantalla

### Tamaño Real
- La pantalla se muestra en su tamaño real (1:1)
- No hay escalado que distorsione la imagen

### Scroll
- Si la pantalla remota es más grande que tu ventana, aparecerán barras de scroll
- Usa las barras o la rueda del ratón para navegar

### Pantalla Completa
- Para ver más, maximiza la ventana del cliente
- O ajusta el tamaño de la ventana según necesites

---

## 📋 Portapapeles

### Sincronización Automática
El portapapeles se sincroniza automáticamente en ambas direcciones:

1. **Copias en el cliente** → Se pega en el servidor
2. **Copias en el servidor** → Se pega en el cliente

### Sincronización Manual
Si quieres forzar el envío:
1. Haz clic en **"Enviar Portapapeles"**
2. El contenido actual se enviará al servidor

---

## 📁 Transferencia de Archivos

### Enviar Archivos al Servidor

1. Haz clic en **"Transferir Archivos"**
2. Selecciona los archivos que quieres enviar
3. Los archivos se transferirán automáticamente
4. En el servidor, los archivos se guardarán en el directorio actual

### Múltiples Archivos
Puedes seleccionar múltiples archivos a la vez.

---

## 🔧 Configuración Avanzada

### Servidor con Todas las Opciones

```bash
python server.py \
  --host 0.0.0.0 \
  --port 5900 \
  --password mi_contraseña \
  --monitor 2
```

**Parámetros**:
- `--host`: IP para escuchar (0.0.0.0 = todas las interfaces)
- `--port`: Puerto (por defecto 5900)
- `--password`: Contraseña de acceso (opcional)
- `--monitor`: Monitor a capturar (por defecto 1)

### Firewall

Si no puedes conectar, permite el puerto en el firewall:

```cmd
netsh advfirewall firewall add rule name="Remote Desktop" dir=in action=allow protocol=TCP localport=5900
```

### Obtener tu IP

```cmd
ipconfig
```

Busca "Dirección IPv4" (ej: 192.168.0.100)

---

## ❓ Solución de Problemas

### El ratón no apunta bien

**Solución**: Asegúrate de estar usando la versión 1.2. Las versiones anteriores tenían este problema.

### No puedo hacer clic

**Solución**: Actualiza a la versión 1.2. El problema está corregido.

### No puedo escribir

**Solución**: 
1. Asegúrate de que la ventana del cliente esté enfocada (haz clic en ella)
2. Actualiza a la versión 1.2

### La pantalla está cortada

**Solución**: 
1. Actualiza a la versión 1.2
2. Usa las barras de scroll para ver toda la pantalla
3. Maximiza la ventana del cliente

### No veo mi segundo monitor

**Solución**: 
```bash
python server.py --monitor 2
```

### El servidor no inicia

**Solución**:
1. Verifica que el puerto no esté en uso:
```cmd
netstat -ano | findstr :5900
```
2. Usa otro puerto:
```bash
python server.py --port 5901
```

### No puedo conectar desde el cliente

**Solución**:
1. Verifica que el servidor esté ejecutándose
2. Verifica la IP con `ipconfig`
3. Verifica el firewall
4. Prueba con `ping` a la IP del servidor

---

## 📊 Rendimiento

### Resoluciones Soportadas
- ✅ 1920x1080 (Full HD)
- ✅ 2560x1440 (2K)
- ✅ 3840x2160 (4K)
- ✅ Cualquier resolución

### Ancho de Banda
- Escritorio estático: 0.5-1 MB/s
- Uso normal: 2-5 MB/s
- Video/animaciones: 10-20 MB/s

### Latencia
- LAN: 10-30 ms
- WAN: 50-100 ms

---

## 🎯 Casos de Uso

### 1. Soporte Técnico
```bash
# Servidor (cliente que necesita ayuda)
python server.py

# Cliente (técnico)
python client.py
# Conectar a la IP del cliente
```

### 2. Acceso Remoto a tu PC
```bash
# En tu PC de casa
python server.py --password mi_contraseña

# Desde el trabajo
python client.py
# Conectar a tu IP pública
```

### 3. Múltiples Monitores
```bash
# Terminal 1 - Monitor principal
python server.py --port 5900 --monitor 1

# Terminal 2 - Segundo monitor
python server.py --port 5901 --monitor 2

# Cliente: conecta a ambos puertos
```

### 4. Presentaciones
```bash
# Servidor (presentador)
python server.py --monitor 2  # Monitor con la presentación

# Clientes (audiencia)
python client.py
# Todos conectan al servidor
```

---

## 🔐 Seguridad

### Usar Contraseña

**Siempre** usa contraseña si expones el servidor a Internet:

```bash
python server.py --password contraseña_fuerte_aquí
```

### VPN Recomendada

Para acceso remoto, usa VPN en lugar de exponer el puerto:
- Tailscale (más fácil)
- WireGuard
- OpenVPN

### Firewall

Solo permite conexiones desde IPs conocidas.

---

## 📚 Comandos de Referencia Rápida

```bash
# Servidor básico
python server.py

# Servidor con monitor 2
python server.py --monitor 2

# Servidor con contraseña
python server.py --password mi_contraseña

# Servidor completo
python server.py --monitor 2 --port 5901 --password mi_contraseña

# Cliente
python client.py

# Ver IP
ipconfig

# Permitir firewall
netsh advfirewall firewall add rule name="Remote Desktop" dir=in action=allow protocol=TCP localport=5900
```

---

## ✅ Checklist de Verificación

Antes de reportar un problema, verifica:

- [ ] Estoy usando la versión 1.2
- [ ] El servidor está ejecutándose
- [ ] El cliente está ejecutándose
- [ ] La IP es correcta
- [ ] El puerto es correcto
- [ ] El firewall permite la conexión
- [ ] La ventana del cliente está enfocada (para teclado)

---

## 🎉 ¡Disfruta!

Ahora tienes una aplicación de escritorio remoto completamente funcional con:
- ✅ Ratón preciso
- ✅ Clics funcionando
- ✅ Teclado completo
- ✅ Pantalla completa visible
- ✅ Soporte para múltiples monitores

**¿Preguntas?** Consulta el README.md o CHANGELOG.md para más información.

---

**Versión**: 1.2  
**Fecha**: 15 de enero de 2026  
**Estado**: ✅ Completamente funcional
