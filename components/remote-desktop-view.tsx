/**
 * Componente de visualización del escritorio remoto
 * Muestra los frames recibidos del servidor y maneja gestos táctiles
 */

import { useState, useRef, useEffect } from 'react';
import { View, Image, StyleSheet, Dimensions, PanResponder, type GestureResponderEvent, type PanResponderGestureState } from 'react-native';
import { TCPClient, type Frame } from '@/lib/tcp-client';

interface RemoteDesktopViewProps {
  client: TCPClient;
  onDisconnect?: () => void;
}

export function RemoteDesktopView({ client, onDisconnect }: RemoteDesktopViewProps) {
  const [frameUri, setFrameUri] = useState<string | null>(null);
  const [desktopSize, setDesktopSize] = useState({ width: 1920, height: 1080 });
  const screenSize = Dimensions.get('window');
  
  // Calcular escala para ajustar el escritorio a la pantalla
  const scale = Math.min(
    screenSize.width / desktopSize.width,
    screenSize.height / desktopSize.height
  );
  
  const displayWidth = desktopSize.width * scale;
  const displayHeight = desktopSize.height * scale;
  
  // Estado del mouse
  const mousePos = useRef({ x: 0, y: 0 });
  const mouseButtons = useRef(0);
  
  useEffect(() => {
    // Configurar cliente TCP para recibir frames
    const originalOnFrame = client['events'].onFrame;
    
    client['events'].onFrame = (frame: Frame) => {
      handleFrame(frame);
      if (originalOnFrame) {
        originalOnFrame(frame);
      }
    };
    
    return () => {
      // Restaurar handler original
      if (originalOnFrame) {
        client['events'].onFrame = originalOnFrame;
      }
    };
  }, [client]);
  
  function handleFrame(frame: Frame) {
    try {
      // Actualizar tamaño del escritorio
      if (frame.width !== desktopSize.width || frame.height !== desktopSize.height) {
        setDesktopSize({ width: frame.width, height: frame.height });
      }
      
      // Convertir frame JPEG a base64 para mostrar en Image
      if (frame.encoding === 1) { // JPEG
        const base64 = arrayBufferToBase64(frame.data);
        setFrameUri(`data:image/jpeg;base64,${base64}`);
      }
    } catch (error) {
      console.error('[RemoteDesktopView] Error al procesar frame:', error);
    }
  }
  
  // Convertir Uint8Array a base64
  function arrayBufferToBase64(buffer: Uint8Array): string {
    let binary = '';
    const len = buffer.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(buffer[i]);
    }
    return btoa(binary);
  }
  
  // Crear PanResponder para manejar gestos táctiles
  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onMoveShouldSetPanResponder: () => true,
      
      onPanResponderGrant: (evt: GestureResponderEvent) => {
        // Touch down - simular click del mouse
        const { locationX, locationY } = evt.nativeEvent;
        updateMousePosition(locationX, locationY);
        mouseButtons.current = 1; // Botón izquierdo presionado
        sendMouseEvent();
      },
      
      onPanResponderMove: (evt: GestureResponderEvent, gestureState: PanResponderGestureState) => {
        // Movimiento del dedo - mover el mouse
        const { locationX, locationY } = evt.nativeEvent;
        updateMousePosition(locationX, locationY);
        sendMouseEvent();
      },
      
      onPanResponderRelease: () => {
        // Touch up - soltar botón del mouse
        mouseButtons.current = 0;
        sendMouseEvent();
      },
    })
  ).current;
  
  function updateMousePosition(x: number, y: number) {
    // Convertir coordenadas de pantalla a coordenadas del escritorio
    const desktopX = Math.round((x / displayWidth) * desktopSize.width);
    const desktopY = Math.round((y / displayHeight) * desktopSize.height);
    
    mousePos.current = { x: desktopX, y: desktopY };
  }
  
  function sendMouseEvent() {
    client.sendMouseEvent(
      mousePos.current.x,
      mousePos.current.y,
      mouseButtons.current
    );
  }
  
  return (
    <View style={styles.container} {...panResponder.panHandlers}>
      {frameUri ? (
        <Image
          source={{ uri: frameUri }}
          style={{
            width: displayWidth,
            height: displayHeight,
          }}
          resizeMode="contain"
        />
      ) : (
        <View style={styles.placeholder}>
          {/* Placeholder mientras se recibe el primer frame */}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    alignItems: 'center',
    justifyContent: 'center',
  },
  placeholder: {
    width: '100%',
    height: '100%',
    backgroundColor: '#1a1a1a',
  },
});
