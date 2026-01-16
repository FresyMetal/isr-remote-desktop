"""
Servidor de escritorio remoto
Captura la pantalla y procesa eventos de entrada
"""

import socket
import threading
import time
import io
from typing import Optional, Dict, Tuple
import mss
import mss.tools
from PIL import Image
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key
import pyperclip

from protocol import (
    Protocol, MessageType,
    decode_handshake, encode_auth_response,
    decode_mouse_event, decode_keyboard_event,
    encode_video_frame, encode_clipboard_text,
    decode_clipboard_text, decode_file_metadata,
    encode_file_chunk, decode_file_chunk
)

# Ocultar ventana de consola en Windows
import sys
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


class RemoteDesktopServer:
    """Servidor de escritorio remoto"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 5900, password: str = '', monitor_index: int = 1):
        """
        Inicializa el servidor
        
        Args:
            host: Dirección IP para escuchar
            port: Puerto para escuchar
            password: Contraseña para autenticación (vacío = sin auth)
            monitor_index: Índice del monitor a capturar (1 = principal, 2 = segundo, etc.)
        """
        self.host = host
        self.port = port
        self.password = password
        self.monitor_index = monitor_index
        
        self.server_socket: Optional[socket.socket] = None
        self.clients: Dict[socket.socket, threading.Thread] = {}
        self.running = False
        
        # Controladores de entrada
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        
        # Captura de pantalla (se inicializará en cada thread)
        self.monitor = None
        self.available_monitors = []
        self._init_monitor()
        
        # Protocolo
        self.protocol = Protocol(compression_level=3)
        
        # Portapapeles
        self.last_clipboard = ""
        self.clipboard_lock = threading.Lock()
        
        # Transferencia de archivos
        self.file_transfers: Dict[int, Dict] = {}
        self.file_id_counter = 0
        
        print(f"[Servidor] Inicializado en {host}:{port}")
        print(f"[Servidor] Resolución del monitor: {self.monitor['width']}x{self.monitor['height']}")
    
    def start(self):
        """Inicia el servidor"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        self.running = True
        print(f"[Servidor] Escuchando en {self.host}:{self.port}")
        
        # Iniciar thread de monitoreo de portapapeles
        clipboard_thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
        clipboard_thread.start()
        
        # Aceptar conexiones
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"[Servidor] Nueva conexión desde {address}")
                
                # Crear thread para manejar el cliente
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                self.clients[client_socket] = client_thread
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"[Servidor] Error al aceptar conexión: {e}")
    
    def stop(self):
        """Detiene el servidor"""
        print("[Servidor] Deteniendo...")
        self.running = False
        
        # Cerrar todas las conexiones de clientes
        for client_socket in list(self.clients.keys()):
            try:
                client_socket.close()
            except:
                pass
        
        # Cerrar socket del servidor (shutdown primero para desbloquear accept())
        if self.server_socket:
            try:
                self.server_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                self.server_socket.close()
            except:
                pass
        
        print("[Servidor] Detenido")
    
    def _handle_client(self, client_socket: socket.socket, address: Tuple[str, int]):
        """
        Maneja la comunicación con un cliente
        
        Args:
            client_socket: Socket del cliente
            address: Dirección del cliente
        """
        try:
            # Handshake
            if not self._do_handshake(client_socket):
                print(f"[Servidor] Handshake fallido con {address}")
                client_socket.close()
                return
            
            print(f"[Servidor] Cliente {address} autenticado")
            
            # Iniciar captura de pantalla para este cliente
            capture_thread = threading.Thread(
                target=self._capture_screen,
                args=(client_socket,),
                daemon=True
            )
            capture_thread.start()
            
            # Procesar mensajes del cliente
            while self.running:
                # Leer header
                header_bytes = self._recv_exact(client_socket, Protocol.HEADER_SIZE)
                if not header_bytes:
                    break
                
                # Decodificar header
                header = self.protocol.decode_header(header_bytes)
                if not header:
                    print(f"[Servidor] Header inválido de {address}")
                    break
                
                magic, msg_type, flags, payload_len, seq_num = header
                
                # Leer payload
                payload = self._recv_exact(client_socket, payload_len)
                if not payload:
                    break
                
                # Decodificar payload
                try:
                    payload = self.protocol.decode_payload(payload, flags)
                except Exception as e:
                    print(f"[Servidor] Error al decodificar payload: {e}")
                    continue
                
                # Procesar mensaje
                self._process_message(client_socket, msg_type, payload)
            
        except Exception as e:
            print(f"[Servidor] Error con cliente {address}: {e}")
        finally:
            print(f"[Servidor] Cliente {address} desconectado")
            client_socket.close()
            if client_socket in self.clients:
                del self.clients[client_socket]
    
    def _do_handshake(self, client_socket: socket.socket) -> bool:
        """
        Realiza el handshake con el cliente
        
        Returns:
            True si el handshake fue exitoso
        """
        try:
            # Recibir handshake del cliente
            header_bytes = self._recv_exact(client_socket, Protocol.HEADER_SIZE)
            if not header_bytes:
                return False
            
            header = self.protocol.decode_header(header_bytes)
            if not header or header[1] != MessageType.HANDSHAKE:
                return False
            
            payload_len = header[3]
            payload = self._recv_exact(client_socket, payload_len)
            if not payload:
                return False
            
            version, capabilities = decode_handshake(payload)
            print(f"[Servidor] Cliente versión {version}, capacidades: {capabilities}")
            
            # Enviar respuesta de autenticación
            if self.password:
                # TODO: Implementar autenticación real
                # Por ahora, siempre aceptar
                pass
            
            response = encode_auth_response(True, "Conexión aceptada")
            message = self.protocol.encode_message(MessageType.AUTH_RESPONSE, response)
            client_socket.sendall(message)
            
            return True
            
        except Exception as e:
            print(f"[Servidor] Error en handshake: {e}")
            return False
    
    def _recv_exact(self, sock: socket.socket, n: int) -> Optional[bytes]:
        """
        Recibe exactamente n bytes del socket
        
        Args:
            sock: Socket
            n: Número de bytes a recibir
            
        Returns:
            Bytes recibidos o None si se cerró la conexión
        """
        data = b''
        while len(data) < n:
            chunk = sock.recv(n - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def _process_message(self, client_socket: socket.socket, msg_type: int, payload: bytes):
        """
        Procesa un mensaje del cliente
        
        Args:
            client_socket: Socket del cliente
            msg_type: Tipo de mensaje
            payload: Datos del mensaje
        """
        try:
            if msg_type == MessageType.INPUT_MOUSE:
                x, y, buttons = decode_mouse_event(payload)
                self._handle_mouse_event(x, y, buttons)
            
            elif msg_type == MessageType.INPUT_KEYBOARD:
                key_code, pressed = decode_keyboard_event(payload)
                self._handle_keyboard_event(key_code, pressed)
            
            elif msg_type == MessageType.CLIPBOARD_TEXT:
                text = decode_clipboard_text(payload)
                self._handle_clipboard_update(text)
            
            elif msg_type == MessageType.FILE_METADATA:
                file_id, filesize, filename = decode_file_metadata(payload)
                self._handle_file_metadata(client_socket, file_id, filesize, filename)
            
            elif msg_type == MessageType.FILE_CHUNK:
                file_id, chunk_num, data = decode_file_chunk(payload)
                self._handle_file_chunk(file_id, chunk_num, data)
            
            elif msg_type == MessageType.PING:
                # Responder con PONG
                pong = self.protocol.encode_message(MessageType.PONG, b'')
                client_socket.sendall(pong)
            
            elif msg_type == MessageType.VIDEO_REQUEST:
                # El cliente solicita cambio de monitor
                if len(payload) >= 4:
                    direction = int.from_bytes(payload[:4], byteorder='big', signed=True)
                    self._change_monitor(direction)
                else:
                    # Solicitud de frame (ignorar, la captura es continua)
                    pass
            
        except Exception as e:
            print(f"[Servidor] Error al procesar mensaje tipo {msg_type}: {e}")
    
    def _handle_mouse_event(self, x: int, y: int, buttons: int):
        """Maneja un evento de ratón"""
        # Las coordenadas (x, y) son relativas al monitor actual
        # Necesitamos convertirlas a coordenadas absolutas de pantalla
        # sumando el offset del monitor
        absolute_x = self.monitor['left'] + x
        absolute_y = self.monitor['top'] + y
        
        # Log detallado para depuración
        print(f"[Servidor] Evento ratón:")
        print(f"  Monitor actual: {self.monitor_index}")
        print(f"  Offset del monitor: ({self.monitor['left']}, {self.monitor['top']})")
        print(f"  Resolución del monitor: {self.monitor['width']}x{self.monitor['height']}")
        print(f"  Coordenadas recibidas (relativas): ({x}, {y})")
        print(f"  Coordenadas calculadas (absolutas): ({absolute_x}, {absolute_y})")
        
        # Mover ratón a coordenadas absolutas
        self.mouse.position = (absolute_x, absolute_y)
        print(f"  Posición real del ratón después de mover: {self.mouse.position}")
        
        # Procesar botones
        # Bit 0: botón izquierdo
        # Bit 1: botón derecho
        # Bit 2: botón medio
        
        # Obtener estado anterior si existe
        if not hasattr(self, '_last_mouse_buttons'):
            self._last_mouse_buttons = 0
        
        # Detectar cambios en los botones
        changed = buttons ^ self._last_mouse_buttons
        
        # Log para depuración
        if changed != 0:
            print(f"[Servidor] Mouse: relativa=({x},{y}), absoluta=({absolute_x},{absolute_y}), buttons={buttons:03b}, changed={changed:03b}")
        
        # Botón izquierdo
        if changed & 0x01:
            if buttons & 0x01:
                print(f"[Servidor] Presionando botón izquierdo en relativa=({x}, {y}), absoluta=({absolute_x}, {absolute_y})")
                self.mouse.press(Button.left)
            else:
                print(f"[Servidor] Soltando botón izquierdo")
                self.mouse.release(Button.left)
        
        # Botón derecho
        if changed & 0x02:
            if buttons & 0x02:
                print(f"[Servidor] Presionando botón derecho en relativa=({x}, {y}), absoluta=({absolute_x}, {absolute_y})")
                self.mouse.press(Button.right)
            else:
                print(f"[Servidor] Soltando botón derecho")
                self.mouse.release(Button.right)
        
        # Botón medio
        if changed & 0x04:
            if buttons & 0x04:
                print(f"[Servidor] Presionando botón medio en relativa=({x}, {y}), absoluta=({absolute_x}, {absolute_y})")
                self.mouse.press(Button.middle)
            else:
                print(f"[Servidor] Soltando botón medio")
                self.mouse.release(Button.middle)
        
        self._last_mouse_buttons = buttons
    
    def _handle_keyboard_event(self, key_code: int, pressed: bool):
        """Maneja un evento de teclado"""
        try:
            # Mapeo de teclas especiales de Qt a pynput
            from pynput.keyboard import Key, KeyCode
            
            # Diccionario de mapeo para teclas especiales
            special_keys = {
                16777219: Key.backspace,  # Qt.Key_Backspace
                16777220: Key.enter,      # Qt.Key_Return
                16777221: Key.enter,      # Qt.Key_Enter
                16777217: Key.tab,        # Qt.Key_Tab
                16777216: Key.esc,        # Qt.Key_Escape
                16777223: Key.delete,     # Qt.Key_Delete
                16777232: Key.home,       # Qt.Key_Home
                16777233: Key.end,        # Qt.Key_End
                16777234: Key.left,       # Qt.Key_Left
                16777235: Key.up,         # Qt.Key_Up
                16777236: Key.right,      # Qt.Key_Right
                16777237: Key.down,       # Qt.Key_Down
                16777238: Key.page_up,    # Qt.Key_PageUp
                16777239: Key.page_down,  # Qt.Key_PageDown
                16777248: Key.shift,      # Qt.Key_Shift
                16777249: Key.ctrl,       # Qt.Key_Control
                16777251: Key.alt,        # Qt.Key_Alt
                16777252: Key.caps_lock,  # Qt.Key_CapsLock
                16777264: Key.f1,         # Qt.Key_F1
                16777265: Key.f2,         # Qt.Key_F2
                16777266: Key.f3,         # Qt.Key_F3
                16777267: Key.f4,         # Qt.Key_F4
                16777268: Key.f5,         # Qt.Key_F5
                16777269: Key.f6,         # Qt.Key_F6
                16777270: Key.f7,         # Qt.Key_F7
                16777271: Key.f8,         # Qt.Key_F8
                16777272: Key.f9,         # Qt.Key_F9
                16777273: Key.f10,        # Qt.Key_F10
                16777274: Key.f11,        # Qt.Key_F11
                16777275: Key.f12,        # Qt.Key_F12
                32: Key.space,            # Qt.Key_Space
            }
            
            # Verificar si es una tecla especial
            if key_code in special_keys:
                key = special_keys[key_code]
            else:
                # Para teclas normales, usar el código directamente
                # Qt envía el código Unicode para caracteres normales
                if 32 <= key_code <= 126:  # Caracteres ASCII imprimibles
                    key = KeyCode.from_char(chr(key_code).lower())
                else:
                    # Ignorar teclas no mapeadas
                    return
            
            # Presionar o soltar la tecla
            if pressed:
                print(f"[Servidor] Presionando tecla: {key_code} -> {key}")
                self.keyboard.press(key)
            else:
                print(f"[Servidor] Soltando tecla: {key_code} -> {key}")
                self.keyboard.release(key)
                
        except Exception as e:
            print(f"[Servidor] Error al manejar tecla {key_code}: {e}")
    
    def _handle_clipboard_update(self, text: str):
        """Actualiza el portapapeles local"""
        with self.clipboard_lock:
            self.last_clipboard = text
            try:
                pyperclip.copy(text)
            except Exception as e:
                print(f"[Servidor] Error al actualizar portapapeles: {e}")
    
    def _handle_file_metadata(self, client_socket: socket.socket, file_id: int, filesize: int, filename: str):
        """Maneja metadatos de archivo entrante"""
        print(f"[Servidor] Recibiendo archivo: {filename} ({filesize} bytes)")
        self.file_transfers[file_id] = {
            'filename': filename,
            'filesize': filesize,
            'received': 0,
            'chunks': {},
            'socket': client_socket
        }
    
    def _handle_file_chunk(self, file_id: int, chunk_num: int, data: bytes):
        """Maneja un chunk de archivo"""
        if file_id not in self.file_transfers:
            print(f"[Servidor] Chunk recibido para archivo desconocido: {file_id}")
            return
        
        transfer = self.file_transfers[file_id]
        transfer['chunks'][chunk_num] = data
        transfer['received'] += len(data)
        
        # Verificar si se completó la transferencia
        if transfer['received'] >= transfer['filesize']:
            self._complete_file_transfer(file_id)
    
    def _complete_file_transfer(self, file_id: int):
        """Completa una transferencia de archivo"""
        transfer = self.file_transfers[file_id]
        filename = transfer['filename']
        
        # Ensamblar archivo
        chunks = transfer['chunks']
        sorted_chunks = [chunks[i] for i in sorted(chunks.keys())]
        file_data = b''.join(sorted_chunks)
        
        # Guardar archivo
        try:
            with open(filename, 'wb') as f:
                f.write(file_data)
            print(f"[Servidor] Archivo guardado: {filename}")
        except Exception as e:
            print(f"[Servidor] Error al guardar archivo: {e}")
        
        # Limpiar
        del self.file_transfers[file_id]
    
    def _init_monitor(self):
        """Inicializa el monitor (debe llamarse desde el thread principal)"""
        with mss.mss() as sct:
            self.available_monitors = sct.monitors[1:]  # Todos los monitores (sin el virtual)
            
            # Verificar que el índice del monitor es válido
            if self.monitor_index < 1 or self.monitor_index > len(self.available_monitors):
                print(f"[Servidor] Monitor {self.monitor_index} no existe, usando monitor 1")
                self.monitor_index = 1
            
            self.monitor = self.available_monitors[self.monitor_index - 1]
            
            # Mostrar información de monitores disponibles
            print(f"[Servidor] Monitores disponibles: {len(self.available_monitors)}")
            for i, mon in enumerate(self.available_monitors, 1):
                marker = " (ACTIVO)" if i == self.monitor_index else ""
                print(f"  Monitor {i}: {mon['width']}x{mon['height']} en ({mon['left']}, {mon['top']}){marker}")
    
    def _change_monitor(self, direction: int):
        """Cambia al monitor anterior o siguiente"""
        if not self.available_monitors:
            print("[Servidor] No hay monitores disponibles")
            return
        
        # Calcular nuevo índice
        new_index = self.monitor_index + direction
        
        # Wrap around (circular)
        if new_index < 1:
            new_index = len(self.available_monitors)
        elif new_index > len(self.available_monitors):
            new_index = 1
        
        # Actualizar monitor
        self.monitor_index = new_index
        self.monitor = self.available_monitors[self.monitor_index - 1]
        
        # Resetear estado del ratón para evitar problemas
        self._last_mouse_buttons = 0
        
        print(f"[Servidor] Cambiando a monitor {self.monitor_index}: {self.monitor['width']}x{self.monitor['height']}")
        
        # Mostrar todos los monitores con el nuevo activo
        for i, mon in enumerate(self.available_monitors, 1):
            marker = " (ACTIVO)" if i == self.monitor_index else ""
            print(f"  Monitor {i}: {mon['width']}x{mon['height']} en ({mon['left']}, {mon['top']}){marker}")
        
        # Enviar notificación a todos los clientes conectados
        # El siguiente frame tendrá la nueva resolución y el cliente se actualizará automáticamente
    
    def _capture_screen(self, client_socket: socket.socket):
        """
        Captura la pantalla continuamente y la envía al cliente
        
        Args:
            client_socket: Socket del cliente
        """
        print("[Servidor] Iniciando captura de pantalla")
        
        target_fps = 30
        frame_time = 1.0 / target_fps
        
        previous_frame = None
        
        # Crear instancia de mss para este thread
        with mss.mss() as sct:
            while self.running and client_socket in self.clients:
                start_time = time.time()
                
                try:
                    # Capturar pantalla
                    screenshot = sct.grab(self.monitor)
                    
                    # Convertir a PIL Image
                    img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                    
                    # Detectar cambios (simple: comparar con frame anterior)
                    # Por ahora, enviar siempre el frame completo
                    
                    # Comprimir imagen a JPEG
                    buffer = io.BytesIO()
                    img.save(buffer, format='JPEG', quality=75, optimize=True)
                    frame_data = buffer.getvalue()
                    
                    # Codificar y enviar
                    payload = encode_video_frame(
                        0, 0, 
                        self.monitor['width'], 
                        self.monitor['height'],
                        frame_data,
                        encoding=1  # 1 = JPEG
                    )
                    
                    message = self.protocol.encode_message(
                        MessageType.VIDEO_FRAME,
                        payload,
                        compress=True
                    )
                    
                    client_socket.sendall(message)
                    
                    # Controlar FPS
                    elapsed = time.time() - start_time
                    sleep_time = frame_time - elapsed
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    
                except Exception as e:
                    print(f"[Servidor] Error en captura: {e}")
                    break
        
        print("[Servidor] Captura de pantalla detenida")
    
    def _monitor_clipboard(self):
        """Monitorea el portapapeles y envía cambios a los clientes"""
        print("[Servidor] Iniciando monitoreo de portapapeles")
        
        while self.running:
            try:
                with self.clipboard_lock:
                    current = pyperclip.paste()
                    
                    if current != self.last_clipboard:
                        self.last_clipboard = current
                        
                        # Enviar a todos los clientes
                        payload = encode_clipboard_text(current)
                        message = self.protocol.encode_message(
                            MessageType.CLIPBOARD_TEXT,
                            payload,
                            compress=True
                        )
                        
                        for client_socket in list(self.clients.keys()):
                            try:
                                client_socket.sendall(message)
                            except:
                                pass
                
                time.sleep(0.5)  # Verificar cada 500ms
                
            except Exception as e:
                print(f"[Servidor] Error en monitoreo de portapapeles: {e}")
                time.sleep(1)


def main():
    """Función principal"""
    import argparse
    from connection_code import get_code_manager
    
    parser = argparse.ArgumentParser(description='Servidor de Escritorio Remoto')
    parser.add_argument('--host', default='0.0.0.0', help='Dirección IP para escuchar')
    parser.add_argument('--port', type=int, default=5900, help='Puerto para escuchar')
    parser.add_argument('--password', default='', help='Contraseña de conexión')
    parser.add_argument('--monitor', type=int, default=1, help='Monitor a capturar (1 = principal, 2 = segundo, etc.)')
    parser.add_argument('--code', default='', help='Código de conexión personalizado (opcional)')
    
    args = parser.parse_args()
    
    # Generar o usar código de conexión
    code_manager = get_code_manager()
    connection_code = code_manager.generate_code(args.code if args.code else None)
    
    # Obtener IPs
    local_ip = code_manager.get_local_ip()
    public_ip = code_manager.get_public_ip()
    
    # Probar servidor central
    central_server_ok = code_manager.test_central_server()
    
    # Registrar el código (usa IP pública si es diferente de la local)
    register_ip = public_ip if public_ip != local_ip else local_ip
    code_manager.register_code(connection_code, register_ip, args.port, connection_code)
    
    print("========================================")
    print("  SERVIDOR DE ESCRITORIO REMOTO - ISR")
    print("========================================")
    print(f"Código de conexión: {connection_code}")
    print(f"IP local: {local_ip}:{args.port}")
    if public_ip != local_ip:
        print(f"IP pública: {public_ip}:{args.port}")
    print(f"Monitor: {args.monitor}")
    print("")
    if central_server_ok:
        print("✓ Servidor central: Conectado")
        print(f"  URL: {code_manager.registry_server}")
    else:
        print("⚠ Servidor central: No disponible (usando registro local)")
    print("========================================")
    print("")
    print("Para conectar desde el cliente:")
    print(f"  - Usa el código: {connection_code}")
    if central_server_ok:
        print(f"  - Funciona desde cualquier red")
    else:
        print(f"  - O usa la IP: {local_ip}:{args.port} (misma red)")
        if public_ip != local_ip:
            print(f"  - O usa la IP: {public_ip}:{args.port} (desde Internet)")
    print("")
    print("Presiona Ctrl+C para detener el servidor")
    print("")
    
    server = RemoteDesktopServer(args.host, args.port, args.password, args.monitor)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[Servidor] Interrupción de teclado recibida")
    finally:
        server.stop()


if __name__ == '__main__':
    main()
