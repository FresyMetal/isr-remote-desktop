/**
 * Pantalla de Visor de Escritorio Remoto
 */

import { useState, useEffect } from 'react';
import { View, Text, ActivityIndicator, Alert, TouchableOpacity } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import * as Haptics from 'expo-haptics';

import { ScreenContainer } from '@/components/screen-container';
import { useColors } from '@/hooks/use-colors';

export default function RemoteViewerScreen() {
  const colors = useColors();
  const router = useRouter();
  const params = useLocalSearchParams<{ host: string; port: string; code: string }>();
  
  const [isConnecting, setIsConnecting] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    // Simular conexión (por ahora)
    // TODO: Implementar WebSocket real
    const timer = setTimeout(() => {
      setIsConnecting(false);
      // Simular error para testing
      setError('Funcionalidad de WebSocket en desarrollo');
    }, 2000);
    
    return () => clearTimeout(timer);
  }, []);
  
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
            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
            router.back();
          },
        },
      ]
    );
  }
  
  if (isConnecting) {
    return (
      <ScreenContainer className="items-center justify-center">
        <ActivityIndicator size="large" color={colors.primary} />
        <Text className="text-lg text-foreground mt-4">
          Conectando a {params.code}...
        </Text>
        <Text className="text-sm text-muted mt-2">
          {params.host}:{params.port}
        </Text>
        <TouchableOpacity
          onPress={() => router.back()}
          className="mt-8 px-6 py-3 border border-border rounded-full"
        >
          <Text className="text-foreground">Cancelar</Text>
        </TouchableOpacity>
      </ScreenContainer>
    );
  }
  
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
            onPress={() => {
              setError(null);
              setIsConnecting(true);
              // TODO: Reintentar conexión
              setTimeout(() => {
                setIsConnecting(false);
                setError('Funcionalidad de WebSocket en desarrollo');
              }, 2000);
            }}
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
          <Text className="text-sm text-muted">• El servidor esté activo</Text>
          <Text className="text-sm text-muted">• El código sea correcto</Text>
          <Text className="text-sm text-muted">• Tengas conexión a Internet</Text>
        </View>
      </ScreenContainer>
    );
  }
  
  // Vista de escritorio remoto (placeholder)
  return (
    <ScreenContainer edges={["top", "bottom", "left", "right"]}>
      <View className="flex-1 bg-black items-center justify-center">
        <Text className="text-white text-xl">
          Escritorio Remoto
        </Text>
        <Text className="text-white text-sm mt-2">
          (En desarrollo)
        </Text>
        
        <TouchableOpacity
          onPress={handleDisconnect}
          className="mt-8 bg-error px-6 py-3 rounded-full"
        >
          <Text className="text-white font-semibold">Desconectar</Text>
        </TouchableOpacity>
      </View>
    </ScreenContainer>
  );
}
