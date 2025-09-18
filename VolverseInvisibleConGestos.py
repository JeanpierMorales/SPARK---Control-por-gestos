import cv2
import mediapipe as mp
import time
import numpy as np
import threading
import os
from playsound import playsound

# Función para reproducir el sonido en un hilo separado (evita bloquear el programa)
def play_magic_sound():
    if os.path.exists("magic_whoosh.wav"):  # Verifica si el archivo de sonido existe
        threading.Thread(
            target=lambda: playsound("magic_whoosh.wav"), daemon=True
        ).start()
    else:
        print("WARNING: Sound file 'magic_whoosh.wav' not found. Skipping sound.")

# Inicialización de Mediapipe para manos y segmentación de selfies
mp_hands = mp.solutions.hands
mp_selfie_segmentation = mp.solutions.selfie_segmentation
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)  # Detecta una mano con confianza mínima de 0.7
segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)  # Segmentación de persona en la imagen
mp_draw = mp.solutions.drawing_utils  # Utilidad para dibujar los puntos de la mano

# Abre la webcam
cap = cv2.VideoCapture(0)

time.sleep(2)  # Espera 2 segundos para que el usuario pueda salir del cuadro y capturar el fondo
ret, background = cap.read()  # Captura el fondo
if not ret:
    print("ERROR: Could not read from webcam. Exiting.")  # Si no se puede leer la cámara, termina el programa
    cap.release()
    exit(1)
background = cv2.flip(background, 1)  # Invierte la imagen del fondo horizontalmente

# Variables de estado
invisible = False  # Indica si el modo invisible está activo
last_gesture_time = 0  # Última vez que se detectó el gesto
gesture_cooldown = 1.0  # Tiempo mínimo entre gestos (segundos)
fade_frames = 20  # Número de frames para el efecto de desvanecimiento
fade_progress = 0  # Progreso del desvanecimiento
fading = False  # Indica si está ocurriendo el desvanecimiento
fade_direction = 1  # Dirección del desvanecimiento (1 = desaparecer, -1 = aparecer)

# Bucle principal
while True:
    ret, frame = cap.read()  # Lee un frame de la cámara
    if not ret:
        break  # Si no se puede leer, termina el bucle

    frame = cv2.flip(frame, 1)  # Invierte la imagen horizontalmente
    h, w, c = frame.shape  # Obtiene dimensiones del frame
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convierte el frame a RGB para Mediapipe

    # Detección de mano
    result = hands.process(rgb)
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)  # Dibuja los puntos de la mano

            landmarks = hand_landmarks.landmark  # Obtiene los puntos de la mano
            thumb_tip = landmarks[4]   # Punta del pulgar
            index_tip = landmarks[8]   # Punta del índice

            # Condición para gesto de "pulgar arriba"
            if (thumb_tip.y < index_tip.y and
                landmarks[12].y > landmarks[9].y and
                landmarks[16].y > landmarks[13].y and
                landmarks[20].y > landmarks[17].y):
                
                current_time = time.time()
                if current_time - last_gesture_time > gesture_cooldown:  # Verifica el tiempo entre gestos
                    invisible = not invisible  # Cambia el estado de invisibilidad
                    fade_direction = 1 if invisible else -1  # Define la dirección del desvanecimiento
                    fade_progress = 0  # Reinicia el progreso del fade
                    fading = True  # Activa el fade
                    last_gesture_time = current_time  # Actualiza el tiempo del último gesto

                    # Reproduce el sonido mágico
                    play_magic_sound()

    # Segmentación de la persona en el frame
    seg_result = segmentation.process(rgb)
    mask = seg_result.segmentation_mask  # Obtiene la máscara de segmentación

    # Suaviza la máscara para evitar bordes duros
    mask = cv2.GaussianBlur(mask, (15, 15), 0)
    condition = mask > 0.6  # Aplica un umbral fuerte para definir la zona de persona

    # Vista normal (sin efecto)
    output_frame = frame.copy()

    # Si está en modo invisible o desvaneciendo
    if invisible or fading:
        replaced = np.where(condition[..., None], background, frame)  # Reemplaza la zona de persona por el fondo

        if fading:
            alpha = fade_progress / fade_frames  # Calcula el nivel de transparencia
            if fade_direction == -1:
                alpha = 1 - alpha  # Invierte el fade si está apareciendo

            # Mezcla suavemente los frames para un efecto de transición
            output_frame = cv2.addWeighted(replaced, alpha, frame, 1 - alpha, 0)

            fade_progress += 1  # Avanza el fade
            if fade_progress > fade_frames:
                fading = False  # Termina el fade
                output_frame = replaced if invisible else frame  # Muestra el frame final según el estado
        else:
            output_frame = replaced  # Si no hay fade, muestra el frame reemplazado

    # Muestra el resultado en una ventana
    cv2.imshow("🪄 Invisibility Cloak (Smooth + WAV Sound)", output_frame)

    # Salir si se presiona 'q' o ESC
    if cv2.waitKey(1) & 0xFF in [ord('q'), 27]:
        break

# Libera la cámara y cierra las ventanas
cap.release()
cv2.destroyAllWindows()
