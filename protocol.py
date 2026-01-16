"""
Protocolo de comunicación para escritorio remoto
Basado en RFB pero optimizado para nuestras necesidades
"""

import struct
from enum import IntEnum
from typing import Optional, Tuple
import zstandard as zstd

# Magic number para identificar nuestro protocolo
MAGIC_NUMBER = 0x5244  # "RD" = Remote Desktop

class MessageType(IntEnum):
    """Tipos de mensajes del protocolo"""
    # Handshake y autenticación
    HANDSHAKE = 0x01
    AUTH_REQUEST = 0x02
    AUTH_RESPONSE = 0x03
    
    # Video/pantalla
    VIDEO_FRAME = 0x10
    VIDEO_REQUEST = 0x11
    VIDEO_CONFIG = 0x12
    
    # Entrada
    INPUT_MOUSE = 0x20
    INPUT_KEYBOARD = 0x21
    INPUT_SCROLL = 0x22
    
    # Transferencia de archivos
    FILE_METADATA = 0x30
    FILE_CHUNK = 0x31
    FILE_COMPLETE = 0x32
    FILE_ERROR = 0x33
    
    # Portapapeles
    CLIPBOARD_TEXT = 0x40
    CLIPBOARD_IMAGE = 0x41
    
    # Control
    PING = 0xF0
    PONG = 0xF1
    DISCONNECT = 0xF2
    ERROR = 0xFF

class MessageFlags(IntEnum):
    """Flags para los mensajes"""
    NONE = 0x00
    COMPRESSED = 0x01
    ENCRYPTED = 0x02
    PRIORITY = 0x04

class Protocol:
    """Clase para codificar/decodificar mensajes del protocolo"""
    
    HEADER_SIZE = 12  # bytes
    MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
    
    def __init__(self, compression_level: int = 3):
        """
        Inicializa el protocolo
        
        Args:
            compression_level: Nivel de compresión zstd (1-22)
        """
        self.compression_level = compression_level
        self.compressor = zstd.ZstdCompressor(level=compression_level)
        self.decompressor = zstd.ZstdDecompressor()
        self.sequence_number = 0
    
    def encode_message(
        self, 
        msg_type: MessageType, 
        payload: bytes,
        compress: bool = False,
        encrypt: bool = False,
        priority: bool = False
    ) -> bytes:
        """
        Codifica un mensaje con header + payload
        
        Args:
            msg_type: Tipo de mensaje
            payload: Datos del mensaje
            compress: Si se debe comprimir el payload
            encrypt: Si se debe cifrar el payload (no implementado aún)
            priority: Si el mensaje tiene prioridad
            
        Returns:
            Mensaje completo codificado
        """
        # Aplicar compresión si se solicita
        flags = MessageFlags.NONE
        if compress and len(payload) > 1024:  # Solo comprimir si > 1KB
            try:
                compressed = self.compressor.compress(payload)
                if len(compressed) < len(payload):  # Solo usar si reduce tamaño
                    payload = compressed
                    flags |= MessageFlags.COMPRESSED
            except Exception:
                pass  # Si falla la compresión, usar sin comprimir
        
        if encrypt:
            flags |= MessageFlags.ENCRYPTED
            # TODO: Implementar cifrado
        
        if priority:
            flags |= MessageFlags.PRIORITY
        
        # Construir header
        header = struct.pack(
            '!HBBII',  # Network byte order (big-endian)
            MAGIC_NUMBER,           # 2 bytes: magic number
            msg_type,               # 1 byte: tipo de mensaje
            flags,                  # 1 byte: flags
            len(payload),           # 4 bytes: longitud del payload
            self.sequence_number    # 4 bytes: número de secuencia
        )
        
        self.sequence_number = (self.sequence_number + 1) % 0xFFFFFFFF
        
        return header + payload
    
    def decode_header(self, header_bytes: bytes) -> Optional[Tuple[int, int, int, int, int]]:
        """
        Decodifica el header de un mensaje
        
        Args:
            header_bytes: Bytes del header (12 bytes)
            
        Returns:
            Tupla (magic, msg_type, flags, payload_len, seq_num) o None si inválido
        """
        if len(header_bytes) != self.HEADER_SIZE:
            return None
        
        try:
            magic, msg_type, flags, payload_len, seq_num = struct.unpack(
                '!HBBII', header_bytes
            )
            
            # Verificar magic number
            if magic != MAGIC_NUMBER:
                return None
            
            # Verificar tamaño del payload
            if payload_len > self.MAX_PAYLOAD_SIZE:
                return None
            
            return (magic, msg_type, flags, payload_len, seq_num)
        except struct.error:
            return None
    
    def decode_payload(self, payload: bytes, flags: int) -> bytes:
        """
        Decodifica el payload según los flags
        
        Args:
            payload: Datos del payload
            flags: Flags del mensaje
            
        Returns:
            Payload decodificado
        """
        # Descomprimir si está comprimido
        if flags & MessageFlags.COMPRESSED:
            try:
                payload = self.decompressor.decompress(payload)
            except Exception as e:
                raise ValueError(f"Error al descomprimir: {e}")
        
        # Descifrar si está cifrado
        if flags & MessageFlags.ENCRYPTED:
            # TODO: Implementar descifrado
            pass
        
        return payload
    
    def adjust_compression_level(self, latency_ms: float):
        """
        Ajusta el nivel de compresión según la latencia
        
        Args:
            latency_ms: Latencia en milisegundos
        """
        if latency_ms < 20:  # LAN
            level = 1  # Compresión mínima, priorizar velocidad
        elif latency_ms < 100:  # WAN
            level = 5  # Balance
        else:  # Internet lento
            level = 9  # Máxima compresión
        
        if level != self.compression_level:
            self.compression_level = level
            self.compressor = zstd.ZstdCompressor(level=level)


