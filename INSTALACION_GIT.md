# Instalación desde GitHub

## 🚀 Instalación Rápida

### Requisitos Previos

- **Git** instalado
- **Python 3.11+** instalado
- **Windows 10/11**

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/FresyMetal/isr-remote-desktop.git
cd isr-remote-desktop
```

### Paso 2: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 3: Ejecutar

#### Servidor (como administrador):

```cmd
python server.py
```

#### Cliente:

```cmd
python client.py
```

---

## 📦 Instalación Detallada

### 1. Instalar Git

Si no tienes Git instalado:

**Windows**:
1. Descarga desde https://git-scm.com/download/win
2. Ejecuta el instalador
3. Usa las opciones por defecto

### 2. Instalar Python

Si no tienes Python 3.11+:

**Windows**:
1. Descarga desde https://www.python.org/downloads/
2. **IMPORTANTE**: Marca "Add Python to PATH"
3. Instala

Verifica la instalación:
```bash
python --version
# Debe mostrar: Python 3.11.x o superior
```

### 3. Clonar el Repositorio

Abre una terminal (cmd o PowerShell) y ejecuta:

```bash
# Navega a donde quieras instalar
cd C:\

# Clona el repositorio
git clone https://github.com/FresyMetal/isr-remote-desktop.git

# Entra al directorio
cd isr-remote-desktop
```

### 4. Instalar Dependencias

```bash
pip install -r requirements.txt
```

Si tienes problemas, intenta:
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Verificar Instalación

```bash
python -c "import PyQt6; import mss; import pynput; print('✓ Todo instalado correctamente')"
```

---

## 🎯 Uso

### Servidor

```cmd
# Navega al directorio
cd C:\isr-remote-desktop

# Ejecuta como administrador
python server.py
```

**Nota**: El servidor DEBE ejecutarse como administrador para que el ratón y teclado funcionen.

### Cliente

```cmd
# Navega al directorio
cd C:\isr-remote-desktop

# Ejecuta normalmente
python client.py
```

---

## 🔄 Actualizar

Para actualizar a la última versión:

```bash
cd C:\isr-remote-desktop
git pull origin main
pip install -r requirements.txt --upgrade
```

---

## 🐛 Solución de Problemas

### Error: "git no se reconoce como comando"

**Solución**: Instala Git o reinicia la terminal después de instalarlo.

### Error: "python no se reconoce como comando"

**Solución**: 
1. Reinstala Python marcando "Add Python to PATH"
2. O usa `py` en lugar de `python`

### Error: "No module named 'PyQt6'"

**Solución**:
```bash
pip install PyQt6
```

### Error: "Permission denied" al ejecutar servidor

**Solución**: Ejecuta como administrador:
1. Busca "cmd" en el menú de inicio
2. Clic derecho → "Ejecutar como administrador"
3. Navega al directorio y ejecuta `python server.py`

---

## 📁 Estructura del Proyecto

```
isr-remote-desktop/
├── server.py              # Servidor
├── client.py              # Cliente
├── protocol.py            # Protocolo
├── connection_code.py     # Sistema de códigos
├── file_transfer.py       # Transferencia de archivos
├── security.py            # Seguridad
├── requirements.txt       # Dependencias
├── README_GIT.md         # Documentación principal
└── docs/                 # Documentación adicional
```

---

## 🎉 ¡Listo!

Ahora puedes usar ISR Remote Desktop.

**Servidor**:
```
Código de conexión: ISR-12345678
```

**Cliente**:
```
Conecta con: ISR-12345678
```

---

## 🔗 Enlaces Útiles

- **Repositorio**: https://github.com/FresyMetal/isr-remote-desktop
- **Issues**: https://github.com/FresyMetal/isr-remote-desktop/issues
- **Releases**: https://github.com/FresyMetal/isr-remote-desktop/releases

---

## 📞 Soporte

¿Problemas? Abre un issue en GitHub:
https://github.com/FresyMetal/isr-remote-desktop/issues/new
