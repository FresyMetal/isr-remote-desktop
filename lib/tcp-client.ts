/**
 * Cliente TCP para conexión al servidor de escritorio remoto
 * Implementa el protocolo binario compatible con el servidor Python
 */

import { Buffer } from 'buffer';

// Constantes del protocolo
const MAGIC_NUMBER = 0x5244; // "RD" = Remote Desktop
const HEADER_SIZE = 12;

// Tipos de mensajes
export enum MessageType {
  HANDSHAKE = 0x01,
  AUTH_REQUEST = 0x02,
  AUTH_RESPONSE = 0x03,
  VIDEO_FRAME = 0x10,
  VIDEO_REQUEST = 0x11,
  VIDEO_CONFIG = 0x12,
  MONITOR_LIST = 0x13,
  MONITOR_CHANGE = 0x14,
  INPUT_MOUSE = 0x20,
  INPUT_KEYBOARD = 0x21,
  INPUT_SCROLL = 0x22,
  FILE_METADATA = 0x30,
  FILE_CHUNK = 0x31,
  FILE_COMPLETE = 0x32,
  FILE_ERROR = 0x33,
  CLIPBOARD_TEXT = 0x40,
  CLIPBOARD_IMAGE = 0x41,
  PING = 0xF0,
  PONG = 0xF1,
  DISCONNECT = 0xF2,
  ERROR = 0xFF,
}

// Flags de mensajes
export enum MessageFlags {
  NONE = 0x00,
  COMPRESSED = 0x01,
  ENCRYPTED = 0x02,
  PRIORITY = 0x04,
}

export interface Frame {
  x: number;
  y: number;
  width: number;
  height: number;
  encoding: number;
  data: Uint8Array;
}

export interface Monitor {
  id: number;
  name: string;
  width: number;
  height: number;
  isPrimary: boolean;
}

export interface TCPClientEvents {
  onConnected?: () => void;
  onDisconnected?: () => void;
  onFrame?: (frame: Frame) => void;
  onError?: (error: string) => void;
  onClipboard?: (text: string) => void;
  onMonitorList?: (monitors: Monitor[]) => void;
}

export class TCPClient {
  private socket: any = null;
  private host: string;
  private port: number;
  private events: TCPClientEvents;
  private sequenceNumber: number = 0;
  private buffer: Buffer = Buffer.alloc(0);
  private connected: boolean = false;

  constructor(host: string, port: number, events: TCPClientEvents) {
    this.host = host;
    this.port = port;
    this.events = events;
  }

  async connect(): Promise<boolean> {
    try {
      // Usar react-native-tcp-socket para conexión TCP
      const TcpSocket = require('react-native-tcp-socket');
      
      return new Promise((resolve, reject) => {
        this.socket = TcpSocket.createConnection(
          {
            host: this.host,
            port: this.port,
          },
          () => {
            console.log('[TCP] Conectado al servidor');
            this.connected = true;
            this.sendHandshake();
            if (this.events.onConnected) {
              this.events.onConnected();
            }
            resolve(true);
          }
        );

        this.socket.on('data', (data: Buffer) => {
          this.handleData(data);
        });

        this.socket.on('error', (error: Error) => {
          console.error('[TCP] Error:', error);
          if (this.events.onError) {
            this.events.onError(error.message);
          }
          reject(error);
        });

        this.socket.on('close', () => {
          console.log('[TCP] Conexión cerrada');
          this.connected = false;
          if (this.events.onDisconnected) {
            this.events.onDisconnected();
          }
        });

        // Timeout de 10 segundos
        setTimeout(() => {
          if (!this.connected) {
            this.socket.destroy();
            reject(new Error('Timeout de conexión'));
          }
        }, 10000);
      });
    } catch (error) {
      console.error('[TCP] Error al conectar:', error);
      if (this.events.onError) {
        this.events.onError(error instanceof Error ? error.message : 'Error desconocido');
      }
      return false;
    }
  }

