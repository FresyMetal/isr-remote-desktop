/**
 * Componente de Control de Portapapeles
 * Permite copiar del móvil al PC y pegar del PC al móvil
 */

import { View, Text, TouchableOpacity, StyleSheet, Alert, Platform } from 'react-native';
import * as Clipboard from 'expo-clipboard';
import * as Haptics from 'expo-haptics';
import { useColors } from '@/hooks/use-colors';
import type { TCPClient } from '@/lib/tcp-client';

interface ClipboardControlProps {
  client: TCPClient;
  pcClipboard: string;
  visible: boolean;
  onClose: () => void;
}

export function ClipboardControl({ client, pcClipboard, visible, onClose }: ClipboardControlProps) {
  const colors = useColors();

  if (!visible) {
    return null;
  }

  async function handleCopyToPC() {
    try {
      // Leer portapapeles del móvil
      const mobileClipboard = await Clipboard.getStringAsync();
      
      if (!mobileClipboard) {
        Alert.alert('Portapapeles vacío', 'No hay texto en el portapapeles del móvil');
        return;
      }
      
      // Enviar al PC
      client.sendClipboard(mobileClipboard);
      
      if (Platform.OS !== 'web') {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      }
      
      Alert.alert(
        'Copiado al PC',
        `Texto enviado al portapapeles del PC:\n\n${mobileClipboard.substring(0, 100)}${mobileClipboard.length > 100 ? '...' : ''}`
      );
      
      onClose();
    } catch (error) {
      console.error('[Clipboard] Error al copiar al PC:', error);
      Alert.alert('Error', 'No se pudo copiar al PC');
    }
  }

  async function handlePasteFromPC() {
    try {
      if (!pcClipboard) {
        Alert.alert('Portapapeles vacío', 'No hay texto en el portapapeles del PC');
        return;
      }
      
      // Copiar al portapapeles del móvil
      await Clipboard.setStringAsync(pcClipboard);
      
      if (Platform.OS !== 'web') {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      }
      
      Alert.alert(
        'Copiado al móvil',
        `Texto copiado al portapapeles del móvil:\n\n${pcClipboard.substring(0, 100)}${pcClipboard.length > 100 ? '...' : ''}`
      );
      
      onClose();
    } catch (error) {
      console.error('[Clipboard] Error al pegar del PC:', error);
      Alert.alert('Error', 'No se pudo copiar al móvil');
    }
  }

  return (
    <View style={[styles.overlay, { backgroundColor: 'rgba(0, 0, 0, 0.7)' }]}>
      <View style={[styles.container, { backgroundColor: colors.surface, borderColor: colors.border }]}>
        <Text style={[styles.title, { color: colors.foreground }]}>
          Portapapeles
        </Text>

        <View style={styles.actions}>
          {/* Copiar del móvil al PC */}
          <TouchableOpacity
            onPress={handleCopyToPC}
            style={[styles.actionButton, { backgroundColor: colors.primary, borderColor: colors.primary }]}
          >
            <Text style={styles.actionIcon}>📋</Text>
            <Text style={styles.actionLabel}>Copiar al PC</Text>
            <Text style={styles.actionDescription}>
              Envía el portapapeles del móvil al PC
            </Text>
          </TouchableOpacity>

          {/* Pegar del PC al móvil */}
          <TouchableOpacity
            onPress={handlePasteFromPC}
            style={[styles.actionButton, { backgroundColor: colors.primary, borderColor: colors.primary }]}
          >
            <Text style={styles.actionIcon}>📄</Text>
            <Text style={styles.actionLabel}>Pegar del PC</Text>
            <Text style={styles.actionDescription}>
              Copia el portapapeles del PC al móvil
            </Text>
          </TouchableOpacity>
        </View>

        {/* Mostrar contenido del portapapeles del PC */}
        {pcClipboard && (
          <View style={[styles.preview, { backgroundColor: colors.background, borderColor: colors.border }]}>
            <Text style={[styles.previewLabel, { color: colors.muted }]}>
              Portapapeles del PC:
            </Text>
            <Text style={[styles.previewText, { color: colors.foreground }]} numberOfLines={3}>
              {pcClipboard}
            </Text>
          </View>
        )}

        <TouchableOpacity
          onPress={onClose}
          style={[styles.closeButton, { borderColor: colors.border }]}
        >
          <Text style={[styles.closeButtonText, { color: colors.foreground }]}>
            Cerrar
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  container: {
    width: '85%',
    maxWidth: 450,
    borderRadius: 16,
    borderWidth: 1,
    padding: 20,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  actions: {
    gap: 12,
    marginBottom: 20,
  },
  actionButton: {
    padding: 20,
    borderRadius: 12,
    borderWidth: 2,
    alignItems: 'center',
  },
  actionIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  actionLabel: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 4,
  },
  actionDescription: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.8)',
    textAlign: 'center',
  },
  preview: {
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    marginBottom: 20,
  },
  previewLabel: {
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 6,
  },
  previewText: {
    fontSize: 14,
    lineHeight: 20,
  },
  closeButton: {
    padding: 14,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: 'center',
  },
  closeButtonText: {
    fontSize: 16,
    fontWeight: '600',
  },
});
