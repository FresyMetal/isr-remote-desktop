# Inicio Rápido - Aplicación de Escritorio Remoto

## 🚀 Opción 1: Ejecutar Sin Compilar (Más Fácil)

Esta es la forma más rápida de empezar si tienes Python instalado.

### Paso 1: Instalar Dependencias

Abre el símbolo del sistema en el directorio del proyecto y ejecuta:

```cmd
pip install -r requirements.txt
```

### Paso 2: Iniciar el Servidor

En el equipo que quieres controlar remotamente:

**Opción A: Doble clic**
- Haz doble clic en `IniciarServidor.bat`

**Opción B: Línea de comandos**
```cmd
python server.py
```

Verás algo como:
```
Servidor de Escritorio Remoto iniciado
Escuchando en 0.0.0.0:5900
IP local: 192.168.1.100
```

**¡Anota la IP!** La necesitarás para conectar.

### Paso 3: Iniciar el Cliente

En el equipo desde el que quieres controlar:

**Opción A: Doble clic**
- Haz doble clic en `IniciarCliente.bat`

**Opción B: Línea de comandos**
```cmd
python client.py
```

### Paso 4: Conectar

1. En la ventana del cliente, haz clic en **"Nueva Conexión"**
2. Ingresa los datos:
   - **Host**: La IP del servidor (ej: 192.168.1.100)
   - **Puerto**: 5900
   - **Contraseña**: (dejar vacío si no configuraste una)
3. Haz clic en **"OK"**

¡Listo! Deberías ver el escritorio remoto.

---

## 🔧 Opción 2: Compilar a Ejecutables

Si quieres crear archivos `.exe` para distribuir sin necesidad de Python.

### Método A: Scripts BAT (Recomendado)

1. **Instala PyInstaller**:
```cmd
pip install pyinstaller
```

2. **Compila el servidor**:
```cmd
build_server.bat
```

3. **Compila el cliente**:
```cmd
build_client.bat
```

4. **Los ejecutables estarán en** `dist/`:
   - `RemoteDesktopServer.exe`
   - `RemoteDesktopClient.exe`

### Método B: Script Python

```cmd
python build_windows.py
```

Esto compilará ambos y creará un paquete completo en `dist_package/`.

### Problemas al Compilar?

Si tienes errores al compilar, consulta `SOLUCION_PROBLEMAS_COMPILACION.md` para soluciones detalladas.

---

## 🎯 Funciones Principales

### Control Remoto
- **Ratón**: Mueve y haz clic normalmente
- **Teclado**: Escribe directamente en la ventana
- **Scroll**: Usa la rueda del ratón

### Transferir Archivos
1. Haz clic en el botón **"Transferir Archivos"**
2. Selecciona los archivos
3. Se enviarán automáticamente al servidor

### Portapapeles
- **Automático**: Se sincroniza solo
- **Manual**: Botón "Enviar Portapapeles"

### Múltiples Sesiones
- Haz clic en **"Nueva Conexión"** para otra sesión
- Usa las pestañas para cambiar entre sesiones
- Cada sesión es independiente

---

## 🔐 Configuración de Seguridad

### Servidor con Contraseña

```cmd
python server.py --password mi_contraseña_segura
```

O edita `IniciarServidor.bat`:
```batch
python server.py --password mi_contraseña_segura
```

### Puerto Personalizado

```cmd
python server.py --port 6000
```

---

## 🌐 Configuración de Red

### Firewall

Si no puedes conectar, permite el puerto en el firewall:

```cmd
netsh advfirewall firewall add rule name="Remote Desktop" dir=in action=allow protocol=TCP localport=5900
```

### Obtener tu IP

```cmd
ipconfig
```

Busca "Dirección IPv4" (ej: 192.168.1.100)

### Acceso desde Internet

1. Configura port forwarding en tu router (puerto 5900)
2. Usa tu IP pública para conectar
3. **Importante**: Usa contraseña fuerte

**Recomendado**: Usa VPN (Tailscale, WireGuard) en lugar de exponer el puerto.

---

## ❓ Problemas Comunes

### "No se puede conectar"

**Soluciones**:
1. Verifica que el servidor esté ejecutándose
2. Verifica la IP con `ipconfig`
3. Verifica el firewall
4. Prueba con `ping` a la IP del servidor

### "Error al importar módulos"

**Solución**:
```cmd
pip install -r requirements.txt
```

### "Python no reconocido"

**Solución**:
1. Instala Python desde python.org
2. Durante la instalación, marca "Add Python to PATH"
3. Reinicia el símbolo del sistema

### La imagen se ve lenta

**Soluciones**:
1. Verifica tu conexión de red
2. Cierra otras aplicaciones que usen red
3. Usa cable Ethernet en lugar de WiFi

---

## 📊 Requisitos del Sistema

### Mínimos
- Windows 7 SP1 o superior
- Python 3.11+ (si ejecutas sin compilar)
- 2 GB RAM
- Conexión de red

### Recomendados
- Windows 10/11
- 4 GB RAM
- Conexión de 10 Mbps o superior

---

## 📚 Documentación Completa

Para más información, consulta:

- **README.md**: Documentación completa
- **INSTALACION.md**: Guía detallada de instalación
- **SOLUCION_PROBLEMAS_COMPILACION.md**: Solución de problemas al compilar
- **RESUMEN_EJECUTIVO.md**: Visión general del proyecto

---

## 🎉 ¡Listo!

Ahora puedes:
- Controlar equipos remotamente
- Transferir archivos
- Compartir portapapeles
- Mantener múltiples sesiones

**¿Necesitas ayuda?** Revisa la documentación o los archivos de solución de problemas.

---

## 🔄 Comandos de Referencia Rápida

```cmd
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python server.py

# Ejecutar cliente
python client.py

# Servidor con contraseña
python server.py --password mi_contraseña

# Compilar (si quieres .exe)
build_server.bat
build_client.bat

# Ver IP
ipconfig

# Permitir firewall
netsh advfirewall firewall add rule name="Remote Desktop" dir=in action=allow protocol=TCP localport=5900
```

---

**¡Disfruta de tu aplicación de escritorio remoto!** 🚀
