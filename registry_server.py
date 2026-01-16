#!/usr/bin/env python3
"""
Servidor de Registro Central para ISR Remote Desktop

Este servidor se ejecuta en Linux y permite:
- Registrar códigos de conexión con sus IPs
- Resolver códigos a IPs
- Actualizar IPs automáticamente
- API REST simple

Uso:
    python3 registry_server.py
    python3 registry_server.py --port 8080
    python3 registry_server.py --host 0.0.0.0 --port 8080
"""

import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import argparse
import os


class RegistryDatabase:
    """Base de datos de códigos de conexión"""
    
    def __init__(self, db_file='registry.json'):
        self.db_file = db_file
        self.data = self._load()
        self.lock = threading.Lock()
    
    def _load(self):
        """Carga la base de datos"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save(self):
        """Guarda la base de datos"""
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"[Error] No se pudo guardar la base de datos: {e}")
    
    def register(self, code, host, port, name=''):
        """Registra un código"""
        with self.lock:
            self.data[code] = {
                'host': host,
                'port': port,
                'name': name or code,
                'last_update': time.time(),
                'registered_at': self.data.get(code, {}).get('registered_at', time.time())
            }
            self._save()
            return True
    
    def resolve(self, code):
        """Resuelve un código a IP y puerto"""
        with self.lock:
            if code in self.data:
                entry = self.data[code]
                return entry['host'], entry['port']
            return None, None
    
    def get_info(self, code):
        """Obtiene información completa de un código"""
        with self.lock:
            return self.data.get(code)
    
    def list_all(self):
        """Lista todos los códigos registrados"""
        with self.lock:
            return dict(self.data)
    
    def delete(self, code):
        """Elimina un código"""
        with self.lock:
            if code in self.data:
                del self.data[code]
                self._save()
                return True
            return False
    
    def cleanup_old(self, max_age_hours=24):
        """Limpia códigos antiguos"""
        with self.lock:
            now = time.time()
            max_age_seconds = max_age_hours * 3600
            to_delete = []
            
            for code, entry in self.data.items():
                age = now - entry.get('last_update', 0)
                if age > max_age_seconds:
                    to_delete.append(code)
            
            for code in to_delete:
                del self.data[code]
            
            if to_delete:
                self._save()
                print(f"[Cleanup] Eliminados {len(to_delete)} códigos antiguos")
            
            return len(to_delete)


class RegistryHandler(BaseHTTPRequestHandler):
    """Manejador de peticiones HTTP"""
    
    def log_message(self, format, *args):
        """Log personalizado"""
        print(f"[{self.client_address[0]}] {format % args}")
    
    def _send_json(self, data, status=200):
        """Envía respuesta JSON"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error_json(self, message, status=400):
        """Envía error JSON"""
        self._send_json({'error': message, 'success': False}, status)
    
    def do_GET(self):
        """Maneja peticiones GET"""
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        # Resolver código
        if path == '/resolve':
            code = params.get('code', [''])[0]
            if not code:
                self._send_error_json('Falta el parámetro code')
                return
            
            host, port = self.server.db.resolve(code)
            if host:
                self._send_json({
                    'success': True,
                    'code': code,
                    'host': host,
                    'port': port
                })
            else:
                self._send_error_json(f'Código {code} no encontrado', 404)
        
        # Información de código
        elif path == '/info':
            code = params.get('code', [''])[0]
            if not code:
                self._send_error_json('Falta el parámetro code')
                return
            
            info = self.server.db.get_info(code)
            if info:
                self._send_json({
                    'success': True,
                    'code': code,
                    **info
                })
            else:
                self._send_error_json(f'Código {code} no encontrado', 404)
        
        # Listar todos
        elif path == '/list':
            all_codes = self.server.db.list_all()
            self._send_json({
                'success': True,
                'count': len(all_codes),
                'codes': all_codes
            })
        
        # Estado del servidor
        elif path == '/status':
            all_codes = self.server.db.list_all()
            self._send_json({
                'success': True,
                'status': 'running',
                'registered_codes': len(all_codes),
                'version': '2.2'
            })
        
        # Página de inicio
        elif path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            
            all_codes = self.server.db.list_all()
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>ISR Remote Desktop - Servidor de Registro</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                    .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                    .status {{ background: #27ae60; color: white; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                    th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                    th {{ background: #3498db; color: white; }}
                    tr:hover {{ background: #f5f5f5; }}
                    .code {{ font-family: monospace; background: #ecf0f1; padding: 5px 10px; border-radius: 3px; }}
                    .api {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    .api code {{ background: #34495e; color: #ecf0f1; padding: 2px 5px; border-radius: 3px; }}
                    .footer {{ text-align: center; color: #7f8c8d; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🖥️ ISR Remote Desktop - Servidor de Registro</h1>
                    
                    <div class="status">
                        <strong>✓ Servidor Activo</strong><br>
                        Códigos registrados: {len(all_codes)}
                    </div>
                    
                    <h2>📋 Códigos Registrados</h2>
                    <table>
                        <tr>
                            <th>Código</th>
                            <th>Nombre</th>
                            <th>Host</th>
                            <th>Puerto</th>
                            <th>Última Actualización</th>
                        </tr>
            """
            
            for code, info in sorted(all_codes.items()):
                last_update = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info.get('last_update', 0)))
                html += f"""
                        <tr>
                            <td><span class="code">{code}</span></td>
                            <td>{info.get('name', code)}</td>
                            <td>{info.get('host', 'N/A')}</td>
                            <td>{info.get('port', 'N/A')}</td>
                            <td>{last_update}</td>
                        </tr>
                """
            
            if not all_codes:
                html += """
                        <tr>
                            <td colspan="5" style="text-align: center; color: #7f8c8d;">
                                No hay códigos registrados
                            </td>
                        </tr>
                """
            
            html += """
                    </table>
                    
                    <h2>🔌 API REST</h2>
                    <div class="api">
                        <p><strong>Registrar código:</strong></p>
                        <code>POST /register?code=ISR-12345678&host=192.168.1.100&port=5900&name=MiServidor</code>
                        
                        <p style="margin-top: 15px;"><strong>Resolver código:</strong></p>
                        <code>GET /resolve?code=ISR-12345678</code>
                        
                        <p style="margin-top: 15px;"><strong>Información de código:</strong></p>
                        <code>GET /info?code=ISR-12345678</code>
                        
                        <p style="margin-top: 15px;"><strong>Listar todos:</strong></p>
                        <code>GET /list</code>
                        
                        <p style="margin-top: 15px;"><strong>Estado del servidor:</strong></p>
                        <code>GET /status</code>
                    </div>
                    
                    <div class="footer">
                        <p>ISR Comunicaciones © 2026</p>
                        <p>Servidor de Registro Central v2.2</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
        
        else:
            self._send_error_json('Endpoint no encontrado', 404)
    
    def do_POST(self):
        """Maneja peticiones POST"""
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        # Registrar código
        if path == '/register':
            code = params.get('code', [''])[0]
            host = params.get('host', [''])[0]
            port = params.get('port', ['5900'])[0]
            name = params.get('name', [''])[0]
            
            if not code or not host:
                self._send_error_json('Faltan parámetros: code y host son obligatorios')
                return
            
            try:
                port = int(port)
            except:
                self._send_error_json('Puerto inválido')
                return
            
            self.server.db.register(code, host, port, name)
            self._send_json({
                'success': True,
                'message': f'Código {code} registrado correctamente',
                'code': code,
                'host': host,
                'port': port
            })
        
        # Eliminar código
        elif path == '/delete':
            code = params.get('code', [''])[0]
            if not code:
                self._send_error_json('Falta el parámetro code')
                return
            
            if self.server.db.delete(code):
                self._send_json({
                    'success': True,
                    'message': f'Código {code} eliminado'
                })
            else:
                self._send_error_json(f'Código {code} no encontrado', 404)
        
        else:
            self._send_error_json('Endpoint no encontrado', 404)
    
    def do_OPTIONS(self):
        """Maneja peticiones OPTIONS (CORS)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


class RegistryServer(HTTPServer):
    """Servidor HTTP con base de datos"""
    
    def __init__(self, host, port, db_file='registry.json'):
        super().__init__((host, port), RegistryHandler)
        self.db = RegistryDatabase(db_file)
        self.cleanup_thread = None
        self.running = True
    
    def start_cleanup_thread(self, interval_hours=1):
        """Inicia hilo de limpieza automática"""
        def cleanup_loop():
            while self.running:
                time.sleep(interval_hours * 3600)
                if self.running:
                    self.db.cleanup_old()
        
        self.cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def stop(self):
        """Detiene el servidor"""
        self.running = False
        self.shutdown()


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Servidor de Registro Central para ISR Remote Desktop')
    parser.add_argument('--host', default='0.0.0.0', help='Dirección IP para escuchar (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='Puerto para escuchar (default: 8080)')
    parser.add_argument('--db', default='registry.json', help='Archivo de base de datos (default: registry.json)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  SERVIDOR DE REGISTRO CENTRAL - ISR REMOTE DESKTOP")
    print("=" * 60)
    print(f"Host: {args.host}")
    print(f"Puerto: {args.port}")
    print(f"Base de datos: {args.db}")
    print("=" * 60)
    print("")
    print("Endpoints disponibles:")
    print(f"  http://{args.host}:{args.port}/                  - Página de inicio")
    print(f"  http://{args.host}:{args.port}/register          - Registrar código (POST)")
    print(f"  http://{args.host}:{args.port}/resolve           - Resolver código (GET)")
    print(f"  http://{args.host}:{args.port}/info              - Información de código (GET)")
    print(f"  http://{args.host}:{args.port}/list              - Listar todos (GET)")
    print(f"  http://{args.host}:{args.port}/status            - Estado del servidor (GET)")
    print("")
    print("Presiona Ctrl+C para detener el servidor")
    print("=" * 60)
    print("")
    
    server = RegistryServer(args.host, args.port, args.db)
    server.start_cleanup_thread()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Servidor] Interrupción de teclado recibida")
    finally:
        server.stop()
        print("[Servidor] Detenido")


if __name__ == '__main__':
    main()
