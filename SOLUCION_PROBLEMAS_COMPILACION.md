# Solución de Problemas de Compilación

Esta guía te ayudará a resolver problemas comunes al compilar la aplicación con PyInstaller en Windows.

## Tabla de Contenidos

1. [Problemas Comunes](#problemas-comunes)
2. [Métodos de Compilación](#métodos-de-compilación)
3. [Soluciones Paso a Paso](#soluciones-paso-a-paso)
4. [Compilación Manual](#compilación-manual)
5. [Alternativas](#alternativas)

## Problemas Comunes

### Error: "No such file or directory: RemoteDesktopServer.spec"

**Causa**: PyInstaller está intentando crear archivos en un directorio que no existe o no tiene permisos.

**Solución**:
1. Asegúrate de estar en el directorio correcto del proyecto
2. Ejecuta el símbolo del sistema como administrador
3. Usa los scripts `.bat` individuales en lugar del script Python

### Error: "Module not found"

**Causa**: Faltan dependencias o PyInstaller no las detecta automáticamente.

**Solución**:
1. Instala todas las dependencias:
```cmd
pip install -r requirements.txt
```

2. Verifica que todas estén instaladas:
```cmd
pip list
```

### Error: "Permission denied"

**Causa**: Windows Defender o antivirus está bloqueando PyInstaller.

**Solución**:
1. Agrega una excepción en Windows Defender para la carpeta del proyecto
2. Temporalmente deshabilita el antivirus durante la compilación
3. Ejecuta como administrador

## Métodos de Compilación

### Método 1: Script Python (Recomendado)

```cmd
python build_windows.py
```

**Ventajas**:
- Compila ambos (servidor y cliente)
- Crea paquete de distribución completo
- Limpia archivos temporales

**Desventajas**:
- Puede fallar si hay problemas de permisos

### Método 2: Scripts BAT Individuales

**Para el servidor**:
```cmd
build_server.bat
```

**Para el cliente**:
```cmd
build_client.bat
```

**Ventajas**:
- Más simple
- Compila uno a la vez
- Más fácil de depurar

**Desventajas**:
- Debes ejecutar dos scripts
- No crea paquete de distribución

### Método 3: Comandos Manuales

Ver sección [Compilación Manual](#compilación-manual) más abajo.

## Soluciones Paso a Paso

### Solución 1: Usar Scripts BAT (Más Simple)

Esta es la forma más sencilla y confiable:

1. **Abre el símbolo del sistema** en el directorio del proyecto:
   - Shift + Clic derecho en la carpeta → "Abrir ventana de PowerShell aquí"
   - O navega con `cd` al directorio

2. **Compila el servidor**:
```cmd
build_server.bat
```

3. **Compila el cliente**:
```cmd
build_client.bat
```

4. **Los ejecutables estarán en** `dist/`:
   - `dist/RemoteDesktopServer.exe`
   - `dist/RemoteDesktopClient.exe`

### Solución 2: Ejecutar como Administrador

1. **Abre el símbolo del sistema como administrador**:
   - Busca "cmd" en el menú inicio
   - Clic derecho → "Ejecutar como administrador"

2. **Navega al directorio del proyecto**:
```cmd
cd C:\Users\TuUsuario\Downloads\remoto
```

3. **Ejecuta el script**:
```cmd
python build_windows.py
```

### Solución 3: Deshabilitar Antivirus Temporalmente

PyInstaller a veces es bloqueado por antivirus:

1. **Deshabilita Windows Defender temporalmente**:
   - Configuración → Actualización y seguridad → Seguridad de Windows
   - Protección contra virus y amenazas → Administrar configuración
   - Desactiva "Protección en tiempo real"

2. **Compila la aplicación**

3. **Reactiva la protección**

### Solución 4: Agregar Excepción en Windows Defender

1. **Abre Windows Security**

2. **Ve a "Protección contra virus y amenazas"**

3. **Haz clic en "Administrar configuración"**

4. **Desplázate hasta "Exclusiones"**

5. **Agrega la carpeta del proyecto como excepción**

6. **Intenta compilar nuevamente**

## Compilación Manual

Si los scripts no funcionan, puedes compilar manualmente:

### Compilar Servidor

```cmd
pyinstaller ^
  --name=RemoteDesktopServer ^
  --onefile ^
  --console ^
  --hidden-import=mss ^
  --hidden-import=mss.windows ^
  --hidden-import=pynput ^
  --hidden-import=pynput.keyboard ^
  --hidden-import=pynput.mouse ^
  --hidden-import=pyperclip ^
  --hidden-import=zstandard ^
  --hidden-import=cryptography ^
  --hidden-import=PIL ^
  --hidden-import=PIL.Image ^
  --collect-all=mss ^
  --collect-all=pynput ^
  server.py
```

### Compilar Cliente

```cmd
pyinstaller ^
  --name=RemoteDesktopClient ^
  --onefile ^
  --windowed ^
  --hidden-import=PyQt6 ^
  --hidden-import=PyQt6.QtCore ^
  --hidden-import=PyQt6.QtGui ^
  --hidden-import=PyQt6.QtWidgets ^
  --hidden-import=pyperclip ^
  --hidden-import=zstandard ^
  --hidden-import=cryptography ^
  --hidden-import=PIL ^
  --hidden-import=PIL.Image ^
  --collect-all=PyQt6 ^
  client.py
```

**Nota**: El símbolo `^` permite continuar el comando en la siguiente línea en Windows.

## Alternativas

### Alternativa 1: Ejecutar sin Compilar

Si la compilación sigue fallando, puedes ejecutar directamente con Python:

**Servidor**:
```cmd
python server.py
```

**Cliente**:
```cmd
python client.py
```

**Ventajas**:
- No requiere compilación
- Más fácil de depurar
- Funciona siempre

**Desventajas**:
- Requiere Python instalado
- Más lento al iniciar
- No es portable

### Alternativa 2: Crear Scripts BAT para Ejecución

Crea `IniciarServidor.bat`:
```batch
@echo off
python server.py
pause
```

Crea `IniciarCliente.bat`:
```batch
@echo off
python client.py
pause
```

Distribuye estos scripts junto con el código fuente.

### Alternativa 3: Usar cx_Freeze

Si PyInstaller no funciona, prueba cx_Freeze:

1. **Instala cx_Freeze**:
```cmd
pip install cx_Freeze
```

2. **Crea `setup.py`**:
```python
from cx_Freeze import setup, Executable

setup(
    name="RemoteDesktop",
    version="1.0",
    description="Aplicación de Escritorio Remoto",
    executables=[
        Executable("server.py", target_name="RemoteDesktopServer.exe"),
        Executable("client.py", target_name="RemoteDesktopClient.exe", base="Win32GUI")
    ]
)
```

3. **Compila**:
```cmd
python setup.py build
```

## Verificación Post-Compilación

Después de compilar exitosamente:

### 1. Verificar que los Ejecutables Existen

```cmd
dir dist
```

Deberías ver:
- `RemoteDesktopServer.exe`
- `RemoteDesktopClient.exe`

### 2. Probar el Servidor

```cmd
cd dist
RemoteDesktopServer.exe
```

Debería mostrar:
```
Servidor de Escritorio Remoto iniciado
Escuchando en 0.0.0.0:5900
```

### 3. Probar el Cliente

```cmd
RemoteDesktopClient.exe
```

Debería abrir la ventana de la aplicación.

### 4. Probar Conexión

1. Inicia el servidor
2. Inicia el cliente
3. Conecta a `localhost:5900`
4. Verifica que funcione

## Problemas Específicos de Windows

### Python 3.13

Si usas Python 3.13 (como en tu caso), puede haber problemas de compatibilidad:

**Solución**: Usa Python 3.11 o 3.12:

1. Descarga Python 3.11 desde python.org
2. Instala en un directorio diferente
3. Usa ese Python para compilar:
```cmd
C:\Python311\python.exe build_windows.py
```

### Rutas con Espacios

Si tu ruta tiene espacios (ej: `C:\Program Files\...`):

**Solución**: Usa comillas:
```cmd
cd "C:\Users\Fresy Metal\Downloads\remoto"
```

### Permisos de UAC

Si Windows UAC bloquea la ejecución:

**Solución**:
1. Clic derecho en el ejecutable → Propiedades
2. Pestaña "Compatibilidad"
3. Marca "Ejecutar como administrador"

## Logs y Depuración

### Ver Logs de PyInstaller

PyInstaller crea logs en:
- `build/RemoteDesktopServer/warn-RemoteDesktopServer.txt`
- `build/RemoteDesktopClient/warn-RemoteDesktopClient.txt`

Revisa estos archivos para ver advertencias y errores.

### Modo Verbose

Compila con más información:
```cmd
pyinstaller --log-level=DEBUG --onefile server.py
```

### Probar Importaciones

Antes de compilar, verifica que todo se importe correctamente:
```cmd
python -c "import server"
python -c "import client"
```

## Contacto y Soporte

Si ninguna solución funciona:

1. Revisa los logs de PyInstaller
2. Verifica que todas las dependencias estén instaladas
3. Intenta con Python 3.11 en lugar de 3.13
4. Usa la alternativa de ejecutar sin compilar

## Resumen de Comandos Rápidos

```cmd
# Instalar dependencias
pip install -r requirements.txt

# Instalar PyInstaller
pip install pyinstaller

# Compilar con scripts BAT (RECOMENDADO)
build_server.bat
build_client.bat

# O compilar con Python
python build_windows.py

# O ejecutar sin compilar
python server.py
python client.py
```

## Checklist de Verificación

Antes de compilar, verifica:

- [ ] Python 3.11 o 3.12 instalado (no 3.13)
- [ ] Todas las dependencias instaladas (`pip list`)
- [ ] Estás en el directorio correcto del proyecto
- [ ] Tienes permisos de escritura en el directorio
- [ ] Windows Defender no está bloqueando PyInstaller
- [ ] No hay espacios en la ruta del proyecto (o usas comillas)
- [ ] Ejecutas como administrador si es necesario

Si todos los checks están OK, la compilación debería funcionar.
