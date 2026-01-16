# Solución de Problemas de Conexión

## Problema: No puedo conectar entre equipos

### Diagnóstico Rápido

#### 1. Verificar que el Servidor está Activo

En el equipo **servidor** (el que quieres controlar):
- Abre ISR Remote Desktop
- Ve a la pestaña "Permitir Control"
- Haz clic en "▶️ Iniciar Servidor"
- Verifica que veas: **"🟢 Servidor activo"**
- Anota el **código de conexión** (ej: ISR-12345678)

#### 2. Verificar Conectividad de Red

**Opción A: Misma Red Local (LAN)**

En el equipo **cliente** (desde donde controlas):
```cmd
ping [IP_del_servidor]
```

Ejemplo:
```cmd
ping 192.168.1.100
```

**Debe responder**. Si no responde:
- ❌ Firewall bloqueando
- ❌ No están en la misma red
- ❌ IP incorrecta

**Opción B: Desde Internet**

Si estás conectando desde otra red:
- El servidor debe tener IP pública o port forwarding configurado
- O usar el servidor central de registro (77.225.201.4)

---

## Soluciones por Escenario

### Escenario 1: Misma Red Local (Más Común)

#### Problema: Firewall de Windows Bloqueando

**Solución**:

1. **En el equipo SERVIDOR**, abre PowerShell como administrador:

```powershell
# Permitir puerto 5900 (entrada)
New-NetFirewallRule -DisplayName "ISR Remote Desktop" -Direction Inbound -LocalPort 5900 -Protocol TCP -Action Allow

# Permitir puerto 5900 (salida)
New-NetFirewallRule -DisplayName "ISR Remote Desktop Out" -Direction Outbound -LocalPort 5900 -Protocol TCP -Action Allow
```

2. **Reinicia el servidor** en ISR Remote Desktop

3. **Intenta conectar** desde el cliente

#### Problema: Puerto Incorrecto

**Verificar**:
- Servidor usa puerto: **5900** (por defecto)
- Cliente conecta a: **IP:5900** o solo **IP** (usa 5900 automáticamente)

**Cambiar puerto** (si es necesario):
1. En servidor: Configuración → Puerto → Cambiar
2. En cliente: Conectar → Introducir `IP:PUERTO` (ej: `192.168.1.100:5901`)

---

### Escenario 2: Desde Internet (Diferentes Redes)

#### Opción A: Port Forwarding en Router

**Pasos**:

1. **Accede a tu router** (ej: 192.168.1.1)
2. **Busca** "Port Forwarding" o "NAT"
3. **Crea regla**:
   - Puerto externo: 5900
   - Puerto interno: 5900
   - IP interna: [IP del servidor]
   - Protocolo: TCP

4. **Obtén tu IP pública**:
```cmd
curl ifconfig.me
```

5. **Conecta** desde el cliente usando: `[IP_PUBLICA]:5900`

#### Opción B: Usar Servidor Central (Recomendado)

**Ventaja**: Sin configurar router

**Requisitos**:
- Servidor central activo en: 77.225.201.4:8080
- Ambos equipos con acceso a Internet

**Cómo funciona**:
1. Servidor se registra automáticamente con su código
2. Cliente resuelve el código a la IP pública
3. Conexión directa entre equipos

**Verificar servidor central**:
```cmd
curl http://77.225.201.4:8080
```

**Debe responder** con la interfaz web.

Si no responde:
- Servidor central no está activo
- Usa IP directa temporalmente

---

### Escenario 3: Código No Funciona

#### Problema: Servidor Central No Responde

**Diagnóstico**:
```cmd
curl http://77.225.201.4:8080/api/status
```

**Si no responde**:
1. Usa IP directa temporalmente
2. Contacta al administrador del servidor central

#### Problema: Código No Se Registra

**Verificar en el servidor**:
- Debe mostrar: **"✓ Servidor central: Conectado"**
- Si muestra: **"✗ Servidor central: No disponible"**
  - Servidor central está caído
  - Usa IP directa

---

## Pruebas de Conectividad

### Test 1: Ping

```cmd
ping [IP_del_servidor]
```

**Resultado esperado**: Respuestas

### Test 2: Telnet al Puerto

```cmd
telnet [IP_del_servidor] 5900
```

**Resultado esperado**: Conexión establecida

**Si falla**:
- Puerto bloqueado por firewall
- Servidor no está escuchando en ese puerto

### Test 3: Netstat (En el Servidor)

```cmd
netstat -an | findstr 5900
```

**Resultado esperado**:
```
TCP    0.0.0.0:5900           0.0.0.0:0              LISTENING
```

**Si no aparece**:
- Servidor no está activo
- Servidor usa otro puerto

---

## Comandos Útiles

### Ver Firewall (Windows)

```powershell
Get-NetFirewallRule -DisplayName "*ISR*"
```

### Desactivar Firewall Temporalmente (SOLO PARA PRUEBAS)

```powershell
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
```

**IMPORTANTE**: Vuelve a activarlo después:
```powershell
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
```

### Ver IP Local

```cmd
ipconfig
```

Busca "IPv4" en tu adaptador de red principal.

### Ver IP Pública

```cmd
curl ifconfig.me
```

---

## Checklist de Conexión

### En el Servidor:

- [ ] ISR Remote Desktop ejecutándose
- [ ] Pestaña "Permitir Control" activa
- [ ] Servidor iniciado (🟢 Servidor activo)
- [ ] Código de conexión visible
- [ ] Firewall permite puerto 5900
- [ ] Ejecutado como administrador

### En el Cliente:

- [ ] ISR Remote Desktop ejecutándose
- [ ] Pestaña "Controlar Equipo" activa
- [ ] Código o IP correcta
- [ ] Puerto correcto (5900 por defecto)
- [ ] Conexión a Internet (si usa servidor central)

### En la Red:

- [ ] Ambos equipos en la misma red (LAN) O
- [ ] Port forwarding configurado (Internet) O
- [ ] Servidor central activo (Internet)
- [ ] Firewall permite tráfico
- [ ] Router no bloquea puerto

---

## Solución Rápida (Misma Red)

**Si nada funciona y están en la misma red**:

1. **Desactiva temporalmente el firewall** en ambos equipos
2. **Usa IP directa** en lugar de código
3. **Si funciona**: El problema es el firewall
4. **Configura firewall** correctamente
5. **Reactiva firewall**

---

## Contacto Soporte

Si después de seguir esta guía no funciona:

1. **Anota**:
   - IP del servidor
   - Puerto usado
   - Mensaje de error exacto
   - Resultado de `ping` y `telnet`

2. **Reporta** en:
   - GitHub: https://github.com/FresyMetal/isr-remote-desktop/issues

---

## Logs de Depuración

Para obtener más información:

### En el Servidor:

Los logs se muestran en la pestaña "Permitir Control" → Sección de logs

### En el Cliente:

Los logs se muestran en la consola (si ejecutas desde Python) o en la interfaz

---

**Versión**: 3.0.1  
**Última actualización**: 16 de enero de 2026
