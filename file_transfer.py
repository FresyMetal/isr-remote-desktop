"""
Módulo de transferencia de archivos bidireccional
Soporta transferencias simultáneas y reanudación
"""

import os
import hashlib
import threading
from typing import Optional, Callable, Dict
from dataclasses import dataclass
from enum import Enum

from protocol import (
    Protocol, MessageType,
    encode_file_metadata, decode_file_metadata,
    encode_file_chunk, decode_file_chunk
)


class TransferDirection(Enum):
    """Dirección de la transferencia"""
    UPLOAD = "upload"
    DOWNLOAD = "download"


class TransferStatus(Enum):
    """Estado de la transferencia"""
    PENDING = "pending"
    TRANSFERRING = "transferring"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class FileTransfer:
    """Información de una transferencia de archivo"""
    file_id: int
    filename: str
    filepath: str
    filesize: int
    direction: TransferDirection
    status: TransferStatus = TransferStatus.PENDING
    transferred: int = 0
    chunks_sent: int = 0
    total_chunks: int = 0
    checksum: str = ""
    error: str = ""


class FileTransferManager:
    """Gestor de transferencias de archivos"""
    
    CHUNK_SIZE = 64 * 1024  # 64 KB por chunk
    
    def __init__(self, protocol: Protocol, send_callback: Callable[[bytes], None]):
        """
        Inicializa el gestor
        
        Args:
            protocol: Instancia del protocolo
            send_callback: Función para enviar datos por la red
        """
        self.protocol = protocol
        self.send_callback = send_callback
        
        self.transfers: Dict[int, FileTransfer] = {}
        self.file_id_counter = 0
        self.lock = threading.Lock()
        
        # Callbacks para eventos
        self.on_progress: Optional[Callable[[int, float], None]] = None
        self.on_complete: Optional[Callable[[int], None]] = None
        self.on_error: Optional[Callable[[int, str], None]] = None
    
    def send_file(self, filepath: str) -> Optional[int]:
        """
        Inicia el envío de un archivo
        
        Args:
            filepath: Ruta del archivo a enviar
            
        Returns:
            ID de la transferencia o None si hay error
        """
        if not os.path.exists(filepath):
            print(f"[FileTransfer] Archivo no existe: {filepath}")
            return None
        
        if not os.path.isfile(filepath):
            print(f"[FileTransfer] No es un archivo: {filepath}")
            return None
        
        # Obtener información del archivo
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        
        # Calcular checksum
        checksum = self._calculate_checksum(filepath)
        
        # Crear transferencia
        with self.lock:
            file_id = self.file_id_counter
            self.file_id_counter += 1
            
            total_chunks = (filesize + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE
            
            transfer = FileTransfer(
                file_id=file_id,
                filename=filename,
                filepath=filepath,
                filesize=filesize,
                direction=TransferDirection.UPLOAD,
                status=TransferStatus.PENDING,
                total_chunks=total_chunks,
                checksum=checksum
            )
            
            self.transfers[file_id] = transfer
        
        # Enviar metadatos
        try:
            payload = encode_file_metadata(filename, filesize, file_id)
            message = self.protocol.encode_message(MessageType.FILE_METADATA, payload)
            self.send_callback(message)
            
            # Iniciar thread de envío
            transfer.status = TransferStatus.TRANSFERRING
            thread = threading.Thread(
                target=self._send_file_chunks,
                args=(file_id,),
                daemon=True
            )
            thread.start()
            
            return file_id
            
        except Exception as e:
            print(f"[FileTransfer] Error al enviar metadatos: {e}")
            transfer.status = TransferStatus.FAILED
            transfer.error = str(e)
            if self.on_error:
                self.on_error(file_id, str(e))
            return None
    
    def _send_file_chunks(self, file_id: int):
        """
        Envía los chunks de un archivo
        
        Args:
            file_id: ID de la transferencia
        """
        transfer = self.transfers.get(file_id)
        if not transfer:
            return
        
        try:
            with open(transfer.filepath, 'rb') as f:
                chunk_num = 0
                
                while True:
                    # Leer chunk
                    data = f.read(self.CHUNK_SIZE)
                    if not data:
                        break
                    
                    # Enviar chunk
                    payload = encode_file_chunk(file_id, chunk_num, data)
                    message = self.protocol.encode_message(
                        MessageType.FILE_CHUNK,
                        payload,
                        compress=True
                    )
                    self.send_callback(message)
                    
                    # Actualizar progreso
                    transfer.transferred += len(data)
                    transfer.chunks_sent += 1
                    chunk_num += 1
                    
                    if self.on_progress:
                        progress = transfer.transferred / transfer.filesize
                        self.on_progress(file_id, progress)
            
            # Enviar mensaje de completado
            payload = encode_file_metadata(transfer.filename, transfer.filesize, file_id)
            message = self.protocol.encode_message(MessageType.FILE_COMPLETE, payload)
            self.send_callback(message)
            
            transfer.status = TransferStatus.COMPLETED
            if self.on_complete:
                self.on_complete(file_id)
            
            print(f"[FileTransfer] Archivo enviado: {transfer.filename}")
            
        except Exception as e:
            print(f"[FileTransfer] Error al enviar archivo: {e}")
            transfer.status = TransferStatus.FAILED
            transfer.error = str(e)
            if self.on_error:
                self.on_error(file_id, str(e))
    
    def receive_file_metadata(self, file_id: int, filesize: int, filename: str, save_dir: str):
        """
        Inicia la recepción de un archivo
        
        Args:
            file_id: ID del archivo
            filesize: Tamaño del archivo
            filename: Nombre del archivo
            save_dir: Directorio donde guardar el archivo
        """
        # Crear ruta completa
        filepath = os.path.join(save_dir, filename)
        
        # Verificar si el archivo ya existe
        if os.path.exists(filepath):
            # Agregar sufijo numérico
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(filepath):
                filename = f"{base}_{counter}{ext}"
                filepath = os.path.join(save_dir, filename)
                counter += 1
        
        # Crear transferencia
        with self.lock:
            total_chunks = (filesize + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE
            
            transfer = FileTransfer(
                file_id=file_id,
                filename=filename,
                filepath=filepath,
                filesize=filesize,
                direction=TransferDirection.DOWNLOAD,
                status=TransferStatus.TRANSFERRING,
                total_chunks=total_chunks
            )
            
            self.transfers[file_id] = transfer
        
        print(f"[FileTransfer] Recibiendo archivo: {filename} ({filesize} bytes)")
    
    def receive_file_chunk(self, file_id: int, chunk_num: int, data: bytes):
        """
        Recibe un chunk de archivo
        
        Args:
            file_id: ID del archivo
            chunk_num: Número del chunk
            data: Datos del chunk
        """
        transfer = self.transfers.get(file_id)
        if not transfer:
            print(f"[FileTransfer] Chunk recibido para transferencia desconocida: {file_id}")
            return
        
        try:
            # Escribir chunk al archivo
            mode = 'ab' if chunk_num > 0 else 'wb'
            with open(transfer.filepath, mode) as f:
                f.write(data)
            
            # Actualizar progreso
            transfer.transferred += len(data)
            transfer.chunks_sent += 1
            
            if self.on_progress:
                progress = transfer.transferred / transfer.filesize
                self.on_progress(file_id, progress)
            
            # Verificar si se completó
            if transfer.transferred >= transfer.filesize:
                self._complete_file_reception(file_id)
            
        except Exception as e:
            print(f"[FileTransfer] Error al recibir chunk: {e}")
            transfer.status = TransferStatus.FAILED
            transfer.error = str(e)
            if self.on_error:
                self.on_error(file_id, str(e))
    
    def _complete_file_reception(self, file_id: int):
        """
        Completa la recepción de un archivo
        
        Args:
            file_id: ID de la transferencia
        """
        transfer = self.transfers.get(file_id)
        if not transfer:
            return
        
        # Verificar checksum si está disponible
        if transfer.checksum:
            actual_checksum = self._calculate_checksum(transfer.filepath)
            if actual_checksum != transfer.checksum:
                print(f"[FileTransfer] Checksum no coincide para {transfer.filename}")
                transfer.status = TransferStatus.FAILED
                transfer.error = "Checksum mismatch"
                if self.on_error:
                    self.on_error(file_id, "Checksum mismatch")
                return
        
        transfer.status = TransferStatus.COMPLETED
        if self.on_complete:
            self.on_complete(file_id)
        
        print(f"[FileTransfer] Archivo recibido: {transfer.filename}")
    
    def cancel_transfer(self, file_id: int):
        """
        Cancela una transferencia
        
        Args:
            file_id: ID de la transferencia
        """
        transfer = self.transfers.get(file_id)
        if not transfer:
            return
        
        transfer.status = TransferStatus.CANCELLED
        
        # Si es descarga, eliminar archivo parcial
        if transfer.direction == TransferDirection.DOWNLOAD:
            try:
                if os.path.exists(transfer.filepath):
                    os.remove(transfer.filepath)
            except:
                pass
        
        print(f"[FileTransfer] Transferencia cancelada: {transfer.filename}")
    
    def get_transfer(self, file_id: int) -> Optional[FileTransfer]:
        """
        Obtiene información de una transferencia
        
        Args:
            file_id: ID de la transferencia
            
        Returns:
            Información de la transferencia o None
        """
        return self.transfers.get(file_id)
    
    def get_all_transfers(self) -> Dict[int, FileTransfer]:
        """
        Obtiene todas las transferencias
        
        Returns:
            Diccionario de transferencias
        """
        return self.transfers.copy()
    
    def get_active_transfers(self) -> Dict[int, FileTransfer]:
        """
        Obtiene las transferencias activas
        
        Returns:
            Diccionario de transferencias activas
        """
        return {
            fid: t for fid, t in self.transfers.items()
            if t.status == TransferStatus.TRANSFERRING
        }
    
    def _calculate_checksum(self, filepath: str) -> str:
        """
        Calcula el checksum SHA256 de un archivo
        
        Args:
            filepath: Ruta del archivo
            
        Returns:
            Checksum en hexadecimal
        """
        sha256 = hashlib.sha256()
        
        try:
            with open(filepath, 'rb') as f:
                while True:
                    data = f.read(self.CHUNK_SIZE)
                    if not data:
                        break
                    sha256.update(data)
            
            return sha256.hexdigest()
            
        except Exception as e:
            print(f"[FileTransfer] Error al calcular checksum: {e}")
            return ""


class ClipboardManager:
    """Gestor del portapapeles compartido"""
    
    def __init__(self, protocol: Protocol, send_callback: Callable[[bytes], None]):
        """
        Inicializa el gestor
        
        Args:
            protocol: Instancia del protocolo
            send_callback: Función para enviar datos por la red
        """
        self.protocol = protocol
        self.send_callback = send_callback
        
        self.last_sent = ""
        self.last_received = ""
        
        # Callbacks
        self.on_clipboard_received: Optional[Callable[[str], None]] = None
    
    def send_clipboard(self, text: str):
        """
        Envía el contenido del portapapeles
        
        Args:
            text: Texto a enviar
        """
        if text == self.last_sent:
            return  # No enviar si es el mismo contenido
        
        try:
            from protocol import encode_clipboard_text
            
            payload = encode_clipboard_text(text)
            message = self.protocol.encode_message(
                MessageType.CLIPBOARD_TEXT,
                payload,
                compress=True
            )
            self.send_callback(message)
            
            self.last_sent = text
            print(f"[Clipboard] Enviado: {len(text)} caracteres")
            
        except Exception as e:
            print(f"[Clipboard] Error al enviar: {e}")
    
    def receive_clipboard(self, text: str):
        """
        Recibe contenido del portapapeles
        
        Args:
            text: Texto recibido
        """
        if text == self.last_received:
            return  # Ignorar duplicados
        
        self.last_received = text
        
        if self.on_clipboard_received:
            self.on_clipboard_received(text)
        
        print(f"[Clipboard] Recibido: {len(text)} caracteres")
    
    def monitor_local_clipboard(self, get_clipboard_func: Callable[[], str]):
        """
        Monitorea el portapapeles local y envía cambios
        
        Args:
            get_clipboard_func: Función para obtener el contenido del portapapeles
        """
        import time
        
        while True:
            try:
                current = get_clipboard_func()
                if current and current != self.last_sent:
                    self.send_clipboard(current)
                
                time.sleep(0.5)  # Verificar cada 500ms
                
            except Exception as e:
                print(f"[Clipboard] Error en monitoreo: {e}")
                time.sleep(1)
