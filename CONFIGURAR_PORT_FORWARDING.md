# 🌐 Configurar Port Forwarding para Conexión desde Internet

Esta guía te ayudará a configurar tu router para permitir conexiones desde cualquier red (Internet) a tu equipo.

---

## 📋 ¿Qué es Port Forwarding?

**Port Forwarding** (reenvío de puertos) permite que conexiones desde Internet lleguen a tu equipo dentro de tu red local.

**Sin port forwarding**: Solo puedes conectar desde la misma red WiFi/LAN  
**Con port forwarding**: Puedes conectar desde cualquier lugar del mundo

---

## 🎯 Configuración Rápida

### Paso 1: Obtener tu IP Local

**En el equipo SERVIDOR**, abre cmd y ejecuta:

```cmd
ipconfig
```

**Busca**: `Dirección IPv4`  
**Ejemplo**: `192.168.1.100`

**Anótala**: _______________

---

### Paso 2: Acceder a tu Router

**Abre tu navegador** y ve a una de estas direcciones:

- `http://192.168.1.1`
- `http://192.168.0.1`
- `http://10.0.0.1`

**Usuario/Contraseña comunes**:
- admin / admin
- admin / password
- admin / 1234
- (Mira la etiqueta en tu router)

---

### Paso 3: Configurar Port Forwarding

**Busca** una sección llamada:
- "Port Forwarding"
- "Reenvío de Puertos"
- "Virtual Server"
- "NAT"
- "Aplicaciones y Juegos"

**Crea una nueva regla** con estos datos:

| Campo | Valor |
|-------|-------|
| **Nombre** | ISR Remote Desktop |
| **Puerto Externo** | 5900 |
| **Puerto Interno** | 5900 |
| **IP Interna** | [Tu IP local del Paso 1] |
| **Protocolo** | TCP |
| **Estado** | Habilitado |

**Guarda** y **reinicia** el router si es necesario.

---

### Paso 4: Verificar tu IP Pública

**En el equipo SERVIDOR**, abre cmd y ejecuta:

```cmd
curl ifconfig.me
```

O visita: https://www.whatismyip.com/

**Anótala**: _______________

---

### Paso 5: Probar la Conexión

#### Desde el Servidor:

1. Abre **ISR Remote Desktop**
2. Pestaña "Permitir Control"
3. Clic "▶️ Iniciar Servidor"
4. **Anota el código** (ej: ISR-12345678)

#### Desde el Cliente (otro equipo, otra red):

1. Abre **ISR Remote Desktop**
2. Pestaña "Controlar Equipo"
3. **Introduce el código** ISR-12345678
4. Clic "Conectar"

**¡Listo!** El sistema resolverá el código automáticamente usando el servidor central.

---

## 🔧 Configuración por Marca de Router

### TP-Link

1. Ve a **Advanced** → **NAT Forwarding** → **Virtual Servers**
2. Clic **Add**
3. Completa los datos y guarda

### Netgear

1. Ve a **Advanced** → **Advanced Setup** → **Port Forwarding/Port Triggering**
2. Selecciona **Port Forwarding**
3. Clic **Add Custom Service**
4. Completa los datos y guarda

### D-Link

1. Ve a **Advanced** → **Port Forwarding**
2. Clic **Add**
3. Completa los datos y guarda

### Asus

1. Ve a **WAN** → **Virtual Server / Port Forwarding**
2. Clic **Add**
3. Completa los datos y guarda

### Linksys

1. Ve a **Applications & Gaming** → **Single Port Forwarding**
2. Completa los datos y guarda

---

## 🛡️ Configurar IP Estática (Recomendado)

Para que el port forwarding siempre funcione, tu equipo debe tener la misma IP local.

### Opción A: Reserva DHCP en el Router

1. Busca **DHCP Reservation** o **Address Reservation**
2. Encuentra tu equipo en la lista
3. Reserva su IP actual
4. Guarda

### Opción B: IP Estática en Windows

