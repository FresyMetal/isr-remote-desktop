# Aplicación de Escritorio Remoto

Una aplicación de escritorio remoto completa para Windows con soporte para múltiples sesiones simultáneas, transferencia de archivos bidireccional, portapapeles compartido y conexión segura.

## Características

### Principales
- **Escritorio remoto en tiempo real**: Visualización y control completo del escritorio remoto con baja latencia
- **Múltiples sesiones simultáneas**: Conecta a varios equipos al mismo tiempo usando pestañas
- **Transferencia de archivos bidireccional**: Envía y recibe archivos fácilmente
- **Portapapeles compartido**: Sincronización automática del portapapeles entre equipos
- **Conexión segura**: Cifrado AES-256-GCM de extremo a extremo
- **Alto rendimiento**: Captura de pantalla optimizada y compresión eficiente

### Técnicas
- Protocolo personalizado basado en RFB/VNC
- Compresión Zstandard para datos de red
- Compresión JPEG para frames de video
- Detección de cambios para optimizar ancho de banda
- Arquitectura cliente-servidor con threading asíncrono

## Requisitos del Sistema

### Windows
- Windows 7 SP1 o superior (recomendado Windows 10/11)
- 2 GB RAM mínimo (4 GB recomendado)
- Conexión de red (LAN o Internet)
- Python 3.11+ (para ejecutar desde código fuente)

### Dependencias Python
- PyQt6: Interfaz gráfica
- Pillow: Procesamiento de imágenes
- mss: Captura de pantalla (multiplataforma)
- pynput: Control de entrada
- pyperclip: Gestión del portapapeles
- zstandard: Compresión de datos
- cryptography: Cifrado y seguridad

## Instalación

### Opción 1: Ejecutable (Recomendado para usuarios finales)

1. Descarga el instalador desde la sección de Releases
2. Ejecuta el instalador y sigue las instrucciones
3. La aplicación se instalará en `C:\Program Files\RemoteDesktop`
4. Se crearán accesos directos en el escritorio y menú inicio

### Opción 2: Desde código fuente (Para desarrolladores)

