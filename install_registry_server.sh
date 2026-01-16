#!/bin/bash
# Script de instalación del Servidor Central de Registro
# Para ISR Remote Desktop

set -e

echo "=========================================="
echo "  ISR Remote Desktop"
echo "  Instalación del Servidor Central"
echo "=========================================="
echo ""

# Verificar si se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    echo "⚠ Este script debe ejecutarse como root"
    echo "Usa: sudo bash install_registry_server.sh"
    exit 1
fi

# Verificar Python
echo "[1/5] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 no está instalado"
    echo "Instalando Python 3..."
    apt-get update
    apt-get install -y python3
fi
echo "✓ Python 3 instalado"

# Crear directorio
echo ""
echo "[2/5] Creando directorio..."
mkdir -p /opt/isr-remote-desktop
cd /opt/isr-remote-desktop

# Descargar archivos
echo ""
echo "[3/5] Descargando archivos..."
if command -v git &> /dev/null; then
    echo "Usando git clone..."
    git clone https://github.com/FresyMetal/isr-remote-desktop.git temp
    mv temp/* .
    rm -rf temp
else
    echo "Git no disponible, descargando ZIP..."
    apt-get install -y wget unzip
    wget https://github.com/FresyMetal/isr-remote-desktop/archive/refs/heads/main.zip
    unzip main.zip
    mv isr-remote-desktop-main/* .
    rm -rf isr-remote-desktop-main main.zip
fi
echo "✓ Archivos descargados"

# Crear servicio systemd
echo ""
echo "[4/5] Configurando servicio systemd..."
cat > /etc/systemd/system/isr-registry.service << EOF
[Unit]
Description=ISR Remote Desktop Registry Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/isr-remote-desktop
ExecStart=/usr/bin/python3 /opt/isr-remote-desktop/registry_server.py --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable isr-registry
echo "✓ Servicio configurado"

# Configurar firewall
echo ""
echo "[5/5] Configurando firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 8080/tcp
    echo "✓ Firewall configurado (ufw)"
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-port=8080/tcp
    firewall-cmd --reload
    echo "✓ Firewall configurado (firewalld)"
else
    echo "⚠ No se detectó firewall, configúralo manualmente"
fi

# Iniciar servicio
echo ""
echo "Iniciando servicio..."
systemctl start isr-registry

# Verificar estado
sleep 2
if systemctl is-active --quiet isr-registry; then
    echo ""
    echo "=========================================="
    echo "  ✓ INSTALACIÓN COMPLETADA"
    echo "=========================================="
    echo ""
    echo "El servidor está funcionando en:"
    echo "  http://$(hostname -I | awk '{print $1}'):8080"
    echo ""
    echo "Comandos útiles:"
    echo "  sudo systemctl status isr-registry   # Ver estado"
    echo "  sudo systemctl stop isr-registry     # Detener"
    echo "  sudo systemctl start isr-registry    # Iniciar"
    echo "  sudo systemctl restart isr-registry  # Reiniciar"
    echo "  sudo journalctl -u isr-registry -f   # Ver logs"
    echo ""
    echo "Abre en el navegador:"
    echo "  http://$(hostname -I | awk '{print $1}'):8080"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "  ✗ ERROR EN LA INSTALACIÓN"
    echo "=========================================="
    echo ""
    echo "El servicio no se pudo iniciar."
    echo "Revisa los logs:"
    echo "  sudo journalctl -u isr-registry -n 50"
    echo ""
    exit 1
fi
