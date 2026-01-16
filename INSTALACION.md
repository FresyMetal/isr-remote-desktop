# Guía de Instalación y Configuración

Esta guía te ayudará a instalar y configurar la aplicación de escritorio remoto en Windows.

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación desde Ejecutables](#instalación-desde-ejecutables)
3. [Instalación desde Código Fuente](#instalación-desde-código-fuente)
4. [Configuración Inicial](#configuración-inicial)
5. [Primer Uso](#primer-uso)
6. [Configuración Avanzada](#configuración-avanzada)
7. [Solución de Problemas](#solución-de-problemas)

## Requisitos Previos

### Sistema Operativo
- Windows 7 SP1 o superior
- Windows 10/11 recomendado

### Hardware
- Procesador: Intel Core i3 o equivalente
- RAM: 2 GB mínimo (4 GB recomendado)
- Espacio en disco: 100 MB para la aplicación
- Tarjeta de red: 100 Mbps o superior

### Red
- Conexión de red activa (LAN o Internet)
- Acceso al firewall para configuración de puertos

## Instalación desde Ejecutables

Esta es la forma más sencilla y recomendada para usuarios finales.

### Paso 1: Descargar

1. Descarga el paquete `RemoteDesktop-v1.0-Windows.zip` desde la sección de Releases
2. Extrae el archivo ZIP en una ubicación de tu preferencia (ej: `C:\RemoteDesktop`)

### Paso 2: Contenido del Paquete

El paquete incluye:
- `RemoteDesktopServer.exe` - Servidor de escritorio remoto
- `RemoteDesktopClient.exe` - Cliente con interfaz gráfica
- `README.md` - Documentación completa
- `LICENSE.txt` - Licencia del software
- `GUIA_RAPIDA.txt` - Guía de inicio rápido

### Paso 3: Configurar Firewall

Para permitir conexiones, debes configurar el firewall de Windows:

**Método 1: Automático (Recomendado)**
1. Ejecuta `RemoteDesktopServer.exe` por primera vez
2. Windows mostrará una alerta del firewall
3. Marca "Redes privadas" y haz clic en "Permitir acceso"

**Método 2: Manual**
1. Abre el símbolo del sistema como administrador
2. Ejecuta el siguiente comando:
```cmd
netsh advfirewall firewall add rule name="Remote Desktop Server" dir=in action=allow protocol=TCP localport=5900
```

### Paso 4: Crear Accesos Directos (Opcional)

Para facilitar el acceso:

1. Haz clic derecho en `RemoteDesktopServer.exe` → Enviar a → Escritorio (crear acceso directo)
2. Haz clic derecho en `RemoteDesktopClient.exe` → Enviar a → Escritorio (crear acceso directo)

## Instalación desde Código Fuente

Para desarrolladores o usuarios avanzados que desean ejecutar desde el código fuente.

### Paso 1: Instalar Python

1. Descarga Python 3.11 o superior desde https://www.python.org/downloads/
2. Durante la instalación, marca "Add Python to PATH"
3. Completa la instalación

### Paso 2: Verificar Instalación

Abre el símbolo del sistema y ejecuta:
```cmd
python --version
```

Deberías ver algo como: `Python 3.11.0`

### Paso 3: Descargar el Código Fuente

**Opción A: Usando Git**
```cmd
git clone https://github.com/usuario/remote-desktop.git
cd remote-desktop
```

**Opción B: Descarga Manual**
1. Descarga el ZIP del repositorio
2. Extrae en una carpeta
3. Abre el símbolo del sistema en esa carpeta

### Paso 4: Instalar Dependencias

```cmd
pip install -r requirements.txt
```

Esto instalará todas las bibliotecas necesarias:
- PyQt6
- Pillow
- mss
- pynput
- pyperclip
- zstandard
- cryptography

### Paso 5: Verificar Instalación

```cmd
python -c "import PyQt6; import mss; import pynput; print('OK')"
```

Si no hay errores, la instalación fue exitosa.

## Configuración Inicial

### Configurar el Servidor

#### Opción 1: Configuración Básica (Sin Contraseña)

Para uso en red local confiable:

```cmd
RemoteDesktopServer.exe
```

O desde código fuente:
```cmd
python server.py
```

El servidor iniciará en:
- Host: 0.0.0.0 (todas las interfaces)
- Puerto: 5900
- Contraseña: ninguna

#### Opción 2: Configuración con Contraseña

Para mayor seguridad:

```cmd
RemoteDesktopServer.exe --password mi_contraseña_segura
```

O desde código fuente:
```cmd
python server.py --password mi_contraseña_segura
```

#### Opción 3: Configuración Personalizada

```cmd
RemoteDesktopServer.exe --host 192.168.1.100 --port 5900 --password mi_contraseña
```

Parámetros:
- `--host`: IP específica para escuchar (útil si tienes múltiples interfaces de red)
- `--port`: Puerto personalizado (por defecto 5900)
- `--password`: Contraseña de acceso

### Obtener tu Dirección IP

Para que otros equipos puedan conectarse, necesitas tu dirección IP:

**Método 1: Símbolo del Sistema**
```cmd
ipconfig
```

Busca "Dirección IPv4" en tu adaptador de red activo (ej: 192.168.1.100)

**Método 2: Configuración de Red**
1. Abre Configuración → Red e Internet
2. Haz clic en "Propiedades" de tu red activa
3. Busca "Dirección IPv4"

### Configurar el Cliente

El cliente no requiere configuración previa. Simplemente ejecútalo:

```cmd
RemoteDesktopClient.exe
```

O desde código fuente:
```cmd
python client.py
```

## Primer Uso

### Escenario: Conectar dos equipos en la misma red

#### En el Equipo A (Servidor - el que será controlado):

1. Ejecuta `RemoteDesktopServer.exe`
2. Anota la dirección IP mostrada (ej: 192.168.1.100)
3. Deja el servidor ejecutándose

#### En el Equipo B (Cliente - el que controlará):

1. Ejecuta `RemoteDesktopClient.exe`
2. Haz clic en "Nueva Conexión"
3. Ingresa los datos:
   - Host: 192.168.1.100 (la IP del Equipo A)
   - Puerto: 5900
   - Contraseña: (dejar vacío si no configuraste contraseña)
4. Haz clic en "OK"

¡Listo! Deberías ver el escritorio del Equipo A en el Cliente.

### Probar Funciones Básicas

#### Control del Ratón y Teclado
- Mueve el ratón sobre la ventana del escritorio remoto
- Haz clic normalmente
- Escribe con el teclado (asegúrate de que la ventana esté enfocada)

#### Portapapeles
1. Copia texto en el Equipo B (Ctrl+C)
2. El texto se sincronizará automáticamente al Equipo A
3. Pega en el Equipo A (Ctrl+V)
4. Funciona en ambas direcciones

#### Transferencia de Archivos
1. Haz clic en "Transferir Archivos"
2. Selecciona uno o más archivos
3. Los archivos se enviarán al servidor
4. Verifica en el servidor que los archivos se recibieron

## Configuración Avanzada

### Ejecutar Servidor como Servicio de Windows

Para que el servidor inicie automáticamente con Windows:

1. Crea un archivo `start_server.bat`:
```batch
@echo off
cd C:\RemoteDesktop
RemoteDesktopServer.exe --password tu_contraseña
```

2. Crea un acceso directo del archivo .bat
3. Presiona Win+R, escribe `shell:startup`, presiona Enter
4. Copia el acceso directo a la carpeta que se abrió

### Configurar Puerto Personalizado

Si el puerto 5900 está en uso o quieres usar otro:

**Servidor:**
```cmd
RemoteDesktopServer.exe --port 6000
```

**Cliente:**
Al conectar, ingresa el puerto personalizado (6000)

### Acceso desde Internet

#### Paso 1: Configurar Port Forwarding en el Router

1. Accede a tu router (usualmente http://192.168.1.1)
2. Busca "Port Forwarding" o "Virtual Server"
3. Agrega una regla:
   - Nombre: Remote Desktop
   - Puerto externo: 5900
   - Puerto interno: 5900
   - IP interna: [IP de tu PC con el servidor]
   - Protocolo: TCP

#### Paso 2: Obtener tu IP Pública

Visita https://www.whatismyip.com/ desde el equipo servidor

#### Paso 3: Conectar desde Internet

En el cliente, usa tu IP pública en lugar de la IP local:
- Host: [Tu IP pública]
- Puerto: 5900

**⚠️ IMPORTANTE:** Usar una contraseña fuerte es crítico cuando expones el servidor a Internet.

### Usar con VPN (Recomendado)

Para mayor seguridad, usa una VPN en lugar de port forwarding:

#### Opción 1: Tailscale (Más Fácil)
1. Instala Tailscale en ambos equipos: https://tailscale.com/
2. Inicia sesión con la misma cuenta
3. Usa la IP de Tailscale para conectar (ej: 100.x.x.x)

#### Opción 2: WireGuard
1. Configura un servidor WireGuard
2. Conecta ambos equipos a la VPN
3. Usa las IPs de la VPN para conectar

### Múltiples Servidores en el Mismo Equipo

Puedes ejecutar múltiples instancias del servidor en diferentes puertos:

**Terminal 1:**
```cmd
RemoteDesktopServer.exe --port 5900
```

**Terminal 2:**
```cmd
RemoteDesktopServer.exe --port 5901
```

Cada instancia será independiente.

## Solución de Problemas

### El servidor no inicia

**Problema:** "Error: Address already in use"

**Solución:**
1. Verifica que no haya otra instancia ejecutándose
2. Verifica que el puerto no esté en uso:
```cmd
netstat -ano | findstr :5900
```
3. Si hay un proceso usando el puerto, termínalo o usa otro puerto

**Problema:** "Permission denied"

**Solución:**
- Ejecuta como administrador
- Verifica permisos del firewall

### No puedo conectar desde el cliente

**Problema:** "Connection refused"

**Solución:**
1. Verifica que el servidor esté ejecutándose
2. Verifica la IP del servidor:
```cmd
ipconfig
```
3. Prueba hacer ping:
```cmd
ping 192.168.1.100
```
4. Verifica el firewall en ambos equipos

**Problema:** "Connection timeout"

**Solución:**
1. Verifica que ambos equipos estén en la misma red
2. Verifica que no haya firewall bloqueando
3. Si es a través de Internet, verifica el port forwarding

### La imagen se ve lenta

**Solución:**
1. Verifica el ancho de banda de red
2. Cierra aplicaciones que usen mucho ancho de banda
3. Reduce la calidad en la configuración
4. Usa una conexión por cable en lugar de WiFi

### Error al transferir archivos

**Problema:** "Permission denied" al recibir archivos

**Solución:**
- Verifica permisos de escritura en el directorio destino
- Ejecuta el servidor con permisos adecuados

**Problema:** Archivos corruptos

**Solución:**
- Verifica la conexión de red
- Reintenta la transferencia
- Verifica el espacio en disco

### El portapapeles no funciona

**Solución:**
1. Reinicia ambas aplicaciones
2. Verifica que tengas permisos de acceso al portapapeles
3. Cierra otras aplicaciones que puedan interferir con el portapapeles

### Error de cifrado

**Problema:** "Decryption failed"

**Solución:**
- Verifica que ambos usen la misma contraseña
- Reinicia la conexión
- Verifica que las versiones del cliente y servidor sean compatibles

## Desinstalación

### Desde Ejecutables

1. Cierra todas las instancias del servidor y cliente
2. Elimina la carpeta donde instalaste la aplicación
3. Elimina los accesos directos del escritorio/menú inicio
4. (Opcional) Elimina la regla del firewall:
```cmd
netsh advfirewall firewall delete rule name="Remote Desktop Server"
```

### Desde Código Fuente

1. Cierra todas las instancias
2. Elimina la carpeta del proyecto
3. (Opcional) Desinstala las dependencias:
```cmd
pip uninstall -r requirements.txt -y
```

## Soporte Adicional

Si sigues teniendo problemas:

1. Consulta la documentación completa en `README.md`
2. Revisa los logs de la aplicación
3. Reporta el problema en GitHub Issues
4. Contacta al soporte técnico

## Próximos Pasos

Una vez que tengas todo funcionando:

1. Explora las características avanzadas
2. Configura accesos directos para uso frecuente
3. Considera configurar una VPN para acceso remoto seguro
4. Lee sobre las mejores prácticas de seguridad

¡Disfruta de tu aplicación de escritorio remoto!