1. Clona el repositorio:
```bash
git clone https://github.com/usuario/remote-desktop.git
cd remote-desktop
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecuta el servidor:
```bash
python server.py
```

4. Ejecuta el cliente:
```bash
python client.py
```

## Uso

### Configurar el Servidor

El servidor debe ejecutarse en el equipo al que deseas acceder remotamente.

#### Ejecución básica:
```bash
python server.py
```

Esto iniciará el servidor en `0.0.0.0:5900` (escucha en todas las interfaces).

#### Opciones avanzadas:
```bash
python server.py --host 192.168.1.100 --port 5900 --password mi_contraseña
```

Parámetros:
- `--host`: Dirección IP para escuchar (por defecto: 0.0.0.0)
- `--port`: Puerto para escuchar (por defecto: 5900)
- `--password`: Contraseña de conexión (opcional, vacío = sin autenticación)

### Usar el Cliente

El cliente se ejecuta en el equipo desde el que deseas controlar otro equipo.

1. Ejecuta el cliente:
```bash
python client.py
```

2. Haz clic en **"Nueva Conexión"**

3. Ingresa los datos de conexión:
   - **Host**: Dirección IP o nombre del servidor (ej: 192.168.1.100)
   - **Puerto**: Puerto del servidor (por defecto: 5900)
   - **Contraseña**: Contraseña si el servidor la requiere

4. Haz clic en **"OK"** para conectar

5. Una vez conectado, verás el escritorio remoto en una nueva pestaña

### Funciones del Cliente

#### Control del Escritorio Remoto
- **Ratón**: Mueve el cursor y haz clic normalmente sobre la ventana del escritorio remoto
- **Teclado**: Escribe directamente en la ventana (asegúrate de que esté enfocada)
- **Scroll**: Usa la rueda del ratón para hacer scroll

#### Transferir Archivos
1. Haz clic en **"Transferir Archivos"**
2. Selecciona los archivos que deseas enviar
3. Los archivos se transferirán automáticamente al servidor
4. En el servidor, los archivos se guardarán en el directorio actual

#### Portapapeles Compartido
- **Automático**: El portapapeles se sincroniza automáticamente en ambas direcciones
- **Manual**: Haz clic en **"Enviar Portapapeles"** para forzar el envío

#### Múltiples Sesiones
- Haz clic en **"Nueva Conexión"** para abrir otra sesión
- Usa las pestañas para cambiar entre sesiones
- Cada sesión es independiente y puede conectarse a un servidor diferente
- Cierra una pestaña haciendo clic en la X

## Configuración Avanzada

### Configuración del Servidor

Puedes crear un archivo `server_config.json` para configuración persistente:

```json
{
    "host": "0.0.0.0",
    "port": 5900,
    "password": "",
    "max_clients": 5,
    "target_fps": 30,
    "compression_level": 3,
    "enable_encryption": true,
    "enable_clipboard": true,
    "enable_file_transfer": true
}
```

### Configuración del Cliente

Archivo `client_config.json`:

```json
{
    "default_port": 5900,
    "auto_reconnect": true,
    "reconnect_delay": 5,
    "max_reconnect_attempts": 3,
    "compression_level": 3,
    "video_quality": 75
}
```

### Configuración de Red

#### Firewall
Asegúrate de permitir el puerto 5900 (o el que hayas configurado) en el firewall:

**Windows Firewall:**
```cmd
netsh advfirewall firewall add rule name="Remote Desktop Server" dir=in action=allow protocol=TCP localport=5900
```

#### NAT/Port Forwarding
Si deseas acceder desde Internet, configura port forwarding en tu router:
1. Accede a la configuración de tu router (usualmente 192.168.1.1)
2. Busca la sección de Port Forwarding o Virtual Server
3. Agrega una regla:
   - Puerto externo: 5900
   - Puerto interno: 5900
   - IP interna: IP del equipo con el servidor
   - Protocolo: TCP

#### VPN (Recomendado para acceso remoto)
Para mayor seguridad, usa una VPN en lugar de exponer el puerto directamente:
- WireGuard
- OpenVPN
- Tailscale
- ZeroTier

## Seguridad

### Mejores Prácticas

1. **Usa contraseña fuerte**: Siempre configura una contraseña en el servidor
2. **Cifrado habilitado**: El cifrado AES-256 está habilitado por defecto
3. **Firewall**: Solo permite conexiones desde IPs conocidas
4. **VPN**: Usa VPN para acceso remoto en lugar de exponer el puerto
5. **Actualizaciones**: Mantén la aplicación actualizada

### Características de Seguridad

- **Cifrado AES-256-GCM**: Todos los datos se cifran de extremo a extremo
- **Autenticación con PSK**: Contraseña pre-compartida opcional
- **Rate limiting**: Protección contra ataques de fuerza bruta
- **Whitelist de IPs**: Opcional, restringe conexiones a IPs específicas
- **Verificación de integridad**: Checksums para transferencias de archivos

## Solución de Problemas

### El servidor no inicia
- Verifica que el puerto no esté en uso: `netstat -an | findstr 5900`
- Ejecuta como administrador si es necesario
- Verifica el firewall

### No puedo conectar desde el cliente
- Verifica que el servidor esté ejecutándose
- Verifica la dirección IP y puerto
- Verifica el firewall en ambos equipos
- Prueba con `ping` y `telnet` para verificar conectividad

### La imagen se ve lenta o entrecortada
- Reduce la calidad de video en la configuración
- Verifica el ancho de banda de red
- Cierra otras aplicaciones que usen la red
- Reduce el FPS objetivo en el servidor

### La transferencia de archivos falla
- Verifica el espacio en disco
- Verifica permisos de escritura
- Archivos muy grandes pueden tardar más tiempo

### El portapapeles no se sincroniza
- Verifica que ambos equipos tengan acceso al portapapeles
- Reinicia la conexión
- Verifica que la función esté habilitada en la configuración

## Desarrollo

### Estructura del Proyecto

```
remoto/
├── protocol.py          # Protocolo de comunicación
├── server.py            # Servidor de escritorio remoto
├── client.py            # Cliente con interfaz gráfica
├── file_transfer.py     # Gestor de transferencia de archivos
├── security.py          # Cifrado y autenticación
├── requirements.txt     # Dependencias Python
├── build_windows.py     # Script de empaquetado para Windows
├── README.md            # Este archivo
└── LICENSE              # Licencia del proyecto
```

### Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Agrega nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crea un Pull Request

### Roadmap

#### Versión 1.1
- [ ] Soporte para múltiples monitores
- [ ] Grabación de sesiones
- [ ] Chat integrado
- [ ] Transferencia de archivos con drag & drop

#### Versión 2.0
- [ ] Aplicación móvil (Android/iOS)
- [ ] Soporte para Linux y macOS
- [ ] Modo de solo visualización (sin control)
- [ ] Servidor relay para NAT traversal

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Créditos

Desarrollado por [Tu Nombre]

### Bibliotecas de Terceros
- PyQt6: GPL/Commercial
- Pillow: HPND License
- mss: MIT License
- pynput: LGPL
- pyperclip: BSD License
- zstandard: BSD License
- cryptography: Apache/BSD

## Soporte

Para reportar bugs o solicitar características:
- GitHub Issues: https://github.com/usuario/remote-desktop/issues
- Email: soporte@ejemplo.com

## FAQ

### ¿Es compatible con TeamViewer/AnyDesk?
No, esta es una aplicación independiente con su propio protocolo. No es compatible con otros software de escritorio remoto.

### ¿Puedo usar esto comercialmente?
Sí, la licencia MIT permite uso comercial.

### ¿Funciona a través de Internet?
Sí, pero debes configurar port forwarding en tu router o usar VPN.

### ¿Cuánto ancho de banda consume?
Depende de la resolución y actividad. En promedio:
- Escritorio estático: 0.5-1 MB/s
- Uso normal: 2-5 MB/s
- Video/juegos: 10-20 MB/s

### ¿Es seguro?
Sí, usa cifrado AES-256 de grado militar. Sin embargo, siempre usa contraseñas fuertes y considera usar VPN para acceso remoto.

### ¿Puedo ejecutar múltiples servidores?
Sí, solo usa puertos diferentes para cada servidor.

### ¿Funciona en redes corporativas?
Depende de las políticas de firewall de tu empresa. Consulta con tu departamento de IT.
