/**
 * Componente de Teclado Virtual
 * Muestra/oculta el teclado nativo y envía teclas al servidor
 */

import { useState, useRef, useEffect } from 'react';
import { View, TextInput, TouchableOpacity, Text, StyleSheet, Keyboard } from 'react-native';
import { useColors } from '@/hooks/use-colors';
import { TCPClient } from '@/lib/tcp-client';

interface VirtualKeyboardProps {
  client: TCPClient;
  visible: boolean;
  onClose: () => void;
}

// Mapeo de teclas especiales a códigos de tecla
const KEY_CODES: Record<string, number> = {
  'Enter': 13,
  'Backspace': 8,
  'Tab': 9,
  'Escape': 27,
  'Space': 32,
  'ArrowLeft': 37,
  'ArrowUp': 38,
  'ArrowRight': 39,
  'ArrowDown': 40,
  'Delete': 46,
  'Home': 36,
  'End': 35,
  'PageUp': 33,
  'PageDown': 34,
};

export function VirtualKeyboard({ client, visible, onClose }: VirtualKeyboardProps) {
  const colors = useColors();
  const [text, setText] = useState('');
  const inputRef = useRef<TextInput>(null);
  const lastTextRef = useRef('');

  useEffect(() => {
    if (visible && inputRef.current) {
      // Enfocar el input para mostrar el teclado
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    } else {
      // Ocultar teclado
      Keyboard.dismiss();
    }
  }, [visible]);

  function handleTextChange(newText: string) {
    const lastText = lastTextRef.current;
    
    if (newText.length > lastText.length) {
      // Se agregó texto
      const addedText = newText.substring(lastText.length);
      for (const char of addedText) {
        sendChar(char);
      }
    } else if (newText.length < lastText.length) {
      // Se borró texto (Backspace)
      sendKeyCode(KEY_CODES['Backspace']);
    }
    
    lastTextRef.current = newText;
    setText(newText);
  }

  function sendChar(char: string) {
    const code = char.charCodeAt(0);
    client.sendKeyboardEvent(code, true);  // Key down
    setTimeout(() => {
      client.sendKeyboardEvent(code, false); // Key up
    }, 50);
  }

  function sendKeyCode(keyCode: number) {
    client.sendKeyboardEvent(keyCode, true);  // Key down
    setTimeout(() => {
      client.sendKeyboardEvent(keyCode, false); // Key up
    }, 50);
  }

  function handleSpecialKey(keyName: string) {
    const keyCode = KEY_CODES[keyName];
    if (keyCode) {
      sendKeyCode(keyCode);
    }
  }

  if (!visible) {
    return null;
  }

  return (
    <View style={[styles.container, { backgroundColor: colors.surface, borderTopColor: colors.border }]}>
      {/* Input oculto para capturar teclado */}
      <TextInput
        ref={inputRef}
        value={text}
        onChangeText={handleTextChange}
        autoFocus
        autoCorrect={false}
        autoCapitalize="none"
        style={[styles.hiddenInput, { color: colors.foreground }]}
        placeholder="Escribe aquí..."
        placeholderTextColor={colors.muted}
      />

      {/* Teclas especiales */}
      <View style={styles.specialKeys}>
        <TouchableOpacity
          onPress={() => handleSpecialKey('Escape')}
          style={[styles.specialKey, { backgroundColor: colors.background, borderColor: colors.border }]}
        >
          <Text style={[styles.specialKeyText, { color: colors.foreground }]}>Esc</Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => handleSpecialKey('Tab')}
          style={[styles.specialKey, { backgroundColor: colors.background, borderColor: colors.border }]}
        >
          <Text style={[styles.specialKeyText, { color: colors.foreground }]}>Tab</Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => handleSpecialKey('Enter')}
          style={[styles.specialKey, { backgroundColor: colors.background, borderColor: colors.border }]}
        >
          <Text style={[styles.specialKeyText, { color: colors.foreground }]}>↵</Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => handleSpecialKey('Backspace')}
          style={[styles.specialKey, { backgroundColor: colors.background, borderColor: colors.border }]}
        >
          <Text style={[styles.specialKeyText, { color: colors.foreground }]}>⌫</Text>
        </TouchableOpacity>

        <View style={styles.spacer} />

        <TouchableOpacity
          onPress={() => handleSpecialKey('ArrowUp')}
          style={[styles.specialKey, { backgroundColor: colors.background, borderColor: colors.border }]}
        >
          <Text style={[styles.specialKeyText, { color: colors.foreground }]}>↑</Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => handleSpecialKey('ArrowDown')}
          style={[styles.specialKey, { backgroundColor: colors.background, borderColor: colors.border }]}
        >
          <Text style={[styles.specialKeyText, { color: colors.foreground }]}>↓</Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => handleSpecialKey('ArrowLeft')}
          style={[styles.specialKey, { backgroundColor: colors.background, borderColor: colors.border }]}
        >
          <Text style={[styles.specialKeyText, { color: colors.foreground }]}>←</Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => handleSpecialKey('ArrowRight')}
          style={[styles.specialKey, { backgroundColor: colors.background, borderColor: colors.border }]}
        >
          <Text style={[styles.specialKeyText, { color: colors.foreground }]}>→</Text>
        </TouchableOpacity>

        <View style={styles.spacer} />

        <TouchableOpacity
          onPress={onClose}
          style={[styles.closeButton, { backgroundColor: colors.error }]}
        >
          <Text style={styles.closeButtonText}>✕</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    borderTopWidth: 1,
    paddingBottom: 8,
  },
  hiddenInput: {
    height: 40,
    paddingHorizontal: 12,
    fontSize: 16,
  },
  specialKeys: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 8,
    paddingTop: 8,
    gap: 6,
  },
  specialKey: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    borderWidth: 1,
    minWidth: 50,
    alignItems: 'center',
  },
  specialKeyText: {
    fontSize: 14,
    fontWeight: '600',
  },
  spacer: {
    flex: 1,
  },
  closeButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
