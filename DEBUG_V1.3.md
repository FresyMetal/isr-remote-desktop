# Guía de Depuración - Versión 1.3

## 🔍 Cambios en la Versión 1.3

Esta versión incluye **logs de depuración** para diagnosticar problemas con clics y teclado.

### Cambios Principales

1. **Escalado Proporcional**: La pantalla ahora se escala para verse completa en la ventana
2. **Logs de Depuración**: Mensajes detallados en servidor y cliente
3. **Foco Automático**: El label obtiene foco al hacer clic para que funcione el teclado
4. **Coordenadas Escaladas**: Las coordenadas se escalan correctamente del tamaño del label al tamaño real

---

## 📊 Logs de Depuración

### En el Cliente

Cuando hagas clic, verás en la consola:
```
[Cliente] Clic en (400, 300) -> remoto (960, 540), buttons=001
[Cliente] Release en (400, 300) -> remoto (960, 540), buttons=000
```

**Significado**:
- `(400, 300)`: Coordenadas en el label (ventana del cliente)
- `(960, 540)`: Coordenadas escaladas al tamaño real de la pantalla remota
- `buttons=001`: Estado de los botones (bit 0 = izquierdo, bit 1 = derecho, bit 2 = medio)

Cuando escribas, verás:
```
[Cliente] Tecla presionada: 65
[Cliente] Tecla liberada: 65
```

**Significado**:
- `65`: Código de la tecla Qt (65 = 'A')

---

### En el Servidor

Cuando el servidor reciba eventos del ratón, verás:
```
[Servidor] Mouse: pos=(960,540), buttons=001, changed=001
[Servidor] Presionando botón izquierdo en (960, 540)
[Servidor] Mouse: pos=(960,540), buttons=000, changed=001
[Servidor] Soltando botón izquierdo
```

**Significado**:
- `pos=(960,540)`: Posición del ratón recibida
- `buttons=001`: Estado actual de los botones (binario)
- `changed=001`: Qué botones cambiaron de estado

Cuando el servidor reciba eventos del teclado, verás:
```
[Servidor] Presionando tecla: 65 -> 'a'
[Servidor] Soltando tecla: 65 -> 'a'
```

**Significado**:
- `65`: Código de tecla Qt recibido
- `'a'`: Tecla mapeada a pynput

---

## 🐛 Diagnóstico de Problemas

### Problema: No Puedo Hacer Clic

**Pasos de diagnóstico**:

1. **Verifica el cliente**: Haz clic en la ventana del cliente y mira la consola
   
   **¿Ves esto?**
   ```
   [Cliente] Clic en (X, Y) -> remoto (X2, Y2), buttons=001
   ```
   - ✅ **SÍ**: El cliente está enviando el evento correctamente
   - ❌ **NO**: El evento no se está capturando. Asegúrate de hacer clic dentro de la imagen.

2. **Verifica el servidor**: Mira la consola del servidor
   
   **¿Ves esto?**
   ```
   [Servidor] Mouse: pos=(X,Y), buttons=001, changed=001
   [Servidor] Presionando botón izquierdo en (X, Y)
   ```
   - ✅ **SÍ**: El servidor está recibiendo y procesando el evento
   - ❌ **NO**: El evento no está llegando al servidor. Verifica la conexión.

3. **Verifica que el clic se ejecuta**: Mira si el cursor se mueve y hace clic en el servidor
   
   - ✅ **SÍ**: Todo funciona correctamente
   - ❌ **NO**: Puede haber un problema de permisos. Ejecuta el servidor como administrador.

---

### Problema: No Puedo Escribir

**Pasos de diagnóstico**:

1. **Verifica que el label tiene foco**: Haz clic en la ventana del cliente primero
   
   - El label debe obtener foco automáticamente al hacer clic

2. **Verifica el cliente**: Escribe algo y mira la consola del cliente
   
   **¿Ves esto?**
   ```
   [Cliente] Tecla presionada: 65
   [Cliente] Tecla liberada: 65
   ```
   - ✅ **SÍ**: El cliente está capturando las teclas
   - ❌ **NO**: El label no tiene foco. Haz clic en la imagen primero.

3. **Verifica el servidor**: Mira la consola del servidor
   
   **¿Ves esto?**
   ```
   [Servidor] Presionando tecla: 65 -> 'a'
   [Servidor] Soltando tecla: 65 -> 'a'
   ```
   - ✅ **SÍ**: El servidor está recibiendo y procesando las teclas
   - ❌ **NO**: El evento no está llegando. Verifica la conexión.

4. **Verifica que las teclas se escriben**: Mira si aparece texto en el servidor
   
   - ✅ **SÍ**: Todo funciona correctamente
   - ❌ **NO**: Puede haber un problema de permisos o mapeo de teclas.

---

### Problema: La Pantalla No Se Ve Completa

