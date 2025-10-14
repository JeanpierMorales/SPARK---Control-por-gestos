# hand_cursor.py - Control de cursor del mouse con gestos de la mano
# Este script permite mover el cursor del mouse usando el dedo índice detectado por MediaPipe.
# Incluye suavizado para movimientos fluidos.

import sys
sys.path.insert(0, 'C:\\Users\\Omar Morales Silva\\Desktop\\Spark\\sparkEnv\\Lib\\site-packages')

import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Obtener las dimensiones de la pantalla
screen_width, screen_height = pyautogui.size()

# Iniciar la cámara
cap = cv2.VideoCapture(0)

# Variables para suavizar el movimiento del cursor
smoothening = 9
prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0

print("Iniciando el control de gestos... Mueve tu dedo índice para mover el cursor.")
print("Para salir, cierra la ventana de la cámara o presiona 'q'.")

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    # Voltear la imagen horizontalmente para una vista de "selfie"
    image = cv2.flip(image, 1)

    # Convertir la imagen BGR a RGB para MediaPipe
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Procesar la imagen y detectar manos
    results = hands.process(image_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Dibujar los landmarks y conexiones de la mano
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Obtener las coordenadas de la punta del dedo índice (landmark 8)
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # Convertir las coordenadas de los landmarks a píxeles
            h, w, c = image.shape
            x = int(index_finger_tip.x * w)
            y = int(index_finger_tip.y * h)

            # Convertir las coordenadas de la cámara a coordenadas de pantalla
            screen_x = np.interp(x, (0, w), (0, screen_width))
            screen_y = np.interp(y, (0, h), (0, screen_height))

            # Suavizar el movimiento del cursor
            curr_x = prev_x + (screen_x - prev_x) / smoothening
            curr_y = prev_y + (screen_y - prev_y) / smoothening

            # Mover el cursor del mouse
            pyautogui.moveTo(curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

    # Mostrar la imagen en una ventana
    cv2.imshow('Hand Gesture Control', image)

    # Salir del bucle si se presiona la tecla 'q'
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

# Liberar la cámara y destruir todas las ventanas
cap.release()
cv2.destroyAllWindows()