  disconnect() {
    if (this.socket) {
      try {
        // Enviar mensaje de desconexión
        const message = this.encodeMessage(MessageType.DISCONNECT, Buffer.alloc(0));
        this.socket.write(message);
      } catch (e) {
        // Ignorar errores al desconectar
      }
      
      this.socket.destroy();
      this.socket = null;
    }
    this.connected = false;
  }

  private sendHandshake() {
    // Handshake: version (1 byte) + capabilities (4 bytes)
    const payload = Buffer.alloc(5);
    payload.writeUInt8(1, 0); // version = 1
    payload.writeUInt32BE(0, 1); // capabilities = 0
    
    const message = this.encodeMessage(MessageType.HANDSHAKE, payload);
    this.socket.write(message);
    console.log('[TCP] Handshake enviado');
  }

  private encodeMessage(msgType: MessageType, payload: Buffer): Buffer {
    const header = Buffer.alloc(HEADER_SIZE);
    
    // Magic number (2 bytes)
    header.writeUInt16BE(MAGIC_NUMBER, 0);
    
    // Message type (1 byte)
    header.writeUInt8(msgType, 2);
    
    // Flags (1 byte)
    header.writeUInt8(MessageFlags.NONE, 3);
    
    // Payload length (4 bytes)
    header.writeUInt32BE(payload.length, 4);
    
    // Sequence number (4 bytes)
    header.writeUInt32BE(this.sequenceNumber, 8);
    this.sequenceNumber = (this.sequenceNumber + 1) % 0xFFFFFFFF;
    
    return Buffer.concat([header, payload]);
  }

  private handleData(data: Buffer) {
    // Agregar datos al buffer
    this.buffer = Buffer.concat([this.buffer, data]);
    
    // Procesar mensajes completos
    while (this.buffer.length >= HEADER_SIZE) {
      // Leer header
      const magic = this.buffer.readUInt16BE(0);
      
      if (magic !== MAGIC_NUMBER) {
        console.error('[TCP] Magic number inválido');
        this.buffer = Buffer.alloc(0);
        return;
      }
      
      const msgType = this.buffer.readUInt8(2);
      const flags = this.buffer.readUInt8(3);
      const payloadLen = this.buffer.readUInt32BE(4);
      const seqNum = this.buffer.readUInt32BE(8);
      
      // Verificar si tenemos el mensaje completo
      if (this.buffer.length < HEADER_SIZE + payloadLen) {
        // Mensaje incompleto, esperar más datos
        break;
      }
      
      // Extraer payload
      const payload = this.buffer.subarray(HEADER_SIZE, HEADER_SIZE + payloadLen);
      
      // Procesar mensaje
      this.processMessage(msgType, flags, payload);
      
      // Remover mensaje procesado del buffer
      this.buffer = this.buffer.subarray(HEADER_SIZE + payloadLen);
    }
  }

  private processMessage(msgType: number, flags: number, payload: Buffer) {
    try {
      switch (msgType) {
        case MessageType.AUTH_RESPONSE:
          this.handleAuthResponse(payload);
          break;
          
        case MessageType.VIDEO_FRAME:
          this.handleVideoFrame(payload);
          break;
          
        case MessageType.CLIPBOARD_TEXT:
          this.handleClipboard(payload);
          break;
          
        case MessageType.MONITOR_LIST:
          this.handleMonitorList(payload);
          break;
          
        case MessageType.PONG:
          // Respuesta a ping
          break;
          
        default:
          console.log(`[TCP] Mensaje no manejado: tipo ${msgType}`);
      }
    } catch (error) {
      console.error('[TCP] Error al procesar mensaje:', error);
    }
  }

  private handleAuthResponse(payload: Buffer) {
    const success = payload.readUInt8(0) === 1;
    const messageLen = payload.readUInt32BE(1);
    const message = payload.subarray(5, 5 + messageLen).toString('utf-8');
    
    console.log(`[TCP] Auth response: ${success ? 'OK' : 'FAIL'} - ${message}`);
    
    if (!success && this.events.onError) {
      this.events.onError(`Autenticación fallida: ${message}`);
    }
  }

