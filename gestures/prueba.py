# prueba.py - Programa de prueba para control de gestos con mouse
# Este script permite controlar el mouse con gestos de la mano usando MediaPipe y PyAutoGUI.
# Funcionalidad: Mover cursor con dedo índice, clic con pellizco índice-pulgar.

import sys
sys.path.insert(0, 'C:\\Users\\Omar Morales Silva\\Desktop\\Spark\\sparkEnv\\Lib\\site-packages')

import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math

# ==== CONFIGURACIÓN ====
sensibilidad = 1.3   # 🔧 Controla la velocidad del puntero (1.0 = normal)
suavizado = 6        # 🔧 Controla la fluidez (más alto = más suave pero más lento)
click_umbral_cerca = 40
click_umbral_lejos = 50
# ========================

# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_drawing = mp.solutions.drawing_utils

# Obtener dimensiones de pantalla
screen_width, screen_height = pyautogui.size()

# Captura de video
cap = cv2.VideoCapture(0)

# Variables para suavizar movimiento del cursor
prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0
click_held = False  # Estado de clic

print("🖐 Control de mouse activado:")
print(" - Mueve tu dedo índice para mover el cursor.")
print(" - Junta índice y pulgar para hacer clic una sola vez.")
print(" - Presiona 'q' para salir.")

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    image = cv2.flip(image, 1)
    h, w, _ = image.shape

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_image)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Coordenadas de índice y pulgar
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

            # Convertir a píxeles
            ix, iy = int(index_tip.x * w), int(index_tip.y * h)
            tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)

            # Calcular distancia entre índice y pulgar
            distance = math.hypot(tx - ix, ty - iy)

            # --- Movimiento del cursor ---
            # Aplicar sensibilidad y suavizado
            screen_x = np.interp(ix, (0, w), (0, screen_width * sensibilidad))
            screen_y = np.interp(iy, (0, h), (0, screen_height * sensibilidad))

            curr_x = prev_x + (screen_x - prev_x) / suavizado
            curr_y = prev_y + (screen_y - prev_y) / suavizado
            pyautogui.moveTo(curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

            # --- Detección de gesto "pellizco" ---
            if distance < click_umbral_cerca and not click_held:
                pyautogui.click()
                click_held = True
                cv2.putText(image, "CLICK!", (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            elif distance >= click_umbral_lejos:
                click_held = False

            # Visuales para depuración
            cv2.circle(image, (ix, iy), 10, (255, 0, 0), -1)
            cv2.circle(image, (tx, ty), 10, (0, 255, 0), -1)
            cv2.line(image, (ix, iy), (tx, ty), (255, 255, 255), 2)

    cv2.imshow("Hand Mouse Control", image)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
