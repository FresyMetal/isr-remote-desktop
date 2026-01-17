# Configuración del Servidor Central en Linux

Esta guía explica cómo configurar el servidor central de registro en un servidor Linux con IP pública directa.

---

## 📋 Requisitos

- Servidor Linux (Ubuntu/Debian recomendado)
- IP pública directa (no detrás de NAT)
- Acceso SSH root o sudo
- Puerto 8080 disponible

---

## 🚀 Instalación Paso a Paso

### Paso 1: Conectar al Servidor

```bash
ssh usuario@TU_IP_PUBLICA
```

---

### Paso 2: Actualizar Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

---

### Paso 3: Instalar Dependencias

```bash
# Instalar Python 3 y Flask
sudo apt install python3 python3-flask python3-flask-cors git -y

# Verificar instalación
python3 --version
python3 -c "import flask; print('Flask OK')"
```

---

### Paso 4: Clonar Repositorio

```bash
cd /opt
sudo git clone https://github.com/FresyMetal/isr-remote-desktop.git
cd isr-remote-desktop
```

---

### Paso 5: Crear Servicio Systemd

```bash
sudo nano /etc/systemd/system/isr-registry.service
```

**Contenido del archivo**:

```ini
[Unit]
Description=ISR Remote Desktop Registry Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/isr-remote-desktop
ExecStart=/usr/bin/python3 /opt/isr-remote-desktop/registry_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Guardar**: `Ctrl+O`, `Enter`, `Ctrl+X`

---

### Paso 6: Configurar Firewall

```bash
# Verificar si ufw está activo
sudo ufw status

# Si está activo, permitir puerto 8080
sudo ufw allow 8080/tcp

# Si no está activo, activarlo (opcional)
sudo ufw enable
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 8080/tcp
```

---

### Paso 7: Habilitar e Iniciar Servicio

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar autoarranque
sudo systemctl enable isr-registry

# Iniciar servicio
sudo systemctl start isr-registry

# Verificar estado
sudo systemctl status isr-registry
```

**Debe mostrar**: `Active: active (running)` en verde

---

### Paso 8: Verificar Funcionamiento

```bash
# Probar localmente
curl http://localhost:8080/status

# Probar desde IP pública
curl http://$(curl -s ifconfig.me):8080/status
```

**Respuesta esperada**:
```json
{"success": true, "message": "ISR Registry Server is running"}
```

---

## 🔧 Comandos Útiles

### Ver Logs del Servidor

```bash
# Ver logs en tiempo real
sudo journalctl -u isr-registry -f

# Ver últimas 50 líneas
sudo journalctl -u isr-registry -n 50
```

---

### Reiniciar Servidor

```bash
sudo systemctl restart isr-registry
```

---

### Detener Servidor

```bash
sudo systemctl stop isr-registry
```

---

### Ver Estado

```bash
sudo systemctl status isr-registry
```

---

### Verificar Puerto

```bash
# Ver si el puerto 8080 está escuchando
sudo netstat -tlnp | grep 8080

# O con ss
sudo ss -tlnp | grep 8080
```

---

## 🧪 Pruebas

### Desde el Servidor Linux

```bash
# Test básico
curl http://localhost:8080/status

# Registrar código de prueba
curl -X POST http://localhost:8080/register \
  -H "Content-Type: application/json" \
  -d '{"code":"ISR-TEST1234","ip":"192.168.1.100","port":5900}'

# Resolver código
curl http://localhost:8080/resolve?code=ISR-TEST1234
```

---

### Desde Otro Ordenador

```bash
# Reemplaza TU_IP_PUBLICA con la IP del servidor
curl http://TU_IP_PUBLICA:8080/status
```

---

## 📝 Actualizar Código

Si hay actualizaciones en el repositorio:

```bash
cd /opt/isr-remote-desktop
sudo git pull
sudo systemctl restart isr-registry
```

---

## 🔍 Solución de Problemas

### El servicio no inicia

```bash
# Ver logs de error
sudo journalctl -u isr-registry -n 50

# Verificar que Flask está instalado
python3 -c "import flask; print('OK')"

# Probar manualmente
cd /opt/isr-remote-desktop
python3 registry_server.py
```

---

### Puerto no accesible desde Internet

```bash
# Verificar que el puerto está escuchando
sudo netstat -tlnp | grep 8080

# Verificar firewall
sudo ufw status

# Verificar que escucha en 0.0.0.0 (todas las interfaces)
sudo netstat -tlnp | grep 8080
# Debe mostrar: 0.0.0.0:8080
```

---

### Error "Address already in use"

```bash
# Ver qué proceso usa el puerto
sudo lsof -i :8080

# Matar proceso si es necesario
sudo kill -9 PID
```

---

## 🌐 Verificación Externa

Usa herramientas online para verificar que el puerto está abierto:

1. Ve a: https://www.yougetsignal.com/tools/open-ports/
2. Introduce tu IP pública
3. Introduce puerto: 8080
4. Clic "Check"

**Debe decir**: "Port 8080 is open on [tu IP]"

---

## 📊 Monitoreo

### Ver Conexiones Activas

```bash
# Ver conexiones al puerto 8080
sudo netstat -an | grep 8080
```

---

### Ver Uso de Recursos

```bash
# Ver uso de CPU y memoria del servicio
sudo systemctl status isr-registry
```

---

## 🔒 Seguridad (Opcional)

### Limitar Acceso por IP (si es necesario)

```bash
# Permitir solo IPs específicas
sudo ufw delete allow 8080/tcp
sudo ufw allow from 1.2.3.4 to any port 8080
sudo ufw allow from 5.6.7.8 to any port 8080
```

---

### Configurar HTTPS (Recomendado para producción)

```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado SSL (requiere dominio)
sudo certbot certonly --standalone -d tu-dominio.com
```

Luego modifica `registry_server.py` para usar SSL.

---

## ✅ Checklist de Configuración

- [ ] Servidor Linux actualizado
- [ ] Python 3 y Flask instalados
- [ ] Repositorio clonado en /opt/isr-remote-desktop
- [ ] Servicio systemd creado
- [ ] Firewall configurado (puerto 8080 abierto)
- [ ] Servicio iniciado y habilitado
- [ ] Verificado localmente (curl localhost:8080/status)
- [ ] Verificado externamente (curl IP_PUBLICA:8080/status)
- [ ] Puerto verificado online (yougetsignal.com)

---

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs: `sudo journalctl -u isr-registry -n 50`
2. Verifica el puerto: `sudo netstat -tlnp | grep 8080`
3. Prueba manualmente: `python3 registry_server.py`
4. Verifica firewall: `sudo ufw status`

---

**¡Servidor central configurado y funcionando!**
