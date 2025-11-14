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

    log("Captura de video iniciada. Presiona ESC para salir.", 'info')

    try:
        while True:
            rate(60)  # Limitar a 60 FPS para VPython
            ret, frame = cap.read()
            if not ret:
                log("Error: No se pudo leer el frame de la cámara", 'error')
                break

            # Detectar mano y landmarks
            frame, landmarks = detector.detect(frame)

            # Reconocer gesto
            gesture = recognizer.recognize(landmarks)

            # Escuchar gesto para historial
            listener.listen(gesture)

            # Ejecutar comando basado en gesto
            try:
                interpreter.execute(gesture)
            except Exception as e:
                log(f"Error ejecutando comando para gesto {gesture}: {str(e)}", 'error')

            # Loggear gesto detectado (solo si cambió)
            if gesture != recognizer.last_gesture:
                log(f"Gesto detectado: {gesture}", 'debug')

            # Mostrar frame de la cámara
            cv2.imshow("Camera Feed", frame)

            # Salir si se presiona ESC
            if cv2.waitKey(1) & 0xFF == 27:
                log("Saliendo de la aplicación", 'info')
                break

    except Exception as e:
        log(f"Error durante la ejecución: {str(e)}", 'error')
    finally:
        # Liberar recursos
        cap.release()
        cv2.destroyAllWindows()
        log("Recursos liberados", 'info')

if __name__ == "__main__":
    main()
