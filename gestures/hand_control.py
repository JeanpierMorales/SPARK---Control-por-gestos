# hand_control.py - Control básico de gestos con detección de pulgar arriba
# Este script detecta gestos simples de la mano usando MediaPipe y ejecuta acciones
# como clics del mouse basados en el gesto detectado.

import sys
sys.path.insert(0, 'C:\\Users\\Omar Morales Silva\\Desktop\\Spark\\sparkEnv\\Lib\\site-packages')

import cv2
import mediapipe as mp
import pyautogui

# Inicialización de MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,           # Solo una mano
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Captura de video
cap = cv2.VideoCapture(0)

def detectar_gesto(landmarks):
    """
    Función para detectar gestos según landmarks.
    Recibe la lista de puntos de la mano y devuelve un string con el gesto.
    """
    # Ejemplo básico: solo reconocemos si el pulgar está levantado
    pulgar = landmarks[4]  # punta del pulgar
    indice = landmarks[8]  # punta del índice

    if pulgar.y < indice.y:
        return "pulgar_arriba"
    return "ninguno"

def ejecutar_accion(gesto):
    """
    Ejecuta acción según el gesto detectado.
    """
    if gesto == "pulgar_arriba":
        print("Pulgar arriba detectado: clic izquierdo")
        pyautogui.click()  # clic izquierdo
    # Agrega más gestos y acciones aquí

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # espejo
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            # Extraer landmarks como lista
            landmarks = handLms.landmark
            gesto = detectar_gesto(landmarks)
            ejecutar_accion(gesto)

    cv2.imshow("Control por Gestos", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Esc para salir
        break

cap.release()
cv2.destroyAllWindows()