  private handleVideoFrame(payload: Buffer) {
    try {
      // Decodificar frame: x, y, width, height, encoding, data
      const x = payload.readInt32BE(0);
      const y = payload.readInt32BE(4);
      const width = payload.readUInt32BE(8);
      const height = payload.readUInt32BE(12);
      const encoding = payload.readUInt8(16);
      const frameData = payload.subarray(17);
      
      const frame: Frame = {
        x,
        y,
        width,
        height,
        encoding,
        data: new Uint8Array(frameData),
      };
      
      if (this.events.onFrame) {
        this.events.onFrame(frame);
      }
    } catch (error) {
      console.error('[TCP] Error al decodificar frame:', error);
    }
  }

  private handleClipboard(payload: Buffer) {
    try {
      const textLen = payload.readUInt32BE(0);
      const text = payload.subarray(4, 4 + textLen).toString('utf-8');
      
      if (this.events.onClipboard) {
        this.events.onClipboard(text);
      }
    } catch (error) {
      console.error('[TCP] Error al decodificar clipboard:', error);
    }
  }

  private handleMonitorList(payload: Buffer) {
    try {
      const monitorCount = payload.readUInt8(0);
      const monitors: Monitor[] = [];
      
      let offset = 1;
      for (let i = 0; i < monitorCount; i++) {
        const id = payload.readUInt8(offset);
        offset += 1;
        
        const nameLen = payload.readUInt8(offset);
        offset += 1;
        
        const name = payload.subarray(offset, offset + nameLen).toString('utf-8');
        offset += nameLen;
        
        const width = payload.readUInt32BE(offset);
        offset += 4;
        
        const height = payload.readUInt32BE(offset);
        offset += 4;
        
        const isPrimary = payload.readUInt8(offset) === 1;
        offset += 1;
        
        monitors.push({ id, name, width, height, isPrimary });
      }
      
      console.log(`[TCP] Lista de monitores recibida: ${monitors.length} monitores`);
      
      if (this.events.onMonitorList) {
        this.events.onMonitorList(monitors);
      }
    } catch (error) {
      console.error('[TCP] Error al decodificar lista de monitores:', error);
    }
  }

  sendMouseEvent(x: number, y: number, buttons: number) {
    if (!this.connected) return;
    
    const payload = Buffer.alloc(12);
    payload.writeInt32BE(x, 0);
    payload.writeInt32BE(y, 4);
    payload.writeUInt32BE(buttons, 8);
    
    const message = this.encodeMessage(MessageType.INPUT_MOUSE, payload);
    this.socket.write(message);
  }

  sendKeyboardEvent(keyCode: number, pressed: boolean) {
    if (!this.connected) return;
    
    const payload = Buffer.alloc(5);
    payload.writeUInt32BE(keyCode, 0);
    payload.writeUInt8(pressed ? 1 : 0, 4);
    
    const message = this.encodeMessage(MessageType.INPUT_KEYBOARD, payload);
    this.socket.write(message);
  }

  sendPing() {
    if (!this.connected) return;
    
    const message = this.encodeMessage(MessageType.PING, Buffer.alloc(0));
    this.socket.write(message);
  }

  requestMonitorList() {
    if (!this.connected) return;
    
    // Solicitar lista de monitores al servidor
    const message = this.encodeMessage(MessageType.MONITOR_LIST, Buffer.alloc(0));
    this.socket.write(message);
    console.log('[TCP] Solicitando lista de monitores');
  }

  changeMonitor(monitorId: number) {
    if (!this.connected) return;
    
    const payload = Buffer.alloc(1);
    payload.writeUInt8(monitorId, 0);
    
    const message = this.encodeMessage(MessageType.MONITOR_CHANGE, payload);
    this.socket.write(message);
    console.log(`[TCP] Cambiando a monitor ${monitorId}`);
  }
}
