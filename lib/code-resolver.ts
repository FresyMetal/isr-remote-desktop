/**
 * Módulo para resolver códigos ISR a IP:puerto
 */

import axios from 'axios';

const REGISTRY_SERVER = 'http://77.225.201.4:8080';
const TIMEOUT = 5000; // 5 segundos

export interface ResolveResult {
  success: boolean;
  host: string;
  port: number;
  error?: string;
}

/**
 * Verifica si un string es una IP válida
 */
function isValidIP(text: string): boolean {
  const parts = text.split(':')[0].split('.');
  if (parts.length !== 4) return false;
  
  return parts.every(part => {
    const num = parseInt(part, 10);
    return num >= 0 && num <= 255;
  });
}

/**
 * Parsea una IP:puerto o IP sola
 */
function parseIPPort(text: string): { host: string; port: number } | null {
  if (text.includes(':')) {
    const [host, portStr] = text.split(':');
    const port = parseInt(portStr, 10);
    if (isValidIP(host) && port > 0 && port <= 65535) {
      return { host, port };
    }
  } else if (isValidIP(text)) {
    return { host: text, port: 5900 }; // Puerto por defecto
  }
  
  return null;
}

/**
 * Resuelve un código ISR desde el servidor central
 */
async function resolveFromServer(code: string): Promise<ResolveResult> {
  try {
    const response = await axios.get(`${REGISTRY_SERVER}/resolve`, {
      params: { code },
      timeout: TIMEOUT,
    });
    
    const data = response.data;
    
    if (data.success && data.host && data.port) {
      return {
        success: true,
        host: data.host,
        port: data.port,
      };
    }
    
    return {
      success: false,
      host: '',
      port: 0,
      error: data.error || 'Código no encontrado',
    };
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNABORTED') {
        return {
          success: false,
          host: '',
          port: 0,
          error: 'Timeout: No se pudo conectar al servidor central',
        };
      }
      if (error.response) {
        return {
          success: false,
          host: '',
          port: 0,
          error: `Error del servidor: ${error.response.status}`,
        };
      }
      return {
        success: false,
        host: '',
        port: 0,
        error: 'No se pudo conectar al servidor central',
      };
    }
    
    return {
      success: false,
      host: '',
      port: 0,
      error: 'Error desconocido al resolver código',
    };
  }
}

/**
 * Resuelve un código ISR o IP:puerto a host y puerto
 * 
 * Soporta:
 * - Códigos ISR: ISR-12345678
 * - IP con puerto: 192.168.0.97:5900
 * - IP sin puerto: 192.168.0.97 (usa puerto 5900 por defecto)
 */
export async function resolveCode(codeOrIP: string): Promise<ResolveResult> {
  const trimmed = codeOrIP.trim();
  
  if (!trimmed) {
    return {
      success: false,
      host: '',
      port: 0,
      error: 'Código o IP vacío',
    };
  }
  
  // Intentar parsear como IP:puerto
  const parsed = parseIPPort(trimmed);
  if (parsed) {
    return {
      success: true,
      host: parsed.host,
      port: parsed.port,
    };
  }
  
  // Es un código ISR, resolver desde el servidor central
  return resolveFromServer(trimmed);
}

/**
 * Verifica si el servidor central está accesible
 */
export async function testRegistryServer(): Promise<boolean> {
  try {
    const response = await axios.get(`${REGISTRY_SERVER}/status`, {
      timeout: TIMEOUT,
    });
    return response.data?.success === true;
  } catch {
    return false;
  }
}
