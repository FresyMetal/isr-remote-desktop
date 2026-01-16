# 📖 LÉEME PRIMERO - Guía Rápida

## 🚀 Inicio Rápido (Sin Compilar)

### Para USAR la aplicación directamente:

#### 1. Servidor (en el equipo a controlar)
```
Clic derecho en: IniciarServidor.bat
Seleccionar: "Ejecutar como administrador"
```

#### 2. Cliente (en tu equipo)
```
Doble clic en: IniciarCliente.bat
(NO como administrador)
```

#### 3. Conectar
```
- Ingresa la IP del servidor
- Haz clic en "Conectar"
- ¡Listo!
```

---

## 📦 Compilar a EXE (Opcional)

### Solo si quieres crear archivos .exe portables:

#### 1. Compilar Servidor
```
Doble clic en: build_server.bat
(NO como administrador)

Resultado: dist\RemoteDesktopServer.exe
```

#### 2. Compilar Cliente
```
Doble clic en: build_client.bat
(NO como administrador)

Resultado: dist\RemoteDesktopClient.exe
```

#### 3. Ejecutar los EXE
```
Servidor: Clic derecho → "Ejecutar como administrador"
Cliente: Doble clic normal
```

---

## 📁 Archivos Importantes

### Para USAR (sin compilar)
- `IniciarServidor.bat` ← Ejecutar como administrador
- `IniciarCliente.bat` ← Ejecutar normalmente

### Para COMPILAR (opcional)
- `build_server.bat` ← Ejecutar normalmente (NO como admin)
- `build_client.bat` ← Ejecutar normalmente (NO como admin)

### Para PROBAR
- `test_pynput.bat` ← Ejecutar como administrador

---

## ⚠️ IMPORTANTE

### Servidor
- ✅ **DEBE ejecutarse como administrador**
- ❌ Sin administrador, el ratón/teclado NO funcionarán

### Compilación
- ✅ **NO ejecutar como administrador**
- ❌ PyInstaller falla si se ejecuta como admin

### Cliente
- ✅ **NO necesita administrador**
- ✅ Ejecutar normalmente

---

## 🔧 Solución de Problemas

### Problema: "py no se reconoce"
**Solución**: Instala Python desde python.org

### Problema: El ratón/teclado no funcionan
**Solución**: Ejecuta el servidor como administrador

### Problema: Error al compilar
**Solución**: NO ejecutes build_*.bat como administrador

### Problema: "No such file or directory"
**Solución**: Asegúrate de estar en la carpeta correcta

---

## 📚 Documentación Completa

- `SOLUCION_DEFINITIVA_V1.5.md` - Guía completa de uso
- `NUEVAS_FUNCIONALIDADES_V1.4.md` - Modos de visualización
- `DEBUG_V1.3.md` - Guía de depuración
- `README.md` - Documentación técnica

---

## 🎯 Resumen

### Uso Normal (Recomendado)
1. Clic derecho en `IniciarServidor.bat` → "Ejecutar como administrador"
2. Doble clic en `IniciarCliente.bat`
3. Conectar y usar

### Compilar a EXE (Opcional)
1. Doble clic en `build_server.bat` (sin admin)
2. Doble clic en `build_client.bat` (sin admin)
3. Ejecutar los .exe de la carpeta `dist\`

---

**¿Dudas?** Consulta `SOLUCION_DEFINITIVA_V1.5.md`