**Solución**:
- La pantalla ahora se escala automáticamente para verse completa
- Maximiza la ventana del cliente para ver más grande
- El escalado es proporcional, manteniendo la relación de aspecto

---

### Problema: El Ratón No Apunta Bien

**Diagnóstico**:

1. Haz clic en un punto conocido (ej: esquina superior izquierda)
2. Mira los logs del cliente:
   ```
   [Cliente] Clic en (10, 10) -> remoto (24, 18), buttons=001
   ```
3. Verifica que las coordenadas remotas sean correctas para tu resolución

**Si las coordenadas están mal**:
- Verifica que `original_width` y `original_height` sean correctos
- Estos valores se actualizan automáticamente al recibir el primer frame

---

## 🔧 Soluciones Comunes

### Los Clics No Funcionan

**Solución 1**: Ejecutar servidor como administrador
```cmd
# Windows: Clic derecho -> Ejecutar como administrador
python server.py
```

**Solución 2**: Verificar permisos de pynput
```bash
pip install --upgrade pynput
```

**Solución 3**: Desactivar UAC temporalmente (Windows)
- Solo para pruebas, no recomendado permanentemente

---

### El Teclado No Funciona

**Solución 1**: Hacer clic en la imagen primero
- El label necesita tener foco para capturar teclas
- Al hacer clic, el foco se asigna automáticamente

**Solución 2**: Verificar que la ventana del cliente esté activa
- La ventana debe estar en primer plano

**Solución 3**: Ejecutar servidor como administrador
```cmd
python server.py
```

---

### La Pantalla Está Distorsionada

**Causa**: El escalado no mantiene la relación de aspecto

**Solución**: Redimensiona la ventana del cliente manualmente
- El label mantiene la relación de aspecto automáticamente

---

## 📝 Información Útil para Reportar Problemas

Si sigues teniendo problemas, proporciona esta información:

### Del Cliente
```
[Cliente] Clic en (X, Y) -> remoto (X2, Y2), buttons=XXX
[Cliente] Tecla presionada: XXX
```

### Del Servidor
```
[Servidor] Mouse: pos=(X,Y), buttons=XXX, changed=XXX
[Servidor] Presionando botón izquierdo en (X, Y)
[Servidor] Presionando tecla: XXX -> 'X'
```

### Información del Sistema
- Sistema operativo (Windows 10/11)
- Resolución de pantalla del servidor
- Tamaño de ventana del cliente
- ¿Ejecutando como administrador?

---

## ✅ Checklist de Verificación

Antes de reportar un problema:

- [ ] Estoy usando la versión 1.3
- [ ] He reiniciado servidor y cliente
- [ ] He hecho clic en la imagen para dar foco
- [ ] He mirado los logs en ambas consolas
- [ ] He ejecutado el servidor como administrador
- [ ] La ventana del cliente está activa (en primer plano)

---

## 🎯 Pruebas Paso a Paso

### Prueba 1: Clic Izquierdo

1. Inicia servidor y cliente
2. Conecta
3. Haz clic en la imagen
4. **Verifica logs del cliente**: ¿Ves el mensaje de clic?
5. **Verifica logs del servidor**: ¿Ves el mensaje de presionar/soltar?
6. **Verifica visualmente**: ¿Se ejecutó el clic en el servidor?

### Prueba 2: Teclado

1. Haz clic en un editor de texto en el servidor (ej: Notepad)
2. Haz clic en la imagen del cliente para dar foco
3. Escribe "hola"
4. **Verifica logs del cliente**: ¿Ves los códigos de teclas?
5. **Verifica logs del servidor**: ¿Ves las teclas mapeadas?
6. **Verifica visualmente**: ¿Apareció "hola" en el servidor?

### Prueba 3: Escalado

1. Redimensiona la ventana del cliente
2. Mueve el ratón sobre la imagen
3. **Verifica**: ¿El cursor remoto sigue al cursor local?
4. Haz clic en diferentes puntos
5. **Verifica**: ¿Los clics se ejecutan en el lugar correcto?

---

## 🔬 Logs Detallados

### Activar Logs Adicionales

Si necesitas más información, puedes agregar logs adicionales:

**En `client.py`**, en `send_mouse_event()`:
```python
print(f"[Cliente] Enviando mouse: x={x}, y={y}, buttons={buttons}")
```

**En `server.py`**, en `_process_message()`:
```python
print(f"[Servidor] Mensaje recibido: tipo={msg_type}, payload_len={len(payload)}")
```

---

## 📞 Soporte

Si después de seguir esta guía sigues teniendo problemas:

1. **Copia los logs** de cliente y servidor
2. **Describe el problema** paso a paso
3. **Indica qué has probado** de esta guía
4. **Proporciona información del sistema**

---

**Versión**: 1.3  
**Fecha**: 15 de enero de 2026  
**Estado**: Con logs de depuración
