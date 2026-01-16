# Servidor Central de Registro

El servidor central permite que los clientes se conecten usando códigos (tipo AnyDesk) desde cualquier red, sin necesidad de conocer las IPs.

---

## 🎯 Arquitectura

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│   Servidor  │────────▶│ Servidor Central │◀────────│   Cliente   │
│  Windows    │ Registra│   Linux (CRM)    │ Resuelve│  Windows    │
│  (Remoto)   │  Código │  77.225.201.4    │  Código │  (Control)  │
└─────────────┘         └──────────────────┘         └─────────────┘
```

### Flujo:

1. **Servidor Windows** inicia y genera código `ISR-12345678`
2. **Servidor Windows** registra el código en el servidor central con su IP pública
3. **Cliente** introduce el código `ISR-12345678`
4. **Cliente** consulta al servidor central para obtener la IP
5. **Cliente** se conecta directamente al servidor Windows

---

## 📦 Instalación en Linux (Servidor CRM)

### Requisitos

- **Linux** (Ubuntu, Debian, CentOS, etc.)
- **Python 3.6+** (ya incluido en la mayoría de distribuciones)
- **Puerto 8080** abierto

### Paso 1: Clonar el Repositorio

```bash
cd /opt
git clone https://github.com/FresyMetal/isr-remote-desktop.git
cd isr-remote-desktop
```

### Paso 2: Ejecutar el Servidor

```bash
python3 registry_server.py
```

O especificar puerto:

```bash
python3 registry_server.py --port 8080
```

### Paso 3: Verificar

Abre un navegador y ve a:
```
http://77.225.201.4:8080
```

Deberías ver la página de administración del servidor.

---

## 🔧 Configuración como Servicio (systemd)

Para que el servidor se inicie automáticamente:

### 1. Crear archivo de servicio

```bash
sudo nano /etc/systemd/system/isr-registry.service
```

### 2. Contenido del archivo

```ini
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
```

### 3. Activar el servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable isr-registry
sudo systemctl start isr-registry
```

### 4. Verificar estado

```bash
sudo systemctl status isr-registry
```

### 5. Ver logs

```bash
sudo journalctl -u isr-registry -f
```

---

## 🔥 Configurar Firewall

### UFW (Ubuntu/Debian)

```bash
sudo ufw allow 8080/tcp
sudo ufw reload
```

### firewalld (CentOS/RHEL)

```bash
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

### iptables

```bash
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo service iptables save
```

---

## 🌐 API REST

El servidor expone una API REST simple:

### Endpoints

#### 1. Registrar Código

```http
POST /register?code=ISR-12345678&host=77.225.201.4&port=5900&name=MiServidor
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Código ISR-12345678 registrado correctamente",
  "code": "ISR-12345678",
  "host": "77.225.201.4",
  "port": 5900
}
```

#### 2. Resolver Código

```http
GET /resolve?code=ISR-12345678
```

**Respuesta:**
```json
{
  "success": true,
  "code": "ISR-12345678",
  "host": "77.225.201.4",
  "port": 5900
}
```

#### 3. Información de Código

```http
GET /info?code=ISR-12345678
```

**Respuesta:**
```json
{
  "success": true,
  "code": "ISR-12345678",
  "host": "77.225.201.4",
  "port": 5900,
  "name": "MiServidor",
  "last_update": 1234567890.0,
  "registered_at": 1234567890.0
}
```

#### 4. Listar Todos

```http
GET /list
```

**Respuesta:**
```json
{
  "success": true,
  "count": 2,
  "codes": {
    "ISR-12345678": {
      "host": "77.225.201.4",
      "port": 5900,
      "name": "Servidor1",
      "last_update": 1234567890.0
    },
    "ISR-87654321": {
      "host": "192.168.1.100",
      "port": 5900,
      "name": "Servidor2",
      "last_update": 1234567890.0
    }
  }
}
```

#### 5. Estado del Servidor

```http
GET /status
```

**Respuesta:**
```json
{
  "success": true,
  "status": "running",
  "registered_codes": 2,
  "version": "2.2"
}
```

---

## 🧹 Limpieza Automática

El servidor limpia automáticamente códigos antiguos (más de 24 horas sin actualizar).

Para cambiar el intervalo, modifica el código:

```python
server.start_cleanup_thread(interval_hours=1)  # Limpia cada hora
```

---

## 📊 Monitoreo

### Ver códigos registrados

Abre en el navegador:
```
http://77.225.201.4:8080
```

### Ver logs en tiempo real

```bash
sudo journalctl -u isr-registry -f
```

### Ver estadísticas

```bash
curl http://77.225.201.4:8080/status
```

---

## 🔒 Seguridad

### Recomendaciones:

1. **Firewall**: Solo abre el puerto 8080
2. **HTTPS**: Considera usar un proxy reverso (nginx) con SSL
3. **Rate Limiting**: Implementa límites de peticiones
4. **Autenticación**: Agrega autenticación API si es necesario

### Ejemplo con nginx (HTTPS):

```nginx
server {
    listen 443 ssl;
    server_name registro.isrcomunicaciones.com;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🐛 Solución de Problemas

### Error: "Address already in use"

**Causa**: El puerto 8080 ya está en uso.

**Solución**:
```bash
# Ver qué proceso usa el puerto
sudo lsof -i :8080

# Cambiar a otro puerto
python3 registry_server.py --port 8081
```

### Error: "Permission denied"

**Causa**: No tienes permisos para abrir el puerto.

**Solución**:
```bash
# Ejecutar como root
sudo python3 registry_server.py
```

### No se puede acceder desde fuera

**Causa**: Firewall bloqueando el puerto.

**Solución**:
```bash
# Verificar firewall
sudo ufw status

# Abrir puerto
sudo ufw allow 8080/tcp
```

---

## 📈 Escalabilidad

Para alta disponibilidad:

1. **Base de datos**: Cambiar de JSON a Redis/PostgreSQL
2. **Load Balancer**: Usar nginx o HAProxy
3. **Múltiples instancias**: Ejecutar varias instancias del servidor
4. **CDN**: Usar Cloudflare para DDoS protection

---

## 🎉 ¡Listo!

El servidor central está funcionando en:
```
http://77.225.201.4:8080
```

Los clientes Windows ahora pueden:
1. Registrar sus códigos automáticamente
2. Conectar desde cualquier red usando códigos
3. Sin configurar port forwarding

---

## 📞 Soporte

¿Problemas? Abre un issue en GitHub:
https://github.com/FresyMetal/isr-remote-desktop/issues
