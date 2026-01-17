/**
 * Módulo de almacenamiento local usando AsyncStorage
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import type { RecentConnection } from '@/types/connection';

const STORAGE_KEYS = {
  RECENT_CONNECTIONS: '@isr_recent_connections',
};

const MAX_RECENT_CONNECTIONS = 10;

/**
 * Guarda una conexión en el historial de recientes
 */
export async function saveRecentConnection(connection: Omit<RecentConnection, 'id' | 'lastConnected'>): Promise<void> {
  try {
    // Cargar conexiones existentes
    const existing = await getRecentConnections();
    
    // Crear nueva conexión con ID y timestamp
    const newConnection: RecentConnection = {
      ...connection,
      id: `${connection.host}:${connection.port}`,
      lastConnected: Date.now(),
    };
    
    // Eliminar duplicados (misma IP:puerto)
    const filtered = existing.filter(c => c.id !== newConnection.id);
    
    // Agregar al inicio
    const updated = [newConnection, ...filtered];
    
    // Limitar a MAX_RECENT_CONNECTIONS
    const limited = updated.slice(0, MAX_RECENT_CONNECTIONS);
    
    // Guardar
    await AsyncStorage.setItem(STORAGE_KEYS.RECENT_CONNECTIONS, JSON.stringify(limited));
  } catch (error) {
    console.error('[Storage] Error saving recent connection:', error);
  }
}

/**
 * Obtiene el historial de conexiones recientes
 */
export async function getRecentConnections(): Promise<RecentConnection[]> {
  try {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.RECENT_CONNECTIONS);
    if (!data) return [];
    
    const connections = JSON.parse(data) as RecentConnection[];
    
    // Ordenar por última conexión (más reciente primero)
    return connections.sort((a, b) => b.lastConnected - a.lastConnected);
  } catch (error) {
    console.error('[Storage] Error loading recent connections:', error);
    return [];
  }
}

/**
 * Elimina una conexión del historial
 */
export async function deleteRecentConnection(id: string): Promise<void> {
  try {
    const existing = await getRecentConnections();
    const filtered = existing.filter(c => c.id !== id);
    await AsyncStorage.setItem(STORAGE_KEYS.RECENT_CONNECTIONS, JSON.stringify(filtered));
  } catch (error) {
    console.error('[Storage] Error deleting recent connection:', error);
  }
}

/**
 * Limpia todo el historial de conexiones
 */
export async function clearRecentConnections(): Promise<void> {
  try {
    await AsyncStorage.removeItem(STORAGE_KEYS.RECENT_CONNECTIONS);
  } catch (error) {
    console.error('[Storage] Error clearing recent connections:', error);
  }
}
