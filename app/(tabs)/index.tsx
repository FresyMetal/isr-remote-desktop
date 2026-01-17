/**
 * Pantalla Principal - Conexión a Escritorio Remoto
 */

import { useState, useEffect } from 'react';
import { ScrollView, Text, View, TextInput, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import * as Haptics from 'expo-haptics';

import { ScreenContainer } from '@/components/screen-container';
import { ConnectionCard } from '@/components/connection-card';
import { useColors } from '@/hooks/use-colors';
import { resolveCode } from '@/lib/code-resolver';
import { getRecentConnections, saveRecentConnection, deleteRecentConnection } from '@/lib/storage';
import type { RecentConnection } from '@/types/connection';

export default function HomeScreen() {
  const colors = useColors();
  const router = useRouter();
  
  const [code, setCode] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  const [recentConnections, setRecentConnections] = useState<RecentConnection[]>([]);
  const [isLoadingRecent, setIsLoadingRecent] = useState(true);
  
  // Cargar conexiones recientes al montar
  useEffect(() => {
    loadRecentConnections();
  }, []);
  
  async function loadRecentConnections() {
    setIsLoadingRecent(true);
    const connections = await getRecentConnections();
    setRecentConnections(connections);
    setIsLoadingRecent(false);
  }
  
  async function handleConnect(codeOrIP: string) {
    if (!codeOrIP.trim()) {
      Alert.alert('Error', 'Introduce un código ISR o IP:puerto');
      return;
    }
    
    setIsConnecting(true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    
    try {
      // Resolver código o IP
      const result = await resolveCode(codeOrIP);
      
      if (!result.success) {
        Alert.alert(
          'Error de Conexión',
          result.error || 'No se pudo resolver el código',
          [
            {
              text: 'OK',
              onPress: () => Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error),
            },
          ]
        );
        setIsConnecting(false);
        return;
      }
      
      // Guardar en historial
      await saveRecentConnection({
        code: codeOrIP,
        host: result.host,
        port: result.port,
      });
      
      // Recargar historial
      await loadRecentConnections();
      
      // Navegar a pantalla de escritorio remoto
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      router.push({
        pathname: '/remote/viewer',
        params: {
          host: result.host,
          port: result.port.toString(),
          code: codeOrIP,
        },
      });
    } catch (error) {
      Alert.alert(
        'Error',
        'Ocurrió un error inesperado al intentar conectar',
        [
          {
            text: 'OK',
            onPress: () => Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error),
          },
        ]
      );
    } finally {
      setIsConnecting(false);
    }
  }
  
  async function handleDeleteConnection(id: string) {
    Alert.alert(
      'Eliminar Conexión',
      '¿Estás seguro de que quieres eliminar esta conexión del historial?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Eliminar',
          style: 'destructive',
          onPress: async () => {
            await deleteRecentConnection(id);
            await loadRecentConnections();
            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
          },
        },
      ]
    );
  }
  
  return (
    <ScreenContainer className="p-6">
      <ScrollView contentContainerStyle={{ flexGrow: 1 }}>
        <View className="flex-1 gap-6">
          {/* Hero Section */}
          <View className="items-center gap-2 mt-4">
            <Text className="text-4xl font-bold text-foreground">🖥️ ISR Remote</Text>
            <Text className="text-base text-muted text-center">
              Controla tus ordenadores desde cualquier lugar
            </Text>
          </View>

          {/* Input de Código */}
          <View className="gap-3">
            <TextInput
              value={code}
              onChangeText={setCode}
              placeholder="ISR-12345678 o 192.168.0.97:5900"
              placeholderTextColor={colors.muted}
              autoCapitalize="none"
              autoCorrect={false}
              editable={!isConnecting}
              returnKeyType="done"
              onSubmitEditing={() => handleConnect(code)}
              className="bg-surface border-2 border-border rounded-xl px-4 py-4 text-lg text-foreground"
              style={{
                borderColor: colors.border,
                color: colors.foreground,
              }}
            />

            {/* Botón Conectar */}
            <TouchableOpacity
              onPress={() => handleConnect(code)}
              disabled={isConnecting}
              activeOpacity={0.8}
              className="bg-primary rounded-full py-4 items-center"
              style={{
                backgroundColor: isConnecting ? colors.muted : colors.primary,
              }}
            >
              {isConnecting ? (
                <View className="flex-row items-center gap-2">
                  <ActivityIndicator color="#ffffff" />
                  <Text className="text-white font-semibold text-lg">Conectando...</Text>
                </View>
              ) : (
                <Text className="text-white font-semibold text-lg">Conectar</Text>
              )}
            </TouchableOpacity>
          </View>

          {/* Conexiones Recientes */}
          {isLoadingRecent ? (
            <View className="items-center py-8">
              <ActivityIndicator size="large" color={colors.primary} />
            </View>
          ) : recentConnections.length > 0 ? (
            <View className="gap-3">
              <Text className="text-xl font-semibold text-foreground">Recientes</Text>
              {recentConnections.map((connection) => (
                <ConnectionCard
                  key={connection.id}
                  connection={connection}
                  onPress={() => handleConnect(connection.code)}
                  onDelete={() => handleDeleteConnection(connection.id)}
                />
              ))}
            </View>
          ) : (
            <View className="items-center py-8">
              <Text className="text-muted text-center">
                No hay conexiones recientes{'\n'}
                Introduce un código ISR para empezar
              </Text>
            </View>
          )}
        </View>
      </ScrollView>
    </ScreenContainer>
  );
}
