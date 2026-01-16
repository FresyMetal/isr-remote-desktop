"""
Sistema de códigos de conexión tipo AnyDesk
Permite usar códigos en lugar de IPs para conectar
Con soporte para servidor de registro central
"""

import hashlib
import uuid
import socket
import json
import os
import urllib.request
import urllib.parse
import urllib.error
from typing import Tuple, Optional


class ConnectionCodeManager:
    """Gestiona los códigos de conexión"""
    
    def __init__(self, registry_file: str = "connection_registry.json", 
                 registry_server: str = "http://77.225.201.4:8080"):
        self.registry_file = registry_file
        self.registry_server = registry_server
        self.use_central_server = True  # Usar servidor central por defecto
        self.registry = self._load_registry()
    
    def _load_registry(self) -> dict:
        """Carga el registro de códigos local"""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_registry(self):
        """Guarda el registro de códigos local"""
        try:
            with open(self.registry_file, 'w') as f:
                json.dump(self.registry, f, indent=2)
        except Exception as e:
            print(f"[Error] No se pudo guardar el registro local: {e}")
    
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
        Intenta registrar en el servidor central primero, luego localmente
        
        Args:
            code: Código de conexión
            ip: Dirección IP
            port: Puerto
            name: Nombre descriptivo opcional
        """
        # Intentar registrar en el servidor central
        if self.use_central_server:
            try:
                self._register_on_server(code, ip, port, name)
                print(f"[Registro] Código {code} registrado en servidor central")
            except Exception as e:
                print(f"[Advertencia] No se pudo registrar en servidor central: {e}")
                print(f"[Registro] Usando registro local")
        
        # Registrar localmente también (backup)
        self.registry[code] = {
            'ip': ip,
            'port': port,
            'name': name or code,
            'last_seen': self._get_timestamp()
        }
        self._save_registry()
    
    def _register_on_server(self, code: str, ip: str, port: int, name: Optional[str] = None):
        """Registra un código en el servidor central"""
        params = {
            'code': code,
            'host': ip,
            'port': str(port),
            'name': name or code
        }
        
        url = f"{self.registry_server}/register?{urllib.parse.urlencode(params)}"
        
        req = urllib.request.Request(url, method='POST')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if not data.get('success'):
                raise Exception(data.get('error', 'Error desconocido'))
    
    def resolve_code(self, code_or_ip: str) -> Tuple[str, int]:
        """
        Resuelve un código a IP y puerto, o devuelve la IP si ya es una IP
        Intenta resolver desde el servidor central primero, luego localmente
        
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
        
        # Es un código, intentar resolver desde el servidor central
        if self.use_central_server:
            try:
                ip, port = self._resolve_from_server(code_or_ip)
                if ip:
                    print(f"[Resolución] Código {code_or_ip} resuelto desde servidor central")
                    return ip, port
            except Exception as e:
                print(f"[Advertencia] No se pudo resolver desde servidor central: {e}")
                print(f"[Resolución] Intentando resolución local")
        
        # Buscar en el registro local
        if code_or_ip in self.registry:
            entry = self.registry[code_or_ip]
            return entry['ip'], entry['port']
        
        # Intentar buscar por nombre
        for code, entry in self.registry.items():
            if entry.get('name') == code_or_ip:
                return entry['ip'], entry['port']
        
        raise ValueError(f"Código no encontrado: {code_or_ip}")
    
    def _resolve_from_server(self, code: str) -> Tuple[Optional[str], Optional[int]]:
        """Resuelve un código desde el servidor central"""
        params = {'code': code}
        url = f"{self.registry_server}/resolve?{urllib.parse.urlencode(params)}"
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data.get('success'):
                return data.get('host'), data.get('port')
            return None, None
    
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
    
    def get_public_ip(self) -> str:
        """Obtiene la IP pública del equipo"""
        try:
            # Intentar obtener IP pública desde varios servicios
            services = [
                'https://api.ipify.org',
                'https://ifconfig.me/ip',
                'https://icanhazip.com'
            ]
            
            for service in services:
                try:
                    req = urllib.request.Request(service)
                    with urllib.request.urlopen(req, timeout=3) as response:
                        ip = response.read().decode().strip()
                        if self._is_ip(ip):
                            return ip
                except:
                    continue
            
            # Fallback a IP local
            return self.get_local_ip()
        except:
            return self.get_local_ip()
    
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
        """Obtiene todos los códigos registrados localmente"""
        return self.registry.copy()
    
    def remove_code(self, code: str):
        """Elimina un código del registro local"""
        if code in self.registry:
            del self.registry[code]
            self._save_registry()
    
    def update_code_ip(self, code: str, new_ip: str):
        """Actualiza la IP de un código existente"""
        if code in self.registry:
            self.registry[code]['ip'] = new_ip
            self.registry[code]['last_seen'] = self._get_timestamp()
            self._save_registry()
    
    def test_central_server(self) -> bool:
        """Prueba la conexión con el servidor central"""
        try:
            url = f"{self.registry_server}/status"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode())
                return data.get('success', False)
        except:
            return False


# Instancia global
_code_manager = None

def get_code_manager() -> ConnectionCodeManager:
    """Obtiene la instancia global del gestor de códigos"""
    global _code_manager
    if _code_manager is None:
        _code_manager = ConnectionCodeManager()
    return _code_manager