1. Abre **Panel de Control** → **Centro de redes**
2. Clic en tu conexión → **Propiedades**
3. Selecciona **Protocolo de Internet versión 4 (TCP/IPv4)**
4. Clic **Propiedades**
5. Selecciona **Usar la siguiente dirección IP**:
   - **IP**: [Tu IP local actual]
   - **Máscara**: 255.255.255.0
   - **Puerta de enlace**: [IP de tu router]
   - **DNS preferido**: 8.8.8.8
   - **DNS alternativo**: 8.8.4.4
6. Clic **Aceptar**

---

## 🧪 Verificar que Funciona

### Desde Otro Equipo en Internet:

```cmd
telnet [TU_IP_PUBLICA] 5900
```

O usa una herramienta online:
- https://www.yougetsignal.com/tools/open-ports/
- Introduce tu IP pública y puerto 5900

**Resultado esperado**: "Puerto abierto" o "Conectado"

---

## ❓ Problemas Comunes

### "No puedo acceder al router"

**Solución**: 
- Verifica que estés conectado a la red WiFi del router
- Prueba con todas las IPs comunes (192.168.1.1, 192.168.0.1, etc.)
- Busca la IP del router con: `ipconfig` → "Puerta de enlace predeterminada"

### "El puerto sigue cerrado"

**Soluciones**:
1. **Verifica el firewall de Windows**:
   ```powershell
   New-NetFirewallRule -DisplayName "ISR Remote Desktop" -Direction Inbound -LocalPort 5900 -Protocol TCP -Action Allow
   ```

2. **Verifica que el servidor esté activo**:
   ```cmd
   netstat -an | findstr 5900
   ```

3. **Reinicia el router** después de configurar

4. **Verifica que la IP interna sea correcta** en la regla de port forwarding

### "Mi IP pública cambia constantemente"

**Solución**: Usa un servicio de **DNS Dinámico** (DDNS):
- No-IP (gratuito)
- DynDNS
- Duck DNS

Muchos routers tienen soporte integrado para DDNS.

---

## 🔐 Seguridad

### ⚠️ Importante

Al abrir un puerto a Internet, tu equipo es accesible desde cualquier lugar. **Recomendaciones**:

1. **Usa contraseña fuerte** en ISR Remote Desktop
2. **Cambia el puerto** de 5900 a otro (ej: 15900) para evitar escaneos automáticos
3. **Actualiza Windows** regularmente
4. **Usa firewall** activo
5. **Cierra el servidor** cuando no lo uses

### Cambiar Puerto

**En ISR Remote Desktop**:
1. Clic **⚙️ Configuración**
2. Cambia **Puerto** de 5900 a otro (ej: 15900)
3. Guarda

**En el router**:
- Cambia el **Puerto Externo** al mismo número

---

## 📊 Resumen Visual

```
Internet
   ↓
Tu Router (IP Pública: 203.0.113.45)
   ↓ [Port Forwarding: 5900 → 192.168.1.100:5900]
   ↓
Tu PC (IP Local: 192.168.1.100)
   ↓
ISR Remote Desktop Server (Puerto 5900)
```

---

## ✅ Checklist Final

- [ ] Obtenida IP local del servidor
- [ ] Accedido al router
- [ ] Creada regla de port forwarding
- [ ] Configurada IP estática o reserva DHCP
- [ ] Verificada IP pública
- [ ] Firewall de Windows configurado
- [ ] Servidor ISR iniciado
- [ ] Puerto verificado con herramienta online
- [ ] Probada conexión desde otro equipo/red

---

## 🆘 ¿Necesitas Ayuda?

Si después de seguir esta guía aún no funciona:

1. **Verifica** que tu ISP no bloquee puertos (algunos ISPs bloquean puertos comunes)
2. **Contacta** a tu proveedor de Internet para confirmar
3. **Considera** usar una VPN o servicio de túnel (ngrok, ZeroTier, etc.)

---

**Versión**: 3.0.3  
**Fecha**: 16 de enero de 2026
