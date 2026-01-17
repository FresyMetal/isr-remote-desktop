/**
 * Tipos relacionados con conexiones remotas
 */

export interface ConnectionInfo {
  /** Código ISR o IP:puerto */
  code: string;
  /** Nombre descriptivo (opcional) */
  name?: string;
  /** IP del servidor */
  host: string;
  /** Puerto del servidor */
  port: number;
  /** Timestamp de última conexión */
  lastConnected?: number;
}

export interface RecentConnection extends ConnectionInfo {
  /** ID único de la conexión */
  id: string;
  /** Timestamp de última conexión */
  lastConnected: number;
}

export enum ConnectionStatus {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  ERROR = 'error',
}

export interface ConnectionState {
  status: ConnectionStatus;
  info?: ConnectionInfo;
  error?: string;
  latency?: number;
}
