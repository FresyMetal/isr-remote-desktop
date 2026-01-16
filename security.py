"""
Módulo de seguridad y cifrado
Implementa cifrado AES-256-GCM y autenticación simple con PSK
"""

import os
import hashlib
import hmac
from typing import Optional, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class CryptoManager:
    """Gestor de cifrado y descifrado"""
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Inicializa el gestor de cifrado
        
        Args:
            key: Clave de 32 bytes para AES-256. Si es None, se genera una nueva.
        """
        if key is None:
            key = AESGCM.generate_key(bit_length=256)
        elif len(key) != 32:
            raise ValueError("La clave debe tener 32 bytes para AES-256")
        
        self.key = key
        self.aesgcm = AESGCM(key)
    
    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Cifra datos usando AES-256-GCM
        
        Args:
            plaintext: Datos a cifrar
            
        Returns:
            Nonce (12 bytes) + ciphertext + tag (16 bytes)
        """
        # Generar nonce aleatorio de 12 bytes
        nonce = os.urandom(12)
        
        # Cifrar
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, None)
        
        # Retornar nonce + ciphertext (que incluye el tag)
        return nonce + ciphertext
    
    def decrypt(self, encrypted: bytes) -> bytes:
        """
        Descifra datos usando AES-256-GCM
        
        Args:
            encrypted: Nonce + ciphertext + tag
            
        Returns:
            Datos descifrados
            
        Raises:
            ValueError: Si la autenticación falla
        """
        if len(encrypted) < 28:  # 12 (nonce) + 16 (tag mínimo)
            raise ValueError("Datos cifrados demasiado cortos")
        
        # Extraer nonce y ciphertext
        nonce = encrypted[:12]
        ciphertext = encrypted[12:]
        
        # Descifrar y verificar
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        
        return plaintext
    
    @staticmethod
    def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Deriva una clave de 32 bytes a partir de una contraseña usando PBKDF2
        
        Args:
            password: Contraseña
            salt: Salt de 16 bytes. Si es None, se genera uno nuevo.
            
        Returns:
            Tupla (clave, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        elif len(salt) != 16:
            raise ValueError("El salt debe tener 16 bytes")
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode('utf-8'))
        
        return key, salt
    
    def get_key(self) -> bytes:
        """Obtiene la clave actual"""
        return self.key


class AuthenticationManager:
    """Gestor de autenticación simple con PSK (Pre-Shared Key)"""
    
    def __init__(self, password: str = ""):
        """
        Inicializa el gestor de autenticación
        
        Args:
            password: Contraseña pre-compartida (vacío = sin autenticación)
        """
        self.password = password
        self.enabled = bool(password)
        
        # Generar salt para derivación de clave
        self.salt = os.urandom(16)
        
        if self.enabled:
            # Derivar hash de la contraseña
            self.password_hash = self._hash_password(password, self.salt)
    
    def verify_password(self, password: str) -> bool:
        """
        Verifica una contraseña
        
        Args:
            password: Contraseña a verificar
            
        Returns:
            True si la contraseña es correcta
        """
        if not self.enabled:
            return True  # Sin autenticación
        
        password_hash = self._hash_password(password, self.salt)
        return hmac.compare_digest(password_hash, self.password_hash)
    
    def _hash_password(self, password: str, salt: bytes) -> bytes:
        """
        Genera un hash de la contraseña
        
        Args:
            password: Contraseña
            salt: Salt
            
        Returns:
            Hash de la contraseña
        """
        return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    
    def get_salt(self) -> bytes:
        """Obtiene el salt"""
        return self.salt
    
    def is_enabled(self) -> bool:
        """Verifica si la autenticación está habilitada"""
        return self.enabled


class SecureConnection:
    """Conexión segura con cifrado y autenticación"""
    
    def __init__(self, password: str = "", enable_encryption: bool = True):
        """
        Inicializa una conexión segura
        
        Args:
            password: Contraseña para autenticación (vacío = sin auth)
            enable_encryption: Si se debe habilitar el cifrado
        """
        self.auth = AuthenticationManager(password)
        self.crypto: Optional[CryptoManager] = None
        self.enable_encryption = enable_encryption
        self.encryption_ready = False
    
    def setup_encryption(self, password: str = ""):
        """
        Configura el cifrado derivando una clave de la contraseña
        
        Args:
            password: Contraseña para derivar la clave (vacío = clave aleatoria)
        """
        if not self.enable_encryption:
            return
        
        if password:
            # Derivar clave de la contraseña
            key, salt = CryptoManager.derive_key_from_password(password)
            self.crypto = CryptoManager(key)
        else:
            # Generar clave aleatoria
            self.crypto = CryptoManager()
        
        self.encryption_ready = True
    
    def encrypt_data(self, data: bytes) -> bytes:
        """
        Cifra datos si el cifrado está habilitado
        
        Args:
            data: Datos a cifrar
            
        Returns:
            Datos cifrados o sin cifrar según la configuración
        """
        if self.encryption_ready and self.crypto:
            return self.crypto.encrypt(data)
        return data
    
    def decrypt_data(self, data: bytes) -> bytes:
        """
        Descifra datos si el cifrado está habilitado
        
        Args:
            data: Datos a descifrar
            
        Returns:
            Datos descifrados o sin descifrar según la configuración
        """
        if self.encryption_ready and self.crypto:
            return self.crypto.decrypt(data)
        return data
    
    def authenticate(self, password: str) -> bool:
        """
        Autentica con una contraseña
        
        Args:
            password: Contraseña
            
        Returns:
            True si la autenticación fue exitosa
        """
        return self.auth.verify_password(password)
    
    def is_encryption_enabled(self) -> bool:
        """Verifica si el cifrado está habilitado"""
        return self.encryption_ready
    
    def is_authentication_enabled(self) -> bool:
        """Verifica si la autenticación está habilitada"""
        return self.auth.is_enabled()


