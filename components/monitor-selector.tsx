/**
 * Componente de Selector de Monitores
 * Permite cambiar entre diferentes pantallas del PC remoto
 */

import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from 'react-native';
import { useColors } from '@/hooks/use-colors';
import type { Monitor } from '@/lib/tcp-client';

interface MonitorSelectorProps {
  monitors: Monitor[];
  currentMonitorId: number;
  onMonitorChange: (monitorId: number) => void;
  visible: boolean;
  onClose: () => void;
}

export function MonitorSelector({ 
  monitors, 
  currentMonitorId, 
  onMonitorChange, 
  visible, 
  onClose 
}: MonitorSelectorProps) {
  const colors = useColors();

  if (!visible) {
    return null;
  }

  function handleMonitorSelect(monitorId: number) {
    onMonitorChange(monitorId);
    onClose();
  }

  return (
    <View style={[styles.overlay, { backgroundColor: 'rgba(0, 0, 0, 0.7)' }]}>
      <View style={[styles.container, { backgroundColor: colors.surface, borderColor: colors.border }]}>
        <Text style={[styles.title, { color: colors.foreground }]}>
          Seleccionar Monitor
        </Text>

        {monitors.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={[styles.emptyText, { color: colors.muted }]}>
              No hay monitores disponibles
            </Text>
          </View>
        ) : (
          <ScrollView style={styles.scrollView}>
            <View style={styles.monitors}>
              {monitors.map((monitor) => (
                <TouchableOpacity
                  key={monitor.id}
                  onPress={() => handleMonitorSelect(monitor.id)}
                  style={[
                    styles.monitorCard,
                    { 
                      backgroundColor: currentMonitorId === monitor.id ? colors.primary : colors.background,
                      borderColor: colors.border,
                    },
                  ]}
                >
                  <View style={styles.monitorHeader}>
                    <Text 
                      style={[
                        styles.monitorName, 
                        { color: currentMonitorId === monitor.id ? '#fff' : colors.foreground }
                      ]}
                    >
                      {monitor.name}
                    </Text>
                    
                    {monitor.isPrimary && (
                      <View style={[styles.primaryBadge, { backgroundColor: colors.success }]}>
                        <Text style={styles.primaryText}>Principal</Text>
                      </View>
                    )}
                  </View>
                  
                  <Text 
                    style={[
                      styles.monitorResolution, 
                      { color: currentMonitorId === monitor.id ? 'rgba(255,255,255,0.8)' : colors.muted }
                    ]}
                  >
                    {monitor.width} × {monitor.height}
                  </Text>
                  
                  {/* Representación visual del monitor */}
                  <View style={styles.monitorPreview}>
                    <View 
                      style={[
                        styles.monitorScreen,
                        {
                          backgroundColor: currentMonitorId === monitor.id ? 'rgba(255,255,255,0.2)' : colors.border,
                          aspectRatio: monitor.width / monitor.height,
                        }
                      ]}
                    >
                      {currentMonitorId === monitor.id && (
                        <Text style={styles.checkmark}>✓</Text>
                      )}
                    </View>
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          </ScrollView>
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
    maxHeight: '80%',
    borderRadius: 16,
    borderWidth: 1,
    padding: 20,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
    textAlign: 'center',
  },
  scrollView: {
    maxHeight: 400,
  },
  monitors: {
    gap: 12,
    marginBottom: 20,
  },
  monitorCard: {
    padding: 16,
    borderRadius: 12,
    borderWidth: 2,
    marginBottom: 12,
  },
  monitorHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  monitorName: {
    fontSize: 18,
    fontWeight: '600',
    flex: 1,
  },
  primaryBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  primaryText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '600',
  },
  monitorResolution: {
    fontSize: 14,
    marginBottom: 12,
  },
  monitorPreview: {
    alignItems: 'center',
    paddingVertical: 8,
  },
  monitorScreen: {
    width: '80%',
    maxWidth: 200,
    borderRadius: 4,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 60,
  },
  checkmark: {
    fontSize: 32,
    color: '#fff',
  },
  emptyState: {
    paddingVertical: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    textAlign: 'center',
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
