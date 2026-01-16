# ISR Remote Desktop

<p align="center">
  <img src="logoisr2N.png" alt="ISR Comunicaciones" width="200"/>
</p>

<p align="center">
  <strong>Aplicación de Escritorio Remoto Profesional</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.1-blue.svg" alt="Version 2.1"/>
  <img src="https://img.shields.io/badge/python-3.11+-green.svg" alt="Python 3.11+"/>
  <img src="https://img.shields.io/badge/platform-Windows-lightgrey.svg" alt="Windows"/>
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License MIT"/>
</p>

---

## 📋 Descripción

**ISR Remote Desktop** es una aplicación de escritorio remoto completa y profesional desarrollada para ISR Comunicaciones. Permite controlar equipos remotos de forma segura, rápida y eficiente.

### ✨ Características Principales

- 🖥️ **Control remoto completo** - Ratón, teclado y visualización en tiempo real
- 🔢 **Sistema de códigos** - Conecta usando códigos simples (ej: ISR-12345678) en lugar de IPs
- 📁 **Transferencia de archivos bidireccional** - Envía y recibe archivos fácilmente
- 📋 **Portapapeles compartido** - Sincronización automática en ambas direcciones
- 🖼️ **Múltiples monitores** - Soporte completo para configuraciones multi-monitor
- 🔄 **Múltiples sesiones** - Conecta a varios equipos simultáneamente
- 🔒 **Seguridad** - Cifrado AES-256-GCM de extremo a extremo
- 📜 **Historial de conexiones** - Reconecta con un solo clic
- 🎨 **Interfaz moderna** - Botones con iconos, system tray, ventanas ocultas

---

## 🚀 Inicio Rápido

### Requisitos

- **Python 3.11+**
- **Windows 10/11** (por ahora)
- **Permisos de administrador** (para el servidor)

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/isr-remote-desktop.git
cd isr-remote-desktop

# Instalar dependencias
pip install -r requirements.txt
```

### Uso Básico

#### Servidor (Equipo a controlar):

```cmd
# Ejecutar como administrador
python server.py
```

Verás:
```
========================================
  SERVIDOR DE ESCRITORIO REMOTO
========================================
Código de conexión: ISR-87654321
IP local: 192.168.1.100:5900
========================================
```

#### Cliente (Equipo desde donde controlas):

```cmd
python client.py
```

1. Clic en "Nueva Conexión"
2. Escribe el código: `ISR-87654321`
3. ¡Conectado!

---

## 📚 Documentación

### Guías de Usuario

- [**Guía de Inicio Rápido**](INICIO_RAPIDO.md) - Empieza en 5 minutos
- [**Guía de Instalación**](INSTALACION.md) - Instalación detallada
- [**Novedades v2.1**](NOVEDADES_V2.1.md) - Últimas funcionalidades

### Documentación Técnica

- [**Arquitectura**](arquitectura.md) - Diseño del sistema
- [**Protocolo de Red**](investigacion_tecnologias.md) - Detalles del protocolo
- [**Solución de Problemas**](SOLUCION_DEFINITIVA_V1.5.md) - Problemas comunes

### Compilación

- [**Compilar a EXE**](SOLUCION_COMPILACION.md) - Crear ejecutables
- [**Script de Compilación**](compilar.bat) - Compilación automática

---

## 🎯 Características Detalladas

### Sistema de Códigos de Conexión

Similar a AnyDesk, usa códigos simples en lugar de IPs:

```
Servidor: ISR-12345678
Cliente: Conecta con ISR-12345678
```

**Ventajas**:
- ✅ Fácil de recordar
- ✅ Fácil de compartir
- ✅ No cambia con la red

### Historial de Conexiones

Reconecta rápidamente a tus servidores favoritos:

```
[🔗 ISR-12345678] [🔗 Oficina] [🔗 Casa]
```

Un clic y estás conectado.

### Múltiples Monitores

Cambia entre monitores sin cerrar la conexión:

```
[◀] [▶]  ← Botones de navegación
```

### Modos de Visualización

Tres modos para adaptarse a tus necesidades:

- **▣ Escalado** - Pantalla completa escalada
- **⇕ Scroll** - Tamaño real con scroll
- **⛶ Pantalla Completa** - Modo inmersivo

---

## 🔧 Configuración Avanzada

### Servidor

```bash
# Puerto personalizado
python server.py --port 5901

