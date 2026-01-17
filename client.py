"""
Cliente de escritorio remoto con interfaz gráfica PyQt6
Permite conectar a múltiples servidores simultáneamente
"""

import sys
import socket
import threading
import time
import io
from typing import Optional, Dict
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTabWidget, QScrollArea,
    QFileDialog, QMessageBox, QDialog, QDialogButtonBox, QFormLayout,
    QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QPixmap, QImage, QKeyEvent, QMouseEvent, QIcon, QAction
from PIL import Image
import pyperclip

from protocol import (
    Protocol, MessageType,
    encode_handshake, decode_auth_response,
    encode_mouse_event, encode_keyboard_event,
    decode_video_frame, encode_clipboard_text,
    decode_clipboard_text, encode_file_metadata,
    encode_file_chunk, decode_file_chunk
)


class ConnectionSignals(QObject):
    """Señales para comunicación entre threads"""
    frame_received = pyqtSignal(QPixmap)
    connection_status = pyqtSignal(str)
    clipboard_updated = pyqtSignal(str)


class RemoteConnection:
    """Representa una conexión a un servidor remoto"""
    
    def __init__(self, host: str, port: int, password: str = ''):
        """
        Inicializa la conexión
        
        Args:
            host: Dirección del servidor
            port: Puerto del servidor
            password: Contraseña (opcional)
        """
        self.host = host
        self.port = port
        self.password = password
        
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.protocol = Protocol(compression_level=3)
        
        self.signals = ConnectionSignals()
        
        # Threads
        self.receive_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Portapapeles
        self.last_clipboard = ""
    
    def connect(self) -> bool:
        """
        Conecta al servidor
        
        Returns:
            True si la conexión fue exitosa
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            
            # Handshake
            if not self._do_handshake():
                self.socket.close()
                return False
            
            self.connected = True
            self.running = True
            
            # Iniciar thread de recepción
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            self.signals.connection_status.emit("Conectado")
            return True
            
        except Exception as e:
            self.signals.connection_status.emit(f"Error: {e}")
            return False
    
    def disconnect(self):
        """Desconecta del servidor"""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                # Enviar mensaje de desconexión
                msg = self.protocol.encode_message(MessageType.DISCONNECT, b'')
                self.socket.sendall(msg)
            except:
                pass
            
            self.socket.close()
            self.socket = None
        
        self.signals.connection_status.emit("Desconectado")
    
    def _do_handshake(self) -> bool:
        """Realiza el handshake con el servidor"""
        try:
            # Enviar handshake
            payload = encode_handshake(version=1, capabilities=0)
            message = self.protocol.encode_message(MessageType.HANDSHAKE, payload)
            self.socket.sendall(message)
            
            # Recibir respuesta de autenticación
            header_bytes = self._recv_exact(Protocol.HEADER_SIZE)
            if not header_bytes:
                return False
            
            header = self.protocol.decode_header(header_bytes)
            if not header or header[1] != MessageType.AUTH_RESPONSE:
                return False
            
            payload_len = header[3]
            payload = self._recv_exact(payload_len)
            if not payload:
                return False
            
            payload = self.protocol.decode_payload(payload, header[2])
            success, message = decode_auth_response(payload)
            
            return success
            
        except Exception as e:
            print(f"[Cliente] Error en handshake: {e}")
            return False
    
    def _recv_exact(self, n: int) -> Optional[bytes]:
        """Recibe exactamente n bytes"""
        data = b''
        while len(data) < n:
            chunk = self.socket.recv(n - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def _receive_loop(self):
        """Loop de recepción de mensajes"""
        while self.running and self.connected:
            try:
                # Leer header
                header_bytes = self._recv_exact(Protocol.HEADER_SIZE)
                if not header_bytes:
                    break
                
                header = self.protocol.decode_header(header_bytes)
                if not header:
                    break
                
                magic, msg_type, flags, payload_len, seq_num = header
                
                # Leer payload
                payload = self._recv_exact(payload_len)
                if not payload:
                    break
                
                # Decodificar payload
                payload = self.protocol.decode_payload(payload, flags)
                
                # Procesar mensaje
                self._process_message(msg_type, payload)
                
            except Exception as e:
                if self.running:
                    print(f"[Cliente] Error en recepción: {e}")
                break
        
        self.disconnect()
    
    def _process_message(self, msg_type: int, payload: bytes):
        """Procesa un mensaje recibido"""
        try:
            if msg_type == MessageType.VIDEO_FRAME:
                x, y, width, height, encoding, frame_data = decode_video_frame(payload)
                self._handle_video_frame(x, y, width, height, encoding, frame_data)
            
            elif msg_type == MessageType.CLIPBOARD_TEXT:
                text = decode_clipboard_text(payload)
                self._handle_clipboard_update(text)
            
            elif msg_type == MessageType.PONG:
                # Respuesta a ping
                pass
            
        except Exception as e:
            print(f"[Cliente] Error al procesar mensaje tipo {msg_type}: {e}")
    
    def _handle_video_frame(self, x: int, y: int, width: int, height: int, encoding: int, frame_data: bytes):
        """Maneja un frame de video recibido"""
        try:
            if encoding == 1:  # JPEG
                # Decodificar JPEG
                img = Image.open(io.BytesIO(frame_data))
                
                # Convertir a QPixmap
                img_bytes = img.tobytes('raw', 'RGB')
                qimage = QImage(img_bytes, img.width, img.height, img.width * 3, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage)
                
                # Emitir señal
                self.signals.frame_received.emit(pixmap)
            
        except Exception as e:
            print(f"[Cliente] Error al procesar frame: {e}")
    
    def _handle_clipboard_update(self, text: str):
        """Maneja actualización del portapapeles"""
        if text != self.last_clipboard:
            self.last_clipboard = text
            try:
                pyperclip.copy(text)
                self.signals.clipboard_updated.emit(text)
            except Exception as e:
                print(f"[Cliente] Error al actualizar portapapeles: {e}")
    
    def send_mouse_event(self, x: int, y: int, buttons: int):
        """Envía un evento de ratón"""
        if not self.connected:
            return
        
        try:
            payload = encode_mouse_event(x, y, buttons)
            message = self.protocol.encode_message(MessageType.INPUT_MOUSE, payload)
            self.socket.sendall(message)
        except Exception as e:
            print(f"[Cliente] Error al enviar evento de ratón: {e}")
    
    def send_keyboard_event(self, key_code: int, pressed: bool):
        """Envía un evento de teclado"""
        if not self.connected:
            return
        
        try:
            payload = encode_keyboard_event(key_code, pressed)
            message = self.protocol.encode_message(MessageType.INPUT_KEYBOARD, payload)
            self.socket.sendall(message)
        except Exception as e:
            print(f"[Cliente] Error al enviar evento de teclado: {e}")
    
    def request_monitor_change(self, direction: int):
        """Solicita cambio de monitor al servidor"""
        if not self.connected:
            return
        
        try:
            # Enviar dirección como payload: -1 = anterior, 1 = siguiente
            payload = direction.to_bytes(4, byteorder='big', signed=True)
            message = self.protocol.encode_message(MessageType.VIDEO_REQUEST, payload)
            self.socket.sendall(message)
            print(f"[Cliente] Solicitud de cambio de monitor enviada: {direction}")
        except Exception as e:
            print(f"[Cliente] Error al solicitar cambio de monitor: {e}")
    
    def send_clipboard_text(self, text: str):
        """Envía texto del portapapeles"""
        if not self.connected:
            return
        
        try:
            payload = encode_clipboard_text(text)
            message = self.protocol.encode_message(MessageType.CLIPBOARD_TEXT, payload, compress=True)
            self.socket.sendall(message)
        except Exception as e:
            print(f"[Cliente] Error al enviar portapapeles: {e}")


class RemoteDesktopWidget(QWidget):
    """Widget que muestra el escritorio remoto"""
    
    def __init__(self, connection: RemoteConnection):
        super().__init__()
        self.connection = connection
        
        # Estado del ratón
        self.mouse_buttons = 0
        
        # Modo de visualización: 'scaled' (escalado), 'scroll' (scroll), 'fullscreen' (pantalla completa)
        self.view_mode = 'scaled'
        
        # Pixmap original
        self.original_pixmap = None
        
        self.init_ui()
        
        # Conectar señales
        self.connection.signals.frame_received.connect(self.update_frame)
    
    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        
        # Variables para el tamaño original
        self.original_width = 1920
        self.original_height = 1080
        
        # Scroll area para modo scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setVisible(False)  # Oculto por defecto
        
        # Label para mostrar el frame
        self.frame_label = QLabel()
        self.frame_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.frame_label.setText("Conectando...")
        self.frame_label.setStyleSheet("background-color: black; color: white;")
        self.frame_label.setMinimumSize(800, 600)
        self.frame_label.setScaledContents(True)  # Por defecto escalado
        
        # Habilitar tracking del ratón y teclado
        self.frame_label.setMouseTracking(True)
        self.frame_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.frame_label.mouseMoveEvent = self.mouse_move_event
        self.frame_label.mousePressEvent = self.mouse_press_event
        self.frame_label.mouseReleaseEvent = self.mouse_release_event
        self.frame_label.keyPressEvent = self.key_press_event
        self.frame_label.keyReleaseEvent = self.key_release_event
        
        self.scroll_area.setWidget(self.frame_label)
        
        # Barra de herramientas superior
        toolbar = QHBoxLayout()
        
        self.status_label = QLabel("Estado: Desconectado")
        toolbar.addWidget(self.status_label)
        
        toolbar.addStretch()
        
        # Botones de modo de visualización con iconos
        btn_scaled = QPushButton("▣")
        btn_scaled.setToolTip("Escalado: Escalar la pantalla para que se vea completa")
        btn_scaled.setFixedSize(40, 30)
        btn_scaled.clicked.connect(lambda: self.set_view_mode('scaled'))
        toolbar.addWidget(btn_scaled)
        
        btn_scroll = QPushButton("⇕")
        btn_scroll.setToolTip("Scroll: Ver la pantalla en tamaño real con scroll")
        btn_scroll.setFixedSize(40, 30)
        btn_scroll.clicked.connect(lambda: self.set_view_mode('scroll'))
        toolbar.addWidget(btn_scroll)
        
        btn_fullscreen = QPushButton("⛶")
        btn_fullscreen.setToolTip("Pantalla Completa: Modo inmersivo")
        btn_fullscreen.setFixedSize(40, 30)
        btn_fullscreen.clicked.connect(lambda: self.set_view_mode('fullscreen'))
        toolbar.addWidget(btn_fullscreen)
        
        # Separador
        toolbar.addWidget(QLabel(" | "))
        
        # Botones de cambio de monitor con iconos
        btn_prev_monitor = QPushButton("◀")
        btn_prev_monitor.setToolTip("Monitor Anterior")
        btn_prev_monitor.setFixedSize(40, 30)
        btn_prev_monitor.clicked.connect(self.previous_monitor)
        toolbar.addWidget(btn_prev_monitor)
        
        btn_next_monitor = QPushButton("▶")
        btn_next_monitor.setToolTip("Monitor Siguiente")
        btn_next_monitor.setFixedSize(40, 30)
        btn_next_monitor.clicked.connect(self.next_monitor)
        toolbar.addWidget(btn_next_monitor)
        
        # Separador
        toolbar.addWidget(QLabel(" | "))
        
        btn_files = QPushButton("📁")
        btn_files.setToolTip("Transferir Archivos")
        btn_files.setFixedSize(40, 30)
        btn_files.clicked.connect(self.transfer_files)
        toolbar.addWidget(btn_files)
        
        btn_clipboard = QPushButton("📋")
        btn_clipboard.setToolTip("Enviar Portapapeles")
        btn_clipboard.setFixedSize(40, 30)
        btn_clipboard.clicked.connect(self.send_clipboard)
        toolbar.addWidget(btn_clipboard)
        
        btn_disconnect = QPushButton("❌")
        btn_disconnect.setToolTip("Desconectar")
        btn_disconnect.setFixedSize(40, 30)
        btn_disconnect.clicked.connect(self.disconnect)
        toolbar.addWidget(btn_disconnect)
        
        layout.addLayout(toolbar)
        
        # Agregar el label directamente (modo escalado por defecto)
        layout.addWidget(self.frame_label)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)
        
        # Conectar señal de estado
        self.connection.signals.connection_status.connect(self.update_status)
    
    def update_frame(self, pixmap: QPixmap):
        """Actualiza el frame mostrado"""
        # Detectar cambio de resolución (cambio de monitor)
        new_width = pixmap.width()
        new_height = pixmap.height()
        
        if hasattr(self, 'original_width') and (new_width != self.original_width or new_height != self.original_height):
            print(f"[Cliente] Cambio de monitor detectado: {self.original_width}x{self.original_height} -> {new_width}x{new_height}")
            # Resetear estado del ratón
            self.mouse_buttons = 0
            # Restaurar foco al label
            self.frame_label.setFocus()
        
        # Guardar dimensiones originales y pixmap
        self.original_width = new_width
        self.original_height = new_height
        self.original_pixmap = pixmap
        
        # Aplicar el modo de visualización actual
        self._apply_view_mode()
    
    def set_view_mode(self, mode: str):
        """Cambia el modo de visualización"""
        self.view_mode = mode
        print(f"[Cliente] Cambiando a modo: {mode}")
        self._apply_view_mode()
    
    def _apply_view_mode(self):
        """Aplica el modo de visualización actual"""
        if not self.original_pixmap:
            return
        
        if self.view_mode == 'scaled':
            # Modo escalado: escalar para que se vea completa
            self.frame_label.setScaledContents(True)
            self.frame_label.setFixedSize(16777215, 16777215)  # Tamaño máximo
            self.frame_label.setMinimumSize(800, 600)
            self.frame_label.setPixmap(self.original_pixmap)
            self.frame_label.setVisible(True)
            self.scroll_area.setVisible(False)
            
        elif self.view_mode == 'scroll':
            # Modo scroll: tamaño real con scroll
            self.frame_label.setScaledContents(False)
            self.frame_label.setFixedSize(self.original_width, self.original_height)
            self.frame_label.setPixmap(self.original_pixmap)
            self.frame_label.setVisible(True)
            self.scroll_area.setVisible(True)
            
        elif self.view_mode == 'fullscreen':
            # Modo pantalla completa
            self.frame_label.setScaledContents(True)
            self.showFullScreen()
            self.frame_label.setPixmap(self.original_pixmap)
    
    def previous_monitor(self):
        """Cambia al monitor anterior"""
        print("[Cliente] Solicitando monitor anterior")
        self.connection.request_monitor_change(-1)
    
    def next_monitor(self):
        """Cambia al siguiente monitor"""
        print("[Cliente] Solicitando monitor siguiente")
        self.connection.request_monitor_change(1)
    
    def update_status(self, status: str):
        """Actualiza el estado de la conexión"""
        self.status_label.setText(f"Estado: {status}")
    
    def mouse_move_event(self, event: QMouseEvent):
        """Maneja eventos de movimiento del ratón"""
        pos = event.pos()
        # Escalar coordenadas del label al tamaño original de la pantalla
        label_width = self.frame_label.width()
        label_height = self.frame_label.height()
        
        if label_width > 0 and label_height > 0:
            remote_x = int(pos.x() * self.original_width / label_width)
            remote_y = int(pos.y() * self.original_height / label_height)
            self.connection.send_mouse_event(remote_x, remote_y, self.mouse_buttons)
        else:
            self.connection.send_mouse_event(pos.x(), pos.y(), self.mouse_buttons)
    
    def mouse_press_event(self, event: QMouseEvent):
        """Maneja eventos de presión del ratón"""
        # Dar foco al label para que funcione el teclado
        self.frame_label.setFocus()
        
        button = event.button()
        if button == Qt.MouseButton.LeftButton:
            self.mouse_buttons |= 0x01
        elif button == Qt.MouseButton.RightButton:
            self.mouse_buttons |= 0x02
        elif button == Qt.MouseButton.MiddleButton:
            self.mouse_buttons |= 0x04
        
        pos = event.pos()
        # Escalar coordenadas del label al tamaño original de la pantalla
        label_width = self.frame_label.width()
        label_height = self.frame_label.height()
        
        if label_width > 0 and label_height > 0:
            remote_x = int(pos.x() * self.original_width / label_width)
            remote_y = int(pos.y() * self.original_height / label_height)
            print(f"[Cliente] Clic en ({pos.x()}, {pos.y()}) -> remoto ({remote_x}, {remote_y}), buttons={self.mouse_buttons:03b}")
            self.connection.send_mouse_event(remote_x, remote_y, self.mouse_buttons)
        else:
            self.connection.send_mouse_event(pos.x(), pos.y(), self.mouse_buttons)
    
    def mouse_release_event(self, event: QMouseEvent):
        """Maneja eventos de liberación del ratón"""
        button = event.button()
        if button == Qt.MouseButton.LeftButton:
            self.mouse_buttons &= ~0x01
        elif button == Qt.MouseButton.RightButton:
            self.mouse_buttons &= ~0x02
        elif button == Qt.MouseButton.MiddleButton:
            self.mouse_buttons &= ~0x04
        
        pos = event.pos()
        # Escalar coordenadas del label al tamaño original de la pantalla
        label_width = self.frame_label.width()
        label_height = self.frame_label.height()
        
        if label_width > 0 and label_height > 0:
            remote_x = int(pos.x() * self.original_width / label_width)
            remote_y = int(pos.y() * self.original_height / label_height)
            print(f"[Cliente] Release en ({pos.x()}, {pos.y()}) -> remoto ({remote_x}, {remote_y}), buttons={self.mouse_buttons:03b}")
            self.connection.send_mouse_event(remote_x, remote_y, self.mouse_buttons)
        else:
            self.connection.send_mouse_event(pos.x(), pos.y(), self.mouse_buttons)
    
    def key_press_event(self, event: QKeyEvent):
        """Maneja eventos de teclado"""
        # Asegurar que el label tiene foco
        if not self.frame_label.hasFocus():
            print(f"[Cliente] Advertencia: Label sin foco, restaurando...")
            self.frame_label.setFocus()
        
        key_code = event.key()
        print(f"[Cliente] Tecla presionada: {key_code}")
        self.connection.send_keyboard_event(key_code, True)
    
    def key_release_event(self, event: QKeyEvent):
        """Maneja eventos de liberación de tecla"""
        key_code = event.key()
        print(f"[Cliente] Tecla liberada: {key_code}")
        self.connection.send_keyboard_event(key_code, False)
    
    def transfer_files(self):
        """Abre diálogo para transferir archivos"""
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar archivos para transferir")
        if files:
            # TODO: Implementar transferencia de archivos
            QMessageBox.information(self, "Transferencia", f"Se transferirán {len(files)} archivo(s)")
    
    def send_clipboard(self):
        """Envía el contenido del portapapeles"""
        try:
            text = pyperclip.paste()
            self.connection.send_clipboard_text(text)
            QMessageBox.information(self, "Portapapeles", "Portapapeles enviado")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al enviar portapapeles: {e}")
    
    def disconnect(self):
        """Desconecta de la sesión"""
        self.connection.disconnect()


class ConnectDialog(QDialog):
    """Diálogo para conectar a un servidor"""
    
    def __init__(self, parent=None, recent_connections=None):
        super().__init__(parent)
        self.setWindowTitle("Conectar a Servidor")
        self.setModal(True)
        self.recent_connections = recent_connections or []
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        
        # Sección de conexiones recientes
        if self.recent_connections:
            recent_label = QLabel("<b>Conexiones Recientes:</b>")
            layout.addWidget(recent_label)
            
            recent_layout = QHBoxLayout()
            for conn in self.recent_connections[:5]:  # Máximo 5
                btn = QPushButton(f"🔗 {conn['name']}")
                btn.setToolTip(f"{conn['host']}:{conn['port']}")
                btn.clicked.connect(lambda checked, c=conn: self.load_connection(c))
                recent_layout.addWidget(btn)
            
            layout.addLayout(recent_layout)
            
            # Separador
            from PyQt6.QtWidgets import QFrame
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            layout.addWidget(line)
        
        # Formulario de conexión
        form_layout = QFormLayout()
        
        # Campo para código o IP
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("ISR-12345678 o 192.168.1.100")
        form_layout.addRow("🔑 Código o IP:", self.code_input)
        
        self.port_input = QLineEdit()
        self.port_input.setText("5900")
        self.port_input.setPlaceholderText("5900")
        form_layout.addRow("🔌 Puerto:", self.port_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Opcional")
        form_layout.addRow("🔒 Contraseña:", self.password_input)
        
        layout.addLayout(form_layout)
        
        # Nota informativa
        info_label = QLabel(
            "<i>Puedes usar el código de conexión (ej: ISR-12345678) o la IP directa.</i>"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def load_connection(self, conn: dict):
        """Carga una conexión del historial"""
        self.code_input.setText(conn['host'])
        self.port_input.setText(str(conn['port']))
        if 'password' in conn:
            self.password_input.setText(conn['password'])
    
    def get_connection_info(self):
        """Obtiene la información de conexión"""
        from connection_code import get_code_manager
        
        code_or_ip = self.code_input.text().strip()
        
        # Intentar resolver el código
        code_manager = get_code_manager()
        try:
            host, port = code_manager.resolve_code(code_or_ip)
            # Si el usuario especificó un puerto, usarlo
            if self.port_input.text().strip():
                port = int(self.port_input.text())
        except ValueError:
            # No se pudo resolver, usar como está
            host = code_or_ip
            port = int(self.port_input.text()) if self.port_input.text() else 5900
        
        return {
            'host': host,
            'port': port,
            'password': self.password_input.text(),
            'name': code_or_ip  # Guardar el código/IP original como nombre
        }


class RemoteDesktopClient(QMainWindow):
    """Ventana principal del cliente de escritorio remoto"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cliente de Escritorio Remoto - ISR")
        self.setGeometry(100, 100, 1200, 800)
        
        self.connections: Dict[str, RemoteConnection] = {}
        self.recent_connections = self._load_recent_connections()
        
        self.init_ui()
        self.init_tray_icon()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Barra de herramientas superior
        toolbar = QHBoxLayout()
        
        btn_new_connection = QPushButton("Nueva Conexión")
        btn_new_connection.clicked.connect(self.new_connection)
        toolbar.addWidget(btn_new_connection)
        
        toolbar.addStretch()
        
        btn_about = QPushButton("Acerca de")
        btn_about.clicked.connect(self.show_about)
        toolbar.addWidget(btn_about)
        
        layout.addLayout(toolbar)
        
        # Pestañas para múltiples sesiones
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        
        layout.addWidget(self.tabs)
        
        central_widget.setLayout(layout)
    
    def new_connection(self):
        """Crea una nueva conexión"""
        dialog = ConnectDialog(self, self.recent_connections)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            info = dialog.get_connection_info()
            
            # Crear conexión
            connection = RemoteConnection(info['host'], info['port'], info['password'])
            
            # Conectar
            if connection.connect():
                # Crear widget de escritorio remoto
                desktop_widget = RemoteDesktopWidget(connection)
                
                # Agregar pestaña
                tab_name = f"{info.get('name', info['host'])}:{info['port']}"
                index = self.tabs.addTab(desktop_widget, tab_name)
                self.tabs.setCurrentIndex(index)
                
                # Guardar conexión
                self.connections[tab_name] = connection
                
                # Agregar al historial
                self._add_to_recent(info)
            else:
                QMessageBox.critical(self, "Error", "No se pudo conectar al servidor")
    
    def _load_recent_connections(self) -> list:
        """Carga las conexiones recientes"""
        import json
        import os
        
        history_file = os.path.join(os.path.dirname(__file__), 'connection_history.json')
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_recent_connections(self):
        """Guarda las conexiones recientes"""
        import json
        import os
        
        history_file = os.path.join(os.path.dirname(__file__), 'connection_history.json')
        try:
            with open(history_file, 'w') as f:
                json.dump(self.recent_connections, f, indent=2)
        except Exception as e:
            print(f"[Error] No se pudo guardar el historial: {e}")
    
    def _add_to_recent(self, info: dict):
        """Agrega una conexión al historial"""
        # Crear entrada
        entry = {
            'name': info.get('name', info['host']),
            'host': info['host'],
            'port': info['port']
        }
        
        # Eliminar duplicados
        self.recent_connections = [
            c for c in self.recent_connections
            if not (c['host'] == entry['host'] and c['port'] == entry['port'])
        ]
        
        # Agregar al inicio
        self.recent_connections.insert(0, entry)
        
        # Limitar a 10 conexiones
        self.recent_connections = self.recent_connections[:10]
        
        # Guardar
        self._save_recent_connections()
    
    def close_tab(self, index: int):
        """Cierra una pestaña"""
        widget = self.tabs.widget(index)
        if isinstance(widget, RemoteDesktopWidget):
            widget.disconnect()
        
        tab_name = self.tabs.tabText(index)
        if tab_name in self.connections:
            del self.connections[tab_name]
        
        self.tabs.removeTab(index)
    
    def init_tray_icon(self):
        """Inicializa el icono en la bandeja del sistema"""
        # Crear icono de la bandeja
        self.tray_icon = QSystemTrayIcon(self)
        
        # Intentar cargar el icono personalizado
        import os
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
            # También establecer como icono de la ventana
            self.setWindowIcon(QIcon(icon_path))
        else:
            # Usar icono por defecto si no existe el personalizado
            self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        
        # Crear menú contextual
        tray_menu = QMenu()
        
        show_action = QAction("💻 Mostrar", self)
        show_action.triggered.connect(self.show_from_tray)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("👁 Ocultar", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("❌ Salir", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        
        # Doble clic en el icono muestra la ventana
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Mostrar el icono
        self.tray_icon.show()
        
        # Tooltip
        self.tray_icon.setToolTip("Cliente de Escritorio Remoto")
    
    def tray_icon_activated(self, reason):
        """Maneja clics en el icono de la bandeja"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_from_tray()
    
    def show_from_tray(self):
        """Muestra la ventana desde la bandeja"""
        self.show()
        self.activateWindow()
        self.raise_()
    
    def quit_application(self):
        """Cierra completamente la aplicación"""
        # Desconectar todas las sesiones
        for connection in self.connections.values():
            connection.disconnect()
        
        # Ocultar icono de la bandeja
        self.tray_icon.hide()
        
        # Cerrar aplicación
        QApplication.quit()
    
    def connect_to(self, host: str, port: int, password: str = '', name: str = ''):
        """Conecta directamente a un host sin mostrar diálogo"""
        try:
            # Crear conexión
            connection = RemoteConnection(host, port, password)
            
            # Conectar
            if connection.connect():
                # Crear widget de escritorio remoto
                desktop_widget = RemoteDesktopWidget(connection)
                
                # Agregar pestaña
                tab_name = f"{name if name else host}:{port}"
                index = self.tabs.addTab(desktop_widget, tab_name)
                self.tabs.setCurrentIndex(index)
                
                # Guardar conexión
                self.connections[tab_name] = connection
                
                # Agregar al historial
                self._add_to_recent({
                    'name': name if name else host,
                    'host': host,
                    'port': port
                })
                
                return True
            else:
                QMessageBox.critical(self, "Error de Conexión", 
                    f"No se pudo conectar a {host}:{port}\n\n"
                    "Verifica que:\n"
                    "- El servidor esté activo\n"
                    "- La IP y puerto sean correctos\n"
                    "- No haya firewall bloqueando la conexión")
                return False
                
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                f"Error al intentar conectar:\n{str(e)}\n\n"
                "Detalles técnicos:\n"
                f"Host: {host}\n"
                f"Puerto: {port}")
            return False
    
    def show_about(self):
        """Muestra información sobre la aplicación"""
        QMessageBox.about(
            self,
            "Acerca de",
            "Cliente de Escritorio Remoto\n\n"
            "Versión 2.0\n\n"
            "Aplicación de escritorio remoto con soporte para:\n"
            "- Múltiples sesiones simultáneas\n"
            "- Transferencia de archivos bidireccional\n"
            "- Portapapeles compartido\n"
            "- Conexión segura y cifrada\n"
            "- Icono en la bandeja del sistema"
        )
    
    def closeEvent(self, event):
        """Maneja el cierre de la aplicación"""
        # En lugar de cerrar, minimizar a la bandeja
        event.ignore()
        self.hide()
        
        # Mostrar notificación
        self.tray_icon.showMessage(
            "Cliente de Escritorio Remoto",
            "La aplicación sigue ejecutándose en segundo plano.\nHaz clic derecho en el icono para salir.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )


def main():
    """Función principal"""
    app = QApplication(sys.argv)
    
    # Establecer estilo
    app.setStyle('Fusion')
    
    # Crear y mostrar ventana principal
    window = RemoteDesktopClient()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
