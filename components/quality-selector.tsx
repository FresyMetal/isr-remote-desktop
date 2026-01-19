/**
 * Componente de Selector de Calidad de Video
 * Permite ajustar la calidad de la transmisión (Baja/Media/Alta)
 */

import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useColors } from '@/hooks/use-colors';

export type VideoQuality = 'low' | 'medium' | 'high';

interface QualitySelectorProps {
  currentQuality: VideoQuality;
  onQualityChange: (quality: VideoQuality) => void;
  visible: boolean;
  onClose: () => void;
}

const QUALITY_LABELS: Record<VideoQuality, string> = {
  low: 'Baja',
  medium: 'Media',
  high: 'Alta',
};

const QUALITY_DESCRIPTIONS: Record<VideoQuality, string> = {
  low: 'Menor calidad, menos datos',
  medium: 'Balance entre calidad y datos',
  high: 'Máxima calidad, más datos',
};

export function QualitySelector({ currentQuality, onQualityChange, visible, onClose }: QualitySelectorProps) {
  const colors = useColors();

  if (!visible) {
    return null;
  }

  function handleQualitySelect(quality: VideoQuality) {
    onQualityChange(quality);
    onClose();
  }

  return (
    <View style={[styles.overlay, { backgroundColor: 'rgba(0, 0, 0, 0.7)' }]}>
      <View style={[styles.container, { backgroundColor: colors.surface, borderColor: colors.border }]}>
        <Text style={[styles.title, { color: colors.foreground }]}>
          Calidad de Video
        </Text>

        <View style={styles.options}>
          {(['low', 'medium', 'high'] as VideoQuality[]).map((quality) => (
            <TouchableOpacity
              key={quality}
              onPress={() => handleQualitySelect(quality)}
              style={[
                styles.option,
                { 
                  backgroundColor: currentQuality === quality ? colors.primary : colors.background,
                  borderColor: colors.border,
                },
              ]}
            >
              <View style={styles.optionContent}>
                <Text 
                  style={[
                    styles.optionLabel, 
                    { color: currentQuality === quality ? '#fff' : colors.foreground }
                  ]}
                >
                  {QUALITY_LABELS[quality]}
                </Text>
                <Text 
                  style={[
                    styles.optionDescription, 
                    { color: currentQuality === quality ? 'rgba(255,255,255,0.8)' : colors.muted }
                  ]}
                >
                  {QUALITY_DESCRIPTIONS[quality]}
                </Text>
              </View>
              
              {currentQuality === quality && (
                <Text style={styles.checkmark}>✓</Text>
              )}
            </TouchableOpacity>
          ))}
        </View>

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
    width: '80%',
    maxWidth: 400,
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
  options: {
    gap: 12,
    marginBottom: 20,
  },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderRadius: 12,
    borderWidth: 2,
  },
  optionContent: {
    flex: 1,
  },
  optionLabel: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 4,
  },
  optionDescription: {
    fontSize: 13,
  },
  checkmark: {
    fontSize: 24,
    color: '#fff',
    marginLeft: 12,
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
