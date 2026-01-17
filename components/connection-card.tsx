/**
 * Card para mostrar una conexión reciente
 */

import { Text, View, Pressable, type PressableProps } from 'react-native';
import { IconSymbol } from './ui/icon-symbol';
import { useColors } from '@/hooks/use-colors';
import type { RecentConnection } from '@/types/connection';

interface ConnectionCardProps extends Omit<PressableProps, 'children'> {
  connection: RecentConnection;
  onDelete?: () => void;
}

function formatTimestamp(timestamp: number): string {
  const now = Date.now();
  const diff = now - timestamp;
  
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 1) return 'Ahora mismo';
  if (minutes < 60) return `Hace ${minutes} min`;
  if (hours < 24) return `Hace ${hours} h`;
  if (days === 1) return 'Ayer';
  return `Hace ${days} días`;
}

export function ConnectionCard({ connection, onDelete, ...props }: ConnectionCardProps) {
  const colors = useColors();
  
  return (
    <Pressable
      {...props}
      style={({ pressed }) => [
        {
          opacity: pressed ? 0.8 : 1,
        },
      ]}
      className="bg-surface border border-border rounded-2xl p-4 mb-3 flex-row items-center"
    >
      {/* Icono */}
      <View className="mr-4">
        <IconSymbol name="house.fill" size={32} color={colors.primary} />
      </View>
      
      {/* Información */}
      <View className="flex-1">
        <Text className="text-lg font-semibold text-foreground mb-1">
          {connection.name || connection.code}
        </Text>
        <Text className="text-sm text-muted">
          {connection.host}:{connection.port}
        </Text>
        <Text className="text-xs text-muted mt-1">
          {formatTimestamp(connection.lastConnected)}
        </Text>
      </View>
      
      {/* Botón de eliminar (opcional) */}
      {onDelete && (
        <Pressable
          onPress={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          style={({ pressed }) => ({
            opacity: pressed ? 0.6 : 1,
          })}
          className="p-2"
        >
          <Text className="text-error text-lg">✕</Text>
        </Pressable>
      )}
    </Pressable>
  );
}