# Monitor específico
python server.py --monitor 2

# Código personalizado
python server.py --code MiServidor

# Con contraseña
python server.py --password mi_contraseña

# Todo junto
python server.py --code Oficina --port 5901 --monitor 2 --password secreto
```

### Cliente

El cliente se configura desde la interfaz gráfica.

---

## 📦 Estructura del Proyecto

```
isr-remote-desktop/
├── server.py                  # Servidor de escritorio remoto
├── client.py                  # Cliente con interfaz gráfica
├── protocol.py                # Protocolo de comunicación
├── connection_code.py         # Sistema de códigos
├── file_transfer.py           # Transferencia de archivos
├── security.py                # Cifrado y seguridad
├── icon.ico                   # Icono de la aplicación
├── logoisr2N.png             # Logo ISR
├── requirements.txt           # Dependencias Python
├── compilar.bat              # Script de compilación
├── IniciarServidor.bat       # Ejecutar servidor
├── IniciarCliente.bat        # Ejecutar cliente
└── docs/                     # Documentación adicional
```

---

## 🛠️ Desarrollo

### Tecnologías Utilizadas

- **Python 3.11** - Lenguaje principal
- **PyQt6** - Interfaz gráfica
- **mss** - Captura de pantalla
- **pynput** - Control de ratón y teclado
- **Pillow** - Procesamiento de imágenes
- **pyperclip** - Gestión del portapapeles
- **cryptography** - Cifrado AES-256-GCM

### Arquitectura

```
Cliente                    Servidor
  │                          │
  ├─ Interfaz PyQt6          ├─ Captura de pantalla (mss)
  ├─ Eventos de entrada      ├─ Control de entrada (pynput)
  ├─ Visualización           ├─ Compresión de imágenes
  │                          │
  └────── Protocolo TCP ──────┘
         (Cifrado AES-256)
```

---

## 🔒 Seguridad

- **Cifrado AES-256-GCM** - Comunicación cifrada de extremo a extremo
- **Autenticación opcional** - Protección con contraseña
- **Sin telemetría** - Sin recopilación de datos
- **Código abierto** - Auditable y transparente

---

## 📊 Rendimiento

| Métrica | Valor |
|---------|-------|
| Latencia (LAN) | 10-30 ms |
| FPS | Hasta 60 |
| Compresión | JPEG + Zstandard |
| Ancho de banda | 1-10 Mbps |

---

## 🗺️ Roadmap

### v2.2 (Próximamente)

- [ ] Servidor de registro central en la nube
- [ ] Conexión desde cualquier red sin port forwarding
- [ ] Actualización automática de IPs
- [ ] Aplicación móvil (Android/iOS)

### v2.3 (Futuro)

- [ ] Soporte para Linux y macOS
- [ ] Grabación de sesiones
- [ ] Chat integrado
- [ ] Drag & drop para archivos
- [ ] Audio remoto

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 👥 Autores

- **ISR Comunicaciones** - *Proyecto inicial*

---

## 🙏 Agradecimientos

- Inspirado en AnyDesk y TeamViewer
- Desarrollado con ❤️ para ISR Comunicaciones

---

## 📞 Soporte

¿Problemas o preguntas?

- 📧 Email: soporte@isrcomunicaciones.com
- 🌐 Web: https://isrcomunicaciones.com
- 📱 Teléfono: [Tu teléfono]

---

<p align="center">
  Hecho con ❤️ por ISR Comunicaciones
</p>
