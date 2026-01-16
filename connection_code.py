"""
Sistema de códigos de conexión tipo AnyDesk
Permite usar códigos en lugar de IPs para conectar
"""

import hashlib
import uuid
import socket
import json
import os
from typing import Optional, Tuple

class ConnectionCodeManager:
    """Gestiona los códigos de conexión"""
    
    def __init__(self, registry_file: str = "connection_registry.json"):
        self.registry_file = registry_file
        self.registry = self._load_registry()
    
    def _load_registry(self) -> dict:
        """Carga el registro de códigos"""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_registry(self):
        """Guarda el registro de códigos"""
        try:
            with open(self.registry_file, 'w') as f:
                json.dump(self.registry, f, indent=2)
        except Exception as e:
            print(f"[Error] No se pudo guardar el registro: {e}")
    
    def generate_code(self, custom_name: Optional[str] = None) -> str:
        """
        Genera un código único para este equipo
        
        Args:
            custom_name: Nombre personalizado opcional
            
        Returns:
            Código de conexión (ej: "ISR-12345678" o nombre personalizado)
        """
        if custom_name:
            # Usar nombre personalizado
            return custom_name
        
        # Generar código basado en ID de máquina
        try:
            # Obtener ID único de la máquina
            machine_id = str(uuid.getnode())
            
            # Crear hash
            hash_obj = hashlib.sha256(machine_id.encode())
            hash_hex = hash_obj.hexdigest()
            
            # Tomar los primeros 8 caracteres y convertir a número
            code_num = int(hash_hex[:8], 16) % 100000000
            
            # Formato: ISR-XXXXXXXX
            code = f"ISR-{code_num:08d}"
            
            return code
        except:
            # Fallback: código aleatorio
            import random
            code_num = random.randint(10000000, 99999999)
            return f"ISR-{code_num:08d}"
    
    def register_code(self, code: str, ip: str, port: int = 5900, name: Optional[str] = None):
        """
        Registra un código con su IP y puerto
        
        Args:
            code: Código de conexión
            ip: Dirección IP
            port: Puerto
            name: Nombre descriptivo opcional
        """
        self.registry[code] = {
            'ip': ip,
            'port': port,
            'name': name or code,
            'last_seen': self._get_timestamp()
        }
        self._save_registry()
    
    def resolve_code(self, code_or_ip: str) -> Tuple[str, int]:
        """
        Resuelve un código a IP y puerto, o devuelve la IP si ya es una IP
        
        Args:
            code_or_ip: Código de conexión o dirección IP
            
        Returns:
            Tupla (ip, puerto)
            
        Raises:
            ValueError: Si el código no existe
        """
        # Verificar si es una IP directa
        if self._is_ip(code_or_ip):
            # Es una IP, extraer puerto si existe
            if ':' in code_or_ip:
                ip, port_str = code_or_ip.rsplit(':', 1)
                return ip, int(port_str)
            return code_or_ip, 5900
        
        # Es un código, buscar en el registro
        if code_or_ip in self.registry:
            entry = self.registry[code_or_ip]
            return entry['ip'], entry['port']
        
        # Intentar buscar por nombre
        for code, entry in self.registry.items():
            if entry.get('name') == code_or_ip:
                return entry['ip'], entry['port']
        
        raise ValueError(f"Código no encontrado: {code_or_ip}")
    
    def get_local_ip(self) -> str:
        """Obtiene la IP local del equipo"""
        try:
            # Conectar a un servidor externo para obtener la IP local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def _is_ip(self, text: str) -> bool:
        """Verifica si el texto es una dirección IP"""
        # Verificar formato IP (simple)
        parts = text.split(':')[0].split('.')
        if len(parts) == 4:
            try:
                for part in parts:
                    num = int(part)
                    if num < 0 or num > 255:
                        return False
                return True
            except:
                return False
        return False
    
    def _get_timestamp(self) -> str:
        """Obtiene timestamp actual"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_all_codes(self) -> dict:
        """Obtiene todos los códigos registrados"""
        return self.registry.copy()
    
    def remove_code(self, code: str):
        """Elimina un código del registro"""
        if code in self.registry:
            del self.registry[code]
            self._save_registry()
    
    def update_code_ip(self, code: str, new_ip: str):
        """Actualiza la IP de un código existente"""
        if code in self.registry:
            self.registry[code]['ip'] = new_ip
            self.registry[code]['last_seen'] = self._get_timestamp()
            self._save_registry()


# Instancia global
_code_manager = None

def get_code_manager() -> ConnectionCodeManager:
    """Obtiene la instancia global del gestor de códigos"""
    global _code_manager
    if _code_manager is None:
        _code_manager = ConnectionCodeManager()
    return _code_manager
