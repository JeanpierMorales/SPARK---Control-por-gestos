# Importaciones necesarias para la aplicación SPARK
from core.render import setup_scene  # Configura la escena 3D con VPython
from core.controls import change_color, scale_sphere, rotate_sphere  # Funciones para controlar la esfera
from control_module.command_interpreter import CommandInterpreter  # Interpreta gestos en comandos
from control_module.gesture_listener import GestureListener  # Escucha gestos y mantiene historial
from vision.hand_detector import HandDetector  # Detecta manos usando MediaPipe
from vision.gesture_recognition import GestureRecognizer  # Reconoce gestos de la mano
from core.animator import auto_rotate  # Función para rotación automática
from utils.logger import log  # Función de logging mejorada
from vpython import rate, color  # Para control de frame rate y colores en VPython
import cv2  # Para captura de video con OpenCV
import threading  # Para ejecutar rotación automática en un hilo separado

def main():
    """
    Función principal de la aplicación SPARK.
    Inicializa la escena 3D, detectores de gestos y ejecuta el loop principal.
    """
    # Inicializar logger
    log("Iniciando aplicación SPARK", 'info')

    # Configurar escena y esfera
    scene, sphere_obj = setup_scene()
    log("Escena y esfera configuradas", 'info')

    # Inicializar componentes de visión
    detector = HandDetector()
    recognizer = GestureRecognizer()
    log("Detector de mano y reconocedor de gestos inicializados", 'info')

    # Inicializar interprete de comandos y listener de gestos
    interpreter = CommandInterpreter(sphere_obj)
    listener = GestureListener()
    log("Interprete de comandos y listener de gestos inicializados", 'info')

    # Iniciar rotación automática en un hilo separado
    # Nota: La rotación automática se ejecuta en paralelo, pero los controles por gestos tienen prioridad
    rotation_thread = threading.Thread(target=auto_rotate, args=(sphere_obj,))
    rotation_thread.daemon = True  # Hilo daemon para que termine con el programa principal
    rotation_thread.start()
    log("Rotación automática iniciada en hilo separado", 'info')

    # Captura de video
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        log("Error: No se pudo abrir la cámara", 'error')
        return

    # Configurar la ventana de la cámara para que ocupe toda la pantalla
    cv2.namedWindow("Camera Feed", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Camera Feed", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    log("Captura de video iniciada. Presiona ESC para salir.", 'info')

    frame_count = 0  # Contador de frames procesados

    try:
        while True:
            rate(60)  # Limitar a 60 FPS para VPython
            ret, frame = cap.read()
            if not ret:
                log("Error: No se pudo leer el frame de la cámara", 'error')
                break

            # Detectar mano y landmarks
            frame, landmarks, handedness = detector.detect(frame)

            # Reducir resolución del video para mejorar el rendimiento
            frame = cv2.resize(frame, (640, 480))

            # Corregir efecto espejo invirtiendo el marco horizontalmente
            frame = cv2.flip(frame, 1)

            # Procesar cada 2 marcos para optimizar el rendimiento
            if frame_count % 2 == 0:
                gestures = recognizer.recognize(landmarks, handedness)
                for hand, gesture in gestures.items():
                    listener.listen(gesture)

            # Ejecutar comandos basados en gestos
            try:
                interpreter.execute(gestures)
            except Exception as e:
                log(f"Error ejecutando comandos para gestos {gestures}: {str(e)}", 'error')

            # Loggear gestos detectados (solo si cambiaron)
            for hand, gesture in gestures.items():
                last = recognizer.last_gestures.get(hand, None)
                if gesture != last:
                    log(f"Gesto detectado en {hand}: {gesture}", 'debug')

            # Mostrar el marco procesado
            cv2.imshow("Camera Feed", frame)

            # Salir si se presiona ESC
            if cv2.waitKey(1) & 0xFF == 27:
                log("Saliendo de la aplicación", 'info')
                break

            frame_count += 1  # Incrementar contador de frames

    except Exception as e:
        log(f"Error durante la ejecución: {str(e)}", 'error')
    finally:
        # Liberar recursos
        cap.release()
        cv2.destroyAllWindows()
        log("Recursos liberados", 'info')

if __name__ == "__main__":
    main()