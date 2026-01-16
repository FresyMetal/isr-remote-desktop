"""
Script para empaquetar la aplicación para Windows usando PyInstaller
Genera ejecutables standalone para servidor y cliente
"""

import os
import sys
import shutil
import subprocess


def check_pyinstaller():
    """Verifica si PyInstaller está instalado"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} encontrado")
        return True
    except ImportError:
        print("✗ PyInstaller no está instalado")
        print("  Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        return True


def build_server():
    """Construye el ejecutable del servidor"""
    print("\n=== Construyendo Servidor ===")
    
    # Comando básico sin opciones problemáticas
    command = [
        "pyinstaller",
        "--name=RemoteDesktopServer",
        "--onefile",
        "--console",  # Usar console en lugar de windowed para ver errores
        "--hidden-import=mss",
        "--hidden-import=mss.windows",
        "--hidden-import=pynput",
        "--hidden-import=pynput.keyboard",
        "--hidden-import=pynput.mouse",
        "--hidden-import=pyperclip",
        "--hidden-import=zstandard",
        "--hidden-import=cryptography",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--collect-all=mss",
        "--collect-all=pynput",
        "server.py"
    ]
    
    try:
        subprocess.check_call(command)
        print("✓ Servidor construido exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error al construir servidor: {e}")
        return False


def build_client():
    """Construye el ejecutable del cliente"""
    print("\n=== Construyendo Cliente ===")
    
    command = [
        "pyinstaller",
        "--name=RemoteDesktopClient",
        "--onefile",
        "--windowed",  # Sin consola para el cliente
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=pyperclip",
        "--hidden-import=zstandard",
        "--hidden-import=cryptography",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--collect-all=PyQt6",
        "client.py"
    ]
    
    try:
        subprocess.check_call(command)
        print("✓ Cliente construido exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error al construir cliente: {e}")
        return False


def create_distribution():
    """Crea el paquete de distribución"""
    print("\n=== Creando Paquete de Distribución ===")
    
    dist_dir = "dist_package"
    
    # Crear directorio de distribución
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Copiar ejecutables
    if os.path.exists("dist/RemoteDesktopServer.exe"):
        shutil.copy("dist/RemoteDesktopServer.exe", dist_dir)
        print("✓ Servidor copiado")
    else:
        print("⚠ Servidor no encontrado")
    
    if os.path.exists("dist/RemoteDesktopClient.exe"):
        shutil.copy("dist/RemoteDesktopClient.exe", dist_dir)
        print("✓ Cliente copiado")
    else:
        print("⚠ Cliente no encontrado")
    
    # Copiar documentación
    docs = ["README.md", "INSTALACION.md", "RESUMEN_EJECUTIVO.md"]
    for doc in docs:
        if os.path.exists(doc):
            shutil.copy(doc, dist_dir)
            print(f"✓ {doc} copiado")
    
    # Crear archivo de licencia
    license_path = os.path.join(dist_dir, "LICENSE.txt")
    with open(license_path, "w", encoding="utf-8") as f:
        f.write("MIT License\n\n")
        f.write("Copyright (c) 2026 Remote Desktop Application\n\n")
        f.write("Permission is hereby granted, free of charge, to any person obtaining a copy\n")
        f.write("of this software and associated documentation files (the \"Software\"), to deal\n")
        f.write("in the Software without restriction, including without limitation the rights\n")
        f.write("to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n")
        f.write("copies of the Software, and to permit persons to whom the Software is\n")
        f.write("furnished to do so, subject to the following conditions:\n\n")
        f.write("The above copyright notice and this permission notice shall be included in all\n")
        f.write("copies or substantial portions of the Software.\n\n")
        f.write("THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n")
        f.write("IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n")
        f.write("FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n")
        f.write("AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n")
        f.write("LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n")
        f.write("OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n")
        f.write("SOFTWARE.\n")
    print("✓ Licencia creada")
    
    # Crear guía rápida
    guia_path = os.path.join(dist_dir, "GUIA_RAPIDA.txt")
    with open(guia_path, "w", encoding="utf-8") as f:
        f.write("=== GUÍA RÁPIDA - APLICACIÓN DE ESCRITORIO REMOTO ===\n\n")
        f.write("SERVIDOR (Equipo al que deseas acceder):\n")
        f.write("1. Ejecuta RemoteDesktopServer.exe\n")
        f.write("2. El servidor iniciará en el puerto 5900\n")
        f.write("3. Anota la dirección IP de este equipo (ipconfig en CMD)\n\n")
        f.write("CLIENTE (Equipo desde el que deseas controlar):\n")
        f.write("1. Ejecuta RemoteDesktopClient.exe\n")
        f.write("2. Haz clic en 'Nueva Conexión'\n")
        f.write("3. Ingresa la IP del servidor y puerto 5900\n")
        f.write("4. Haz clic en OK para conectar\n\n")
        f.write("CARACTERÍSTICAS:\n")
        f.write("- Múltiples sesiones simultáneas (usa pestañas)\n")
        f.write("- Transferencia de archivos (botón en la barra)\n")
        f.write("- Portapapeles compartido (automático)\n")
        f.write("- Conexión segura con cifrado AES-256\n\n")
        f.write("FIREWALL:\n")
        f.write("Si no puedes conectar, permite el puerto 5900 en el firewall:\n")
        f.write("netsh advfirewall firewall add rule name=\"Remote Desktop\" dir=in action=allow protocol=TCP localport=5900\n\n")
        f.write("Para más información, consulta README.md\n")
    print("✓ Guía rápida creada")
    
    # Crear script de inicio para servidor
    start_server_path = os.path.join(dist_dir, "IniciarServidor.bat")
    with open(start_server_path, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("echo ========================================\n")
        f.write("echo   SERVIDOR DE ESCRITORIO REMOTO\n")
        f.write("echo ========================================\n")
        f.write("echo.\n")
        f.write("echo Iniciando servidor en puerto 5900...\n")
        f.write("echo.\n")
        f.write("RemoteDesktopServer.exe\n")
        f.write("pause\n")
    print("✓ Script de inicio del servidor creado")
    
    print(f"\n✓ Paquete de distribución creado en: {dist_dir}")
    print(f"  Tamaño total: {get_dir_size(dist_dir):.2f} MB")


def get_dir_size(path):
    """Calcula el tamaño de un directorio en MB"""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total += os.path.getsize(filepath)
    except Exception as e:
        print(f"Error calculando tamaño: {e}")
    return total / (1024 * 1024)


def clean_build_files():
    """Limpia archivos temporales de construcción"""
    print("\n=== Limpiando Archivos Temporales ===")
    
    dirs_to_remove = ["build", "__pycache__"]
    files_to_remove = ["RemoteDesktopServer.spec", "RemoteDesktopClient.spec"]
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"✓ Eliminado: {dir_name}")
            except Exception as e:
                print(f"⚠ No se pudo eliminar {dir_name}: {e}")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"✓ Eliminado: {file_name}")
            except Exception as e:
                print(f"⚠ No se pudo eliminar {file_name}: {e}")


def main():
    """Función principal"""
    print("=" * 60)
    print("  CONSTRUCCIÓN DE APLICACIÓN DE ESCRITORIO REMOTO")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("server.py") or not os.path.exists("client.py"):
        print("\n✗ Error: No se encuentran los archivos server.py y client.py")
        print("  Asegúrate de ejecutar este script desde el directorio del proyecto")
        return 1
    
    # Verificar PyInstaller
    if not check_pyinstaller():
        print("\n✗ No se pudo instalar PyInstaller")
        return 1
    
    # Construir servidor
    server_ok = build_server()
    
    # Construir cliente
    client_ok = build_client()
    
    # Si al menos uno fue exitoso, crear distribución
    if server_ok or client_ok:
        create_distribution()
    
    # Limpiar archivos temporales
    clean_build_files()
    
    print("\n" + "=" * 60)
    if server_ok and client_ok:
        print("  ✓ CONSTRUCCIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("\nLos ejecutables están listos en el directorio 'dist_package'")
        print("\nPuedes distribuir todo el contenido de 'dist_package' a los usuarios.")
        return 0
    else:
        print("  ⚠ CONSTRUCCIÓN COMPLETADA CON ADVERTENCIAS")
        print("=" * 60)
        if not server_ok:
            print("\n✗ El servidor no se pudo construir")
        if not client_ok:
            print("\n✗ El cliente no se pudo construir")
        print("\nRevisa los errores arriba para más detalles.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