class RateLimiter:
    """Limitador de tasa para prevenir ataques"""
    
    def __init__(self, max_requests: int = 100, time_window: float = 1.0):
        """
        Inicializa el limitador
        
        Args:
            max_requests: Número máximo de solicitudes
            time_window: Ventana de tiempo en segundos
        """
        self.max_requests = max_requests
        self.time_window = time_window
        
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Verifica si se permite una solicitud
        
        Args:
            identifier: Identificador del cliente (ej: IP)
            
        Returns:
            True si se permite la solicitud
        """
        import time
        
        current_time = time.time()
        
        # Obtener lista de timestamps para este identificador
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        timestamps = self.requests[identifier]
        
        # Eliminar timestamps antiguos
        timestamps[:] = [t for t in timestamps if current_time - t < self.time_window]
        
        # Verificar si se excede el límite
        if len(timestamps) >= self.max_requests:
            return False
        
        # Agregar timestamp actual
        timestamps.append(current_time)
        
        return True
    
    def reset(self, identifier: str):
        """
        Resetea el contador para un identificador
        
        Args:
            identifier: Identificador del cliente
        """
        if identifier in self.requests:
            del self.requests[identifier]


class IPWhitelist:
    """Lista blanca de IPs permitidas"""
    
    def __init__(self, enabled: bool = False):
        """
        Inicializa la whitelist
        
        Args:
            enabled: Si la whitelist está habilitada
        """
        self.enabled = enabled
        self.allowed_ips: set = set()
        
        # Por defecto, permitir localhost
        if enabled:
            self.allowed_ips.add('127.0.0.1')
            self.allowed_ips.add('::1')
    
    def add_ip(self, ip: str):
        """
        Agrega una IP a la whitelist
        
        Args:
            ip: Dirección IP
        """
        self.allowed_ips.add(ip)
    
    def remove_ip(self, ip: str):
        """
        Elimina una IP de la whitelist
        
        Args:
            ip: Dirección IP
        """
        if ip in self.allowed_ips:
            self.allowed_ips.remove(ip)
    
    def is_allowed(self, ip: str) -> bool:
        """
        Verifica si una IP está permitida
        
        Args:
            ip: Dirección IP
            
        Returns:
            True si está permitida o si la whitelist está deshabilitada
        """
        if not self.enabled:
            return True
        
        return ip in self.allowed_ips
    
    def enable(self):
        """Habilita la whitelist"""
        self.enabled = True
    
    def disable(self):
        """Deshabilita la whitelist"""
        self.enabled = False
    
    def get_allowed_ips(self) -> set:
        """Obtiene las IPs permitidas"""
        return self.allowed_ips.copy()


# Funciones auxiliares

def generate_random_password(length: int = 16) -> str:
    """
    Genera una contraseña aleatoria segura
    
    Args:
        length: Longitud de la contraseña
        
    Returns:
        Contraseña aleatoria
    """
    import string
    import secrets
    
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    return password


def hash_data(data: bytes) -> str:
    """
    Calcula el hash SHA-256 de datos
    
    Args:
        data: Datos a hashear
        
    Returns:
        Hash en hexadecimal
    """
    return hashlib.sha256(data).hexdigest()


def verify_hash(data: bytes, expected_hash: str) -> bool:
    """
    Verifica el hash de datos
    
    Args:
        data: Datos
        expected_hash: Hash esperado en hexadecimal
        
    Returns:
        True si el hash coincide
    """
    actual_hash = hash_data(data)
    return hmac.compare_digest(actual_hash, expected_hash)


# Ejemplo de uso
if __name__ == '__main__':
    # Cifrado
    print("=== Prueba de Cifrado ===")
    crypto = CryptoManager()
    plaintext = b"Hola, este es un mensaje secreto!"
    print(f"Texto plano: {plaintext}")
    
    encrypted = crypto.encrypt(plaintext)
    print(f"Cifrado: {encrypted.hex()}")
    
    decrypted = crypto.decrypt(encrypted)
    print(f"Descifrado: {decrypted}")
    print(f"Coincide: {plaintext == decrypted}")
    
    # Derivación de clave
    print("\n=== Derivación de Clave ===")
    password = "mi_contraseña_segura"
    key, salt = CryptoManager.derive_key_from_password(password)
    print(f"Clave derivada: {key.hex()}")
    print(f"Salt: {salt.hex()}")
    
    # Autenticación
    print("\n=== Autenticación ===")
    auth = AuthenticationManager("password123")
    print(f"Contraseña correcta: {auth.verify_password('password123')}")
    print(f"Contraseña incorrecta: {auth.verify_password('wrong')}")
    
    # Rate limiting
    print("\n=== Rate Limiting ===")
    limiter = RateLimiter(max_requests=5, time_window=1.0)
    client_ip = "192.168.1.100"
    
    for i in range(7):
        allowed = limiter.is_allowed(client_ip)
        print(f"Solicitud {i+1}: {'Permitida' if allowed else 'Bloqueada'}")
    
    print("\n¡Todas las pruebas completadas!")