# Funciones auxiliares para codificar payloads específicos

def encode_handshake(version: int = 1, capabilities: int = 0) -> bytes:
    """Codifica un mensaje de handshake"""
    return struct.pack('!II', version, capabilities)

def decode_handshake(payload: bytes) -> Tuple[int, int]:
    """Decodifica un mensaje de handshake"""
    return struct.unpack('!II', payload)

def encode_auth_request(password: str) -> bytes:
    """Codifica una solicitud de autenticación"""
    password_bytes = password.encode('utf-8')
    return struct.pack('!I', len(password_bytes)) + password_bytes

def decode_auth_request(payload: bytes) -> str:
    """Decodifica una solicitud de autenticación"""
    length = struct.unpack('!I', payload[:4])[0]
    return payload[4:4+length].decode('utf-8')

def encode_auth_response(success: bool, message: str = "") -> bytes:
    """Codifica una respuesta de autenticación"""
    msg_bytes = message.encode('utf-8')
    return struct.pack('!?I', success, len(msg_bytes)) + msg_bytes

def decode_auth_response(payload: bytes) -> Tuple[bool, str]:
    """Decodifica una respuesta de autenticación"""
    success = struct.unpack('!?', payload[:1])[0]
    length = struct.unpack('!I', payload[1:5])[0]
    message = payload[5:5+length].decode('utf-8')
    return success, message

def encode_video_frame(
    x: int, y: int, width: int, height: int, 
    frame_data: bytes, encoding: int = 0
) -> bytes:
    """
    Codifica un frame de video
    
    Args:
        x, y: Posición del rectángulo
        width, height: Dimensiones del rectángulo
        frame_data: Datos de la imagen (RGB)
        encoding: Tipo de codificación (0=raw, 1=jpeg, etc.)
    """
    header = struct.pack('!HHHHBI', x, y, width, height, encoding, len(frame_data))
    return header + frame_data

def decode_video_frame(payload: bytes) -> Tuple[int, int, int, int, int, bytes]:
    """Decodifica un frame de video"""
    x, y, width, height, encoding, data_len = struct.unpack('!HHHHBI', payload[:13])
    frame_data = payload[13:13+data_len]
    return x, y, width, height, encoding, frame_data

def encode_mouse_event(x: int, y: int, buttons: int) -> bytes:
    """
    Codifica un evento de ratón
    
    Args:
        x, y: Posición del ratón
        buttons: Botones presionados (bit 0=izq, 1=der, 2=medio)
    """
    return struct.pack('!HHB', x, y, buttons)

def decode_mouse_event(payload: bytes) -> Tuple[int, int, int]:
    """Decodifica un evento de ratón"""
    return struct.unpack('!HHB', payload)

def encode_keyboard_event(key_code: int, pressed: bool) -> bytes:
    """
    Codifica un evento de teclado
    
    Args:
        key_code: Código de la tecla
        pressed: True si se presionó, False si se soltó
    """
    return struct.pack('!I?', key_code, pressed)

def decode_keyboard_event(payload: bytes) -> Tuple[int, bool]:
    """Decodifica un evento de teclado"""
    return struct.unpack('!I?', payload)

def encode_clipboard_text(text: str) -> bytes:
    """Codifica texto del portapapeles"""
    text_bytes = text.encode('utf-8')
    return struct.pack('!I', len(text_bytes)) + text_bytes

def decode_clipboard_text(payload: bytes) -> str:
    """Decodifica texto del portapapeles"""
    length = struct.unpack('!I', payload[:4])[0]
    return payload[4:4+length].decode('utf-8')

def encode_file_metadata(filename: str, filesize: int, file_id: int) -> bytes:
    """Codifica metadatos de un archivo"""
    filename_bytes = filename.encode('utf-8')
    return struct.pack('!IQI', file_id, filesize, len(filename_bytes)) + filename_bytes

def decode_file_metadata(payload: bytes) -> Tuple[int, int, str]:
    """Decodifica metadatos de un archivo"""
    file_id, filesize, name_len = struct.unpack('!IQI', payload[:16])
    filename = payload[16:16+name_len].decode('utf-8')
    return file_id, filesize, filename

def encode_file_chunk(file_id: int, chunk_num: int, data: bytes) -> bytes:
    """Codifica un chunk de archivo"""
    return struct.pack('!III', file_id, chunk_num, len(data)) + data

def decode_file_chunk(payload: bytes) -> Tuple[int, int, bytes]:
    """Decodifica un chunk de archivo"""
    file_id, chunk_num, data_len = struct.unpack('!III', payload[:12])
    data = payload[12:12+data_len]
    return file_id, chunk_num, data
