/**
 * Componente de visualización del escritorio remoto
 * Muestra los frames recibidos del servidor y maneja gestos táctiles avanzados
 */

import { useState, useRef, useEffect } from 'react';
import { View, Image, StyleSheet, Dimensions, type GestureResponderEvent } from 'react-native';
import { Gesture, GestureDetector, GestureHandlerRootView } from 'react-native-gesture-handler';
import { TCPClient, type Frame } from '@/lib/tcp-client';

interface RemoteDesktopViewProps {
  client: TCPClient;
  onDisconnect?: () => void;
  onEdgeSwipe?: () => void;
}

export function RemoteDesktopView({ client, onDisconnect, onEdgeSwipe }: RemoteDesktopViewProps) {
  const [frameUri, setFrameUri] = useState<string | null>(null);
  const [desktopSize, setDesktopSize] = useState({ width: 1920, height: 1080 });
  const screenSize = Dimensions.get('window');
  
  // Estado de zoom y pan
  const [scale, setScale] = useState(1);
  const [translateX, setTranslateX] = useState(0);
  const [translateY, setTranslateY] = useState(0);
  
  // Calcular escala base para ajustar el escritorio a la pantalla
  const baseScale = Math.min(
    screenSize.width / desktopSize.width,
    screenSize.height / desktopSize.height
  );
  
  const displayWidth = desktopSize.width * baseScale * scale;
  const displayHeight = desktopSize.height * baseScale * scale;
  
  // Estado del mouse
  const mousePos = useRef({ x: 0, y: 0 });
  const mouseButtons = useRef(0);
  const longPressTimer = useRef<NodeJS.Timeout | null>(null);
  
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
  
  function updateMousePosition(x: number, y: number) {
    // Ajustar por zoom y pan
    const adjustedX = (x - translateX) / scale;
    const adjustedY = (y - translateY) / scale;
    
    // Convertir coordenadas de pantalla a coordenadas del escritorio
    const desktopX = Math.round((adjustedX / displayWidth) * desktopSize.width);
    const desktopY = Math.round((adjustedY / displayHeight) * desktopSize.height);
    
    mousePos.current = { 
      x: Math.max(0, Math.min(desktopSize.width, desktopX)), 
      y: Math.max(0, Math.min(desktopSize.height, desktopY)) 
    };
  }
  
  function sendMouseEvent() {
    client.sendMouseEvent(
      mousePos.current.x,
      mousePos.current.y,
      mouseButtons.current
    );
  }
  
  // Gesto de tap simple (click izquierdo)
  const tapGesture = Gesture.Tap()
    .numberOfTaps(1)
    .onStart((event) => {
      updateMousePosition(event.x, event.y);
      mouseButtons.current = 1; // Botón izquierdo
      sendMouseEvent();
    })
    .onEnd(() => {
      mouseButtons.current = 0;
      sendMouseEvent();
    });
  
  // Gesto de tap largo (click derecho)
  const longPressGesture = Gesture.LongPress()
    .minDuration(500)
    .onStart((event) => {
      updateMousePosition(event.x, event.y);
      mouseButtons.current = 2; // Botón derecho
      sendMouseEvent();
    })
    .onEnd(() => {
      mouseButtons.current = 0;
      sendMouseEvent();
    });
  
  // Gesto de pan con un dedo (mover mouse)
  const panGesture = Gesture.Pan()
    .minPointers(1)
    .maxPointers(1)
    .onUpdate((event) => {
      updateMousePosition(event.x, event.y);
      mouseButtons.current = 1; // Simular arrastrar
      sendMouseEvent();
    })
    .onEnd(() => {
      mouseButtons.current = 0;
      sendMouseEvent();
    });
  
  // Gesto de scroll con dos dedos
  const scrollGesture = Gesture.Pan()
    .minPointers(2)
    .maxPointers(2)
    .onUpdate((event) => {
      // Enviar evento de scroll
      const scrollAmount = Math.round(event.translationY / 10);
      if (scrollAmount !== 0) {
        // TODO: Implementar mensaje de scroll en el protocolo
        // Por ahora, mover el pan de la vista
        setTranslateY(prev => prev + event.translationY);
      }
    });
  
  // Gesto de pinch para zoom
  const pinchGesture = Gesture.Pinch()
    .onUpdate((event) => {
      const newScale = Math.max(1, Math.min(3, event.scale));
      setScale(newScale);
    })
    .onEnd((event) => {
      const newScale = Math.max(1, Math.min(3, event.scale));
      setScale(newScale);
    });
  
  // Gesto de deslizar desde borde derecho (para salir del modo kiosko)
  const edgeSwipeGesture = Gesture.Pan()
    .minPointers(1)
    .maxPointers(1)
    .onStart((event) => {
      // Solo activar si empieza desde el borde derecho
      if (event.x > screenSize.width - 50 && onEdgeSwipe) {
        onEdgeSwipe();
      }
    })
    .enabled(!!onEdgeSwipe);
  
  // Combinar gestos
  const composedGesture = Gesture.Race(
    edgeSwipeGesture,
    longPressGesture,
    Gesture.Exclusive(
      pinchGesture,
      scrollGesture,
      Gesture.Simultaneous(tapGesture, panGesture)
    )
  );
  
  return (
    <GestureHandlerRootView style={styles.container}>
      <GestureDetector gesture={composedGesture}>
        <View style={styles.gestureContainer}>
          {frameUri ? (
            <Image
              source={{ uri: frameUri }}
              style={{
                width: displayWidth,
                height: displayHeight,
                transform: [
                  { translateX },
                  { translateY },
                ],
              }}
              resizeMode="contain"
            />
          ) : (
            <View style={styles.placeholder}>
              {/* Placeholder mientras se recibe el primer frame */}
            </View>
          )}
        </View>
      </GestureDetector>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  gestureContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  placeholder: {
    width: '100%',
    height: '100%',
    backgroundColor: '#1a1a1a',
  },
});
