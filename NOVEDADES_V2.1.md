# Novedades Versión 2.1 - Sistema de Códigos y Historial

## 🎉 Nuevas Funcionalidades

### 1. ✅ Sistema de Códigos de Conexión (tipo AnyDesk)

**¡Ya no necesitas recordar IPs!** Ahora puedes usar códigos simples para conectarte.

#### Características:

**En el Servidor**:
- Al iniciar, se genera un código único automáticamente
- Formato: `ISR-12345678`
- También puedes usar un código personalizado

**En el Cliente**:
- Conecta usando el código en lugar de la IP
- También puedes seguir usando IPs directamente
- Resolución automática de códigos a IPs

#### Ejemplo de Uso:

**Servidor**:
```
========================================
  SERVIDOR DE ESCRITORIO REMOTO
========================================
Código de conexión: ISR-87654321
IP local: 192.168.1.100:5900
Monitor: 1
========================================

Para conectar desde el cliente:
  - Usa el código: ISR-87654321
  - O usa la IP: 192.168.1.100:5900
```

**Cliente**:
```
🔑 Código o IP: ISR-87654321
🔌 Puerto: 5900
🔒 Contraseña: (opcional)
```

---

### 2. ✅ Historial de Conexiones Recientes

**Reconecta rápidamente** a tus servidores favoritos.

#### Características:

**Botones de Acceso Rápido**:
- Muestra las últimas 5 conexiones
- Un clic para reconectar
- Iconos con nombres descriptivos

**Persistencia**:
- El historial se guarda automáticamente
- Persiste entre sesiones
- Máximo 10 conexiones guardadas

**Gestión Automática**:
- Elimina duplicados
- Las más recientes primero
- Límite de 10 conexiones

#### Interfaz del Diálogo:

```
┌─────────────────────────────────────────┐
│  Conexiones Recientes:                  │
│  [🔗 ISR-12345678] [🔗 192.168.1.50]   │
│  [🔗 ISR-87654321] [🔗 Servidor-Casa]  │
├─────────────────────────────────────────┤
│  🔑 Código o IP: ___________________   │
│  🔌 Puerto: 5900                        │
│  🔒 Contraseña: ___________________    │
│                                          │
│  Puedes usar el código de conexión     │
│  (ej: ISR-12345678) o la IP directa.   │
│                                          │
│  [Aceptar] [Cancelar]                   │
└─────────────────────────────────────────┘
```

---

### 3. ✅ Icono Personalizado

**Logo de ISR Comunicaciones** en:
- Ventana de la aplicación
- Bandeja del sistema
- Ejecutables compilados (.exe)

---

## 🎯 Casos de Uso

### Caso 1: Conexión Rápida con Código

**Escenario**: Quieres conectarte a un servidor remoto sin recordar la IP.

```
Servidor:
1. Inicia el servidor
2. Anota el código: ISR-12345678
3. Comparte el código con el cliente

Cliente:
1. Abre el cliente
2. Nueva Conexión
3. Escribe: ISR-12345678
4. Conectar
```

---

### Caso 2: Reconexión Rápida

**Escenario**: Te conectas frecuentemente a los mismos servidores.

```
Cliente:
1. Abre el cliente
2. Nueva Conexión
3. Clic en el botón de conexión reciente
4. ¡Conectado!
```

---

### Caso 3: Código Personalizado

**Escenario**: Quieres un código fácil de recordar.

```
Servidor:
py server.py --code Servidor-Casa

Código de conexión: Servidor-Casa
```

---

## 🔧 Detalles Técnicos

### Sistema de Códigos

**Generación de Códigos**:
```python
# Código automático basado en ID de máquina
ISR-12345678

# Código personalizado
py server.py --code MiServidor
```

**Resolución de Códigos**:
```python
# En el cliente
code_manager.resolve_code("ISR-12345678")
# Devuelve: ("192.168.1.100", 5900)
```

**Registro de Códigos**:
- Archivo: `connection_registry.json`
- Formato JSON
- Mapea códigos a IPs y puertos

---

### Historial de Conexiones

**Almacenamiento**:
- Archivo: `connection_history.json`
- Formato JSON
- Máximo 10 entradas

**Estructura**:
```json
[
  {
    "name": "ISR-12345678",
    "host": "192.168.1.100",
    "port": 5900
  },
  {
    "name": "Servidor-Casa",
    "host": "192.168.1.50",
    "port": 5900
  }
]
```

---

## 📊 Comparación de Versiones

| Característica | v2.0 | v2.1 |
|----------------|------|------|
| Conexión por IP | ✅ | ✅ |
| Códigos de conexión | ❌ | ✅ |
| Historial | ❌ | ✅ |
| Reconexión rápida | ❌ | ✅ |
| Icono personalizado | ❌ | ✅ |
| Logo ISR | ❌ | ✅ |

---

## 🚀 Cómo Usar

### Servidor

#### Código Automático:
```cmd
py server.py
```

#### Código Personalizado:
```cmd
py server.py --code MiServidor
```

#### Con Opciones:
```cmd
py server.py --code Oficina --port 5901 --monitor 2
```

---

### Cliente

#### Conectar con Código:
```
1. Nueva Conexión
2. Código o IP: ISR-12345678
3. Puerto: 5900
4. Conectar
```

#### Conectar con IP (como antes):
```
1. Nueva Conexión
2. Código o IP: 192.168.1.100
3. Puerto: 5900
4. Conectar
```

#### Reconectar Rápidamente:
```
1. Nueva Conexión
2. Clic en botón de conexión reciente
3. ¡Conectado!
```

---

## 💡 Ventajas del Sistema de Códigos

### Vs. IP Directa:

| Aspecto | IP Directa | Código |
|---------|-----------|--------|
| Fácil de recordar | ❌ | ✅ |
| Funciona en NAT | ❌ | ✅* |
| Cambio de IP | ❌ Hay que actualizar | ✅ Automático* |
| Compartir | ❌ Complejo | ✅ Simple |

*Requiere servidor de registro central (próxima versión)

---

## 🔮 Próximas Mejoras

### Servidor de Registro Central (v2.2)

**Funcionalidad**:
- Servidor central en la nube
- Actualización automática de IPs
- Conexión desde cualquier red
- Sin configuración de router

**Uso**:
```
Servidor:
py server.py --register-online

Cliente:
Código: ISR-12345678
(Funciona desde cualquier red)
```

---

## 📝 Notas Importantes

### Registro de Códigos

**Local**:
- Los códigos se registran localmente
- Archivo: `connection_registry.json`
- Solo funciona en la misma red local

**Para Conexión desde Internet**:
- Configura port forwarding en tu router
- O usa VPN (Tailscale, WireGuard)
- O espera la v2.2 con servidor central

---

### Compatibilidad

**Servidor v2.1 + Cliente v2.0**:
- ✅ Funciona (usando IP)
- ❌ No funciona (usando código)

**Servidor v2.0 + Cliente v2.1**:
- ✅ Funciona (usando IP)
- ❌ No funciona (usando código)

**Recomendación**: Actualiza servidor y cliente a v2.1

---

## 🎉 Resumen

### Lo Nuevo en v2.1:

1. **Códigos de conexión** → Fácil de recordar y compartir
2. **Historial de conexiones** → Reconexión rápida
3. **Icono personalizado** → Logo de ISR

### Beneficios:

- ✅ Más fácil de usar
- ✅ Más rápido para reconectar
- ✅ Más profesional
- ✅ Preparado para servidor central

---

**Versión**: 2.1  
**Fecha**: 15 de enero de 2026  
**Estado**: ✅ Sistema de códigos y historial implementado
