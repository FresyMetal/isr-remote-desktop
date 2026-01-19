/**
 * Pantalla de Visor de Escritorio Remoto
 * Conecta al servidor TCP y muestra el escritorio remoto
 */

import { useState, useEffect, useRef } from 'react';
import { View, Text, ActivityIndicator, Alert, TouchableOpacity, BackHandler } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import * as Haptics from 'expo-haptics';
import * as KeepAwake from 'expo-keep-awake';

import { ScreenContainer } from '@/components/screen-container';
import { RemoteDesktopView } from '@/components/remote-desktop-view';
import { useColors } from '@/hooks/use-colors';
import { TCPClient } from '@/lib/tcp-client';

export default function RemoteViewerScreen() {
  const colors = useColors();
  const router = useRouter();
  const params = useLocalSearchParams<{ host: string; port: string; code: string }>();
  
  const [isConnecting, setIsConnecting] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState('Conectando...');
  
  const clientRef = useRef<TCPClient | null>(null);
  
  // Mantener pantalla encendida mientras está conectado
  useEffect(() => {
    if (isConnected) {
      KeepAwake.activateKeepAwakeAsync();
    }
    
    return () => {
      KeepAwake.deactivateKeepAwake();
    };
  }, [isConnected]);
  
  // Manejar botón atrás de Android
  useEffect(() => {
    const backHandler = BackHandler.addEventListener('hardwareBackPress', () => {
      if (isConnected) {
        handleDisconnect();
        return true; // Prevenir comportamiento por defecto
      }
      return false;
    });
    
    return () => backHandler.remove();
  }, [isConnected]);
  
  // Conectar al servidor
  useEffect(() => {
    connectToServer();
    
    return () => {
      // Desconectar al desmontar
      if (clientRef.current) {
        clientRef.current.disconnect();
      }
    };
  }, []);
  
  async function connectToServer() {
    try {
      setIsConnecting(true);
      setError(null);
      setStatusMessage('Conectando al servidor...');
      
      const host = params.host;
      const port = parseInt(params.port, 10);
      
      if (!host || !port) {
        throw new Error('Host o puerto inválido');
      }
      
      // Crear cliente TCP
      const client = new TCPClient(host, port, {
        onConnected: () => {
          console.log('[Viewer] Conectado al servidor');
          setStatusMessage('Autenticando...');
        },
        
        onDisconnected: () => {
          console.log('[Viewer] Desconectado del servidor');
          setIsConnected(false);
          if (!error) {
            setError('Conexión perdida');
          }
        },
        
        onFrame: (frame) => {
          // El primer frame indica que estamos completamente conectados
          if (!isConnected) {
            setIsConnected(true);
            setIsConnecting(false);
            setStatusMessage('Conectado');
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
          }
        },
        
        onError: (errorMsg) => {
          console.error('[Viewer] Error:', errorMsg);
          setError(errorMsg);
          setIsConnecting(false);
          setIsConnected(false);
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
        },
        
        onClipboard: (text) => {
          console.log('[Viewer] Clipboard actualizado:', text.substring(0, 50));
        },
      });
      
      clientRef.current = client;
      
      // Intentar conectar
      const connected = await client.connect();
      
      if (!connected) {
        throw new Error('No se pudo establecer la conexión');
      }
      
      // Esperar hasta 10 segundos para recibir el primer frame
      let timeout = setTimeout(() => {
        if (!isConnected) {
          setError('Timeout: No se recibieron frames del servidor');
          setIsConnecting(false);
          client.disconnect();
        }
      }, 10000);
      
      return () => clearTimeout(timeout);
      
    } catch (err) {
      console.error('[Viewer] Error al conectar:', err);
      setError(err instanceof Error ? err.message : 'Error desconocido');
      setIsConnecting(false);
      setIsConnected(false);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    }
  }
  
  function handleDisconnect() {
    Alert.alert(
      'Desconectar',
      '¿Estás seguro de que quieres desconectar?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Desconectar',
          style: 'destructive',
          onPress: () => {
            if (clientRef.current) {
              clientRef.current.disconnect();
            }
            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
            router.back();
          },
        },
      ]
    );
  }
  
  function handleRetry() {
    setError(null);
    setIsConnecting(true);
    connectToServer();
  }
  
  // Pantalla de conexión
  if (isConnecting) {
    return (
      <ScreenContainer className="items-center justify-center">
        <ActivityIndicator size="large" color={colors.primary} />
        <Text className="text-lg text-foreground mt-4">
          {statusMessage}
        </Text>
        <Text className="text-sm text-muted mt-2">
          {params.code}
        </Text>
        <Text className="text-xs text-muted mt-1">
          {params.host}:{params.port}
        </Text>
        <TouchableOpacity
          onPress={() => {
            if (clientRef.current) {
              clientRef.current.disconnect();
            }
            router.back();
          }}
          className="mt-8 px-6 py-3 border border-border rounded-full"
        >
          <Text className="text-foreground">Cancelar</Text>
        </TouchableOpacity>
      </ScreenContainer>
    );
  }
  
  // Pantalla de error
  if (error) {
    return (
      <ScreenContainer className="items-center justify-center p-6">
        <Text className="text-6xl mb-4">❌</Text>
        <Text className="text-2xl font-bold text-foreground mb-2">
          Error de Conexión
        </Text>
        <Text className="text-base text-muted text-center mb-6">
          {error}
        </Text>
        
        <View className="gap-3 w-full max-w-sm">
          <TouchableOpacity
            onPress={handleRetry}
            className="bg-primary rounded-full py-4 items-center"
          >
            <Text className="text-white font-semibold text-lg">Reintentar</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            onPress={() => router.back()}
            className="border border-border rounded-full py-4 items-center"
          >
            <Text className="text-foreground font-semibold text-lg">Volver</Text>
          </TouchableOpacity>
        </View>
        
        <View className="mt-8 bg-surface p-4 rounded-xl border border-border">
          <Text className="text-sm text-muted mb-2">Verifica que:</Text>
          <Text className="text-sm text-muted">• El servidor esté activo en el PC</Text>
          <Text className="text-sm text-muted">• El código/IP sea correcto</Text>
          <Text className="text-sm text-muted">• Estés en la misma red WiFi</Text>
          <Text className="text-sm text-muted">• No haya firewall bloqueando</Text>
        </View>
      </ScreenContainer>
    );
  }
  
  // Vista de escritorio remoto conectado
  if (isConnected && clientRef.current) {
    return (
      <ScreenContainer edges={["top", "bottom", "left", "right"]}>
        <View className="flex-1">
          {/* Visor del escritorio remoto */}
          <RemoteDesktopView 
            client={clientRef.current}
            onDisconnect={handleDisconnect}
          />
          
          {/* Botón flotante de desconexión */}
          <View className="absolute top-12 right-4">
            <TouchableOpacity
              onPress={handleDisconnect}
              className="bg-error px-4 py-2 rounded-full shadow-lg"
              style={{
                shadowColor: '#000',
                shadowOffset: { width: 0, height: 2 },
                shadowOpacity: 0.25,
                shadowRadius: 3.84,
                elevation: 5,
              }}
            >
              <Text className="text-white font-semibold">✕ Desconectar</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScreenContainer>
    );
  }
  
  return null;
}
