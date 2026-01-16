# Guía de Contribución

¡Gracias por tu interés en contribuir a ISR Remote Desktop!

## Cómo Contribuir

### Reportar Bugs

Si encuentras un bug, por favor abre un issue con:

- Descripción clara del problema
- Pasos para reproducirlo
- Comportamiento esperado vs. actual
- Versión de la aplicación
- Sistema operativo y versión de Python

### Sugerir Funcionalidades

Para sugerir nuevas funcionalidades:

1. Abre un issue con la etiqueta "enhancement"
2. Describe la funcionalidad detalladamente
3. Explica por qué sería útil
4. Si es posible, propón una implementación

### Pull Requests

1. Fork el repositorio
2. Crea una rama para tu feature:
   ```bash
   git checkout -b feature/mi-nueva-funcionalidad
   ```
3. Haz tus cambios
4. Asegúrate de que el código funciona
5. Commit con mensajes descriptivos:
   ```bash
   git commit -m "Agrega funcionalidad X que hace Y"
   ```
6. Push a tu fork:
   ```bash
   git push origin feature/mi-nueva-funcionalidad
   ```
7. Abre un Pull Request

### Estilo de Código

- Sigue PEP 8 para código Python
- Usa nombres descriptivos para variables y funciones
- Comenta código complejo
- Mantén las funciones pequeñas y enfocadas

### Testing

Antes de enviar un PR:

- Prueba tu código en Windows
- Verifica que no rompe funcionalidades existentes
- Prueba con múltiples monitores si aplica

## Estructura del Proyecto

```
isr-remote-desktop/
├── server.py           # Servidor principal
├── client.py           # Cliente con GUI
├── protocol.py         # Protocolo de red
├── connection_code.py  # Sistema de códigos
├── file_transfer.py    # Transferencia de archivos
├── security.py         # Seguridad y cifrado
└── docs/              # Documentación
```

## Áreas que Necesitan Ayuda

- [ ] Soporte para Linux y macOS
- [ ] Tests automatizados
- [ ] Optimización de rendimiento
- [ ] Traducción a otros idiomas
- [ ] Documentación adicional

## Código de Conducta

- Sé respetuoso con otros contribuidores
- Acepta críticas constructivas
- Enfócate en lo mejor para el proyecto
- Ayuda a crear un ambiente acogedor

## Preguntas

Si tienes preguntas, abre un issue o contacta a:
- Email: soporte@isrcomunicaciones.com

¡Gracias por contribuir!
