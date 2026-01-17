#!/usr/bin/env python3
"""
ISR Remote Desktop - Aplicación Unificada v3.0.5
Permite controlar otros equipos y ser controlado desde una sola aplicación

Cambios en v3.0.5:
- Corregido error de dependencia circular en connection_code.py
- Agregada guía de configuración para servidor Linux con IP pública
- Agregado script de verificación del servidor (test_server_linux.py)
- Simplificada detección de red para evitar errores de inicialización

Cambios en v3.0.4:
- Detección automática de servidor central (IP local vs IP pública)
- Usa 192.168.0.57:8080 cuando está en la red local
- Usa 77.225.201.4:8080 cuando está fuera de la red
- Soluciona problema de NAT loopback

Cambios en v3.0.3:
- Corregido bug que colgaba la aplicación al detener el servidor
- Agregada guía de configuración de port forwarding para conexión desde Internet
- Agregado script de prueba de conectividad
"""

import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QLabel, QPushButton,
                             QLineEdit, QTextEdit, QGroupBox, QFormLayout,
                             QCheckBox, QSpinBox, QMessageBox, QSystemTrayIcon,
                             QMenu, QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QAction
import threading

# Importar módulos existentes
from server import RemoteDesktopServer
from client import RemoteConnection, RemoteDesktopWidget
from connection_code import get_code_manager


class ServerThread(QThread):
    """Thread para ejecutar el servidor"""
    log_signal = pyqtSignal(str)
    code_signal = pyqtSignal(str, str, int)  # code, ip, port
    error_signal = pyqtSignal(str)
    
    def __init__(self, port=5900, password='', monitor=1):
        super().__init__()
        self.port = port
        self.password = password
        self.monitor = monitor
        self.server = None
        self.running = False
    
    def run(self):
        """Ejecuta el servidor"""
        try:
            self.running = True
            
            # Generar código
            code_manager = get_code_manager()
            connection_code = code_manager.generate_code()
            
            # Obtener IPs
            local_ip = code_manager.get_local_ip()
            public_ip = code_manager.get_public_ip()
            
            # Registrar código
            register_ip = public_ip if public_ip != local_ip else local_ip
            code_manager.register_code(connection_code, register_ip, self.port, connection_code)
            
            # Emitir código
            self.code_signal.emit(connection_code, register_ip, self.port)
            
            self.log_signal.emit(f"Servidor iniciado en puerto {self.port}")
            self.log_signal.emit(f"Código: {connection_code}")
            self.log_signal.emit(f"IP: {register_ip}:{self.port}")
            
            # Iniciar servidor
            self.server = RemoteDesktopServer('0.0.0.0', self.port, self.password, self.monitor)
            self.server.start()
            
        except Exception as e:
            self.error_signal.emit(f"Error en el servidor: {str(e)}")
        finally:
            self.running = False
    
    def stop(self):
        """Detiene el servidor"""
        self.running = False
        if self.server:
            try:
                self.server.shutdown()
            except:
                pass


class SettingsDialog(QDialog):
    """Diálogo de configuración"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración")
        self.setMinimumWidth(400)
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        
        # Servidor
        server_group = QGroupBox("Configuración del Servidor")
        server_layout = QFormLayout()
        
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1024, 65535)
        self.port_spin.setValue(5900)
        server_layout.addRow("Puerto:", self.port_spin)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Dejar vacío para sin contraseña")
        server_layout.addRow("Contraseña:", self.password_edit)
        
        self.monitor_spin = QSpinBox()
        self.monitor_spin.setRange(1, 10)
        self.monitor_spin.setValue(1)
        server_layout.addRow("Monitor:", self.monitor_spin)
        
        self.autostart_check = QCheckBox("Iniciar servidor automáticamente")
        server_layout.addRow("", self.autostart_check)
        
        server_group.setLayout(server_layout)
        layout.addWidget(server_group)
        
        # Cliente
        client_group = QGroupBox("Configuración del Cliente")
        client_layout = QFormLayout()
        
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 100)
        self.quality_spin.setValue(75)
        client_layout.addRow("Calidad JPEG:", self.quality_spin)
        
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 60)
        self.fps_spin.setValue(30)
        client_layout.addRow("FPS máximo:", self.fps_spin)
        
        client_group.setLayout(client_layout)
        layout.addWidget(client_group)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def load_settings(self):
        """Carga la configuración"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    self.port_spin.setValue(settings.get('port', 5900))
                    self.password_edit.setText(settings.get('password', ''))
                    self.monitor_spin.setValue(settings.get('monitor', 1))
                    self.autostart_check.setChecked(settings.get('autostart', False))
                    self.quality_spin.setValue(settings.get('quality', 75))
                    self.fps_spin.setValue(settings.get('fps', 30))
        except:
            pass
    
    def save_settings(self):
        """Guarda la configuración"""
        settings = {
            'port': self.port_spin.value(),
            'password': self.password_edit.text(),
            'monitor': self.monitor_spin.value(),
            'autostart': self.autostart_check.isChecked(),
            'quality': self.quality_spin.value(),
            'fps': self.fps_spin.value()
        }
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo guardar la configuración: {e}")
    
    def get_settings(self):
        """Obtiene la configuración actual"""
        return {
            'port': self.port_spin.value(),
            'password': self.password_edit.text(),
            'monitor': self.monitor_spin.value(),
            'autostart': self.autostart_check.isChecked(),
            'quality': self.quality_spin.value(),
            'fps': self.fps_spin.value()
        }


class ISRRemoteDesktop(QMainWindow):
    """Aplicación principal unificada"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ISR Remote Desktop")
        self.setMinimumSize(900, 600)
        
        # Cargar icono
        if os.path.exists('icon.ico'):
            self.setWindowIcon(QIcon('icon.ico'))
        
        self.server_thread = None
        self.connections = {}  # Diccionario de conexiones activas
        
        self.init_ui()
        self.init_tray()
        self.load_settings()
        
        # Autostart del servidor si está configurado
        if self.settings.get('autostart', False):
            QTimer.singleShot(1000, self.start_server)
    
    def init_ui(self):
        """Inicializa la interfaz"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Tabs principales
        self.tabs = QTabWidget()
        
        # Tab 1: Permitir Control (Servidor)
        self.server_tab = self.create_server_tab()
        self.tabs.addTab(self.server_tab, "🖥️ Permitir Control")
        
        # Tab 2: Controlar Otro Equipo (Cliente)
        self.client_tab = self.create_client_tab()
        self.tabs.addTab(self.client_tab, "🖱️ Controlar Equipo")
        
        layout.addWidget(self.tabs)
        
        # Barra de estado
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Listo")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        settings_btn = QPushButton("⚙️ Configuración")
        settings_btn.clicked.connect(self.show_settings)
        status_layout.addWidget(settings_btn)
        
        layout.addLayout(status_layout)
        
        central_widget.setLayout(layout)
    
    def create_server_tab(self):
        """Crea la pestaña del servidor"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Información
        info_group = QGroupBox("Tu Código de Conexión")
        info_layout = QVBoxLayout()
        
        self.code_label = QLabel("No iniciado")
        self.code_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        self.code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.code_label)
        
        self.ip_label = QLabel("")
        self.ip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.ip_label)
        
        copy_btn = QPushButton("📋 Copiar Código")
        copy_btn.clicked.connect(self.copy_code)
        info_layout.addWidget(copy_btn)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Controles
        controls_layout = QHBoxLayout()
        
        self.start_server_btn = QPushButton("▶️ Iniciar Servidor")
        self.start_server_btn.clicked.connect(self.start_server)
        self.start_server_btn.setStyleSheet("padding: 10px; font-size: 14px;")
        controls_layout.addWidget(self.start_server_btn)
        
        self.stop_server_btn = QPushButton("⏹️ Detener Servidor")
        self.stop_server_btn.clicked.connect(self.stop_server)
        self.stop_server_btn.setEnabled(False)
        self.stop_server_btn.setStyleSheet("padding: 10px; font-size: 14px;")
        controls_layout.addWidget(self.stop_server_btn)
        
        layout.addLayout(controls_layout)
        
        # Log
        log_group = QGroupBox("Registro de Actividad")
        log_layout = QVBoxLayout()
        
        self.server_log = QTextEdit()
        self.server_log.setReadOnly(True)
        self.server_log.setMaximumHeight(200)
        log_layout.addWidget(self.server_log)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Instrucciones
        instructions = QLabel(
            "<b>Instrucciones:</b><br>"
            "1. Haz clic en 'Iniciar Servidor'<br>"
            "2. Comparte tu código con quien quiera controlarte<br>"
            "3. Espera a que se conecten<br>"
            "<br>"
            "<b>Nota:</b> El servidor debe ejecutarse como administrador para que funcione correctamente.<br>"
            "<br>"
            "<b>Conexión desde Internet:</b><br>"
            "Para permitir conexiones desde otras redes (Internet), necesitas configurar <b>Port Forwarding</b> "
            "en tu router. Lee el archivo <b>CONFIGURAR_PORT_FORWARDING.md</b> para instrucciones detalladas."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_client_tab(self):
        """Crea la pestaña del cliente"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Conexión
        connect_group = QGroupBox("Conectar a Otro Equipo")
        connect_layout = QHBoxLayout()
        
        connect_layout.addWidget(QLabel("Código o IP:"))
        
        self.connect_input = QLineEdit()
        self.connect_input.setPlaceholderText("ISR-12345678 o 192.168.1.100")
        self.connect_input.returnPressed.connect(self.connect_to_remote)
        connect_layout.addWidget(self.connect_input)
        
        connect_btn = QPushButton("🔗 Conectar")
        connect_btn.clicked.connect(self.connect_to_remote)
        connect_layout.addWidget(connect_btn)
        
        connect_group.setLayout(connect_layout)
        layout.addWidget(connect_group)
        
        # Conexiones activas
        self.connections_group = QGroupBox("Conexiones Activas")
        self.connections_layout = QVBoxLayout()
        
        no_connections_label = QLabel("No hay conexiones activas")
        no_connections_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.connections_layout.addWidget(no_connections_label)
        
        self.connections_group.setLayout(self.connections_layout)
        layout.addWidget(self.connections_group)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def init_tray(self):
        """Inicializa el icono de la bandeja del sistema"""
        self.tray_icon = QSystemTrayIcon(self)
        
        if os.path.exists('icon.ico'):
            self.tray_icon.setIcon(QIcon('icon.ico'))
        else:
            self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        
        # Menú
        tray_menu = QMenu()
        
        show_action = QAction("Mostrar", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Salir", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """Maneja la activación del icono de la bandeja"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.activateWindow()
    
    def load_settings(self):
        """Carga la configuración"""
        self.settings = {}
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    self.settings = json.load(f)
        except:
            pass
    
    def show_settings(self):
        """Muestra el diálogo de configuración"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog.save_settings()
            self.load_settings()
            QMessageBox.information(self, "Configuración", "Configuración guardada correctamente")
    
    def start_server(self):
        """Inicia el servidor"""
        if self.server_thread and self.server_thread.running:
            QMessageBox.warning(self, "Servidor", "El servidor ya está en ejecución")
            return
        
        port = self.settings.get('port', 5900)
        password = self.settings.get('password', '')
        monitor = self.settings.get('monitor', 1)
        
        self.server_thread = ServerThread(port, password, monitor)
        self.server_thread.log_signal.connect(self.add_server_log)
        self.server_thread.code_signal.connect(self.update_server_info)
        self.server_thread.error_signal.connect(self.show_server_error)
        self.server_thread.start()
        
        self.start_server_btn.setEnabled(False)
        self.stop_server_btn.setEnabled(True)
        self.status_label.setText("Servidor en ejecución")
    
    def stop_server(self):
        """Detiene el servidor"""
        if self.server_thread:
            self.server_thread.stop()
            # Esperar máximo 3 segundos para que el thread termine
            self.server_thread.wait(3000)  # 3000 ms = 3 segundos
            if self.server_thread.isRunning():
                # Si aún está corriendo, terminarlo forzosamente
                self.server_thread.terminate()
                self.server_thread.wait(1000)
            self.server_thread = None
        
        self.start_server_btn.setEnabled(True)
        self.stop_server_btn.setEnabled(False)
        self.code_label.setText("No iniciado")
        self.ip_label.setText("")
        self.status_label.setText("Servidor detenido")
        self.add_server_log("Servidor detenido")
    
    def add_server_log(self, message):
        """Agrega un mensaje al log del servidor"""
        self.server_log.append(message)
    
    def update_server_info(self, code, ip, port):
        """Actualiza la información del servidor"""
        self.code_label.setText(code)
        self.ip_label.setText(f"{ip}:{port}")
        self.current_code = code
    
    def show_server_error(self, error):
        """Muestra un error del servidor"""
        QMessageBox.critical(self, "Error del Servidor", error)
        self.stop_server()
    
    def copy_code(self):
        """Copia el código al portapapeles"""
        if hasattr(self, 'current_code'):
            QApplication.clipboard().setText(self.current_code)
            self.status_label.setText("Código copiado al portapapeles")
            QTimer.singleShot(3000, lambda: self.status_label.setText("Listo"))
    
    def connect_to_remote(self):
        """Conecta a un equipo remoto"""
        code_or_ip = self.connect_input.text().strip()
        if not code_or_ip:
            QMessageBox.warning(self, "Conectar", "Introduce un código o IP")
            return
        
        # Crear ventana de conexión
        try:
            from client import RemoteDesktopClient
            
            # Resolver código
            code_manager = get_code_manager()
            ip, port = code_manager.resolve_code(code_or_ip)
            
            # Crear cliente
            client_window = RemoteDesktopClient()
            client_window.show()
            
            # Conectar automáticamente
            QTimer.singleShot(500, lambda: client_window.connect_to(ip, port))
            
            self.status_label.setText(f"Conectando a {code_or_ip}...")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {str(e)}")
    
    def closeEvent(self, event):
        """Maneja el cierre de la ventana"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "ISR Remote Desktop",
            "La aplicación sigue ejecutándose en segundo plano",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def quit_application(self):
        """Cierra la aplicación completamente"""
        # Detener servidor si está en ejecución
        if self.server_thread:
            self.stop_server()
        
        # Cerrar todas las ventanas
        QApplication.quit()


def main():
    """Función principal"""
    # Ocultar consola en Windows
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    app = QApplication(sys.argv)
    app.setApplicationName("ISR Remote Desktop")
    app.setOrganizationName("ISR Comunicaciones")
    
    window = ISRRemoteDesktop()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
