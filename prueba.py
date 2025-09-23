#--- Pintar con gestos usando MediaPipe y OpenCV ---
# Este script permite dibujar en la pantalla utilizando gestos de la mano capturados por la cámara web.
import cv2
import mediapipe as mp
import numpy as np
import time

# --- Inicialización de MediaPipe Hands ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

# --- Parámetros de dibujo ---
draw_color = (0, 0, 255)  # Color por defecto: Rojo (BGR)
brush_thickness = 10
eraser_thickness = 50

# --- Lienzo y variables de estado ---
canvas = None
prev_x, prev_y = -1, -1
erase_mode = False

# --- Paleta de colores y UI ---
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255), (255, 255, 255)] # Azul, Verde, Rojo, Amarillo, Blanco
color_names = ["Blue", "Green", "Red", "Yellow", "White"]
color_rect_height = 50
color_rect_width = 80
toolbar_y = 0

last_toolbar_action = 0  # Para evitar acciones repetidas en la barra

def draw_ui(frame):
    """
    Dibuja la barra de herramientas (paleta de colores, borrador, limpiar) y el indicador de modo.
    """
    for i, color in enumerate(colors):
        cv2.rectangle(frame, (i * color_rect_width, toolbar_y),
                      ((i + 1) * color_rect_width, toolbar_y + color_rect_height),
                      color, -1)
        cv2.putText(frame, color_names[i], (i * color_rect_width + 5, toolbar_y + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    # Botón borrador
    cv2.rectangle(frame, (len(colors) * color_rect_width, toolbar_y),
                  ((len(colors) + 1) * color_rect_width, toolbar_y + color_rect_height),
                  (100, 100, 100), -1)
    cv2.putText(frame, "Eraser", (len(colors) * color_rect_width + 5, toolbar_y + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    # Botón limpiar
    cv2.rectangle(frame, ((len(colors) + 1) * color_rect_width, toolbar_y),
                  ((len(colors) + 2) * color_rect_width, toolbar_y + color_rect_height),
                  (100, 100, 100), -1)
    cv2.putText(frame, "Clear", ((len(colors) + 1) * color_rect_width + 5, toolbar_y + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    # Indicador de modo actual
    if erase_mode:
        text = "Mode: Eraser"
        color_indicator = (100, 100, 100)
    else:
        text = "Mode: Draw"
        color_indicator = draw_color
    cv2.putText(frame, text, (10, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.circle(frame, (100, frame.shape[0] - 20), 10, color_indicator, -1)

# --- Inicialización de la cámara ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
canvas = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

print("Press 'q' to quit.")
print("Press 's' to save your artwork.")

cv2.namedWindow("Air Canvas", cv2.WINDOW_NORMAL)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    draw_ui(frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Coordenadas de la punta del índice y pulgar
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            h, w, c = frame.shape
            x, y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
            cv2.circle(frame, (x, y), 10, (255, 255, 0), -1)

            # --- Detección de gestos ---
            # Palma abierta (limpiar lienzo)
            is_open_palm = (
                hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].y and
                hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y and
                hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].y and
                hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP].y and
                abs(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x - hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP].x) > 0.1
            )

            if is_open_palm and y > toolbar_y + color_rect_height:
                canvas = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
                cv2.putText(frame, "Canvas Cleared!", (w // 2 - 100, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                prev_x, prev_y = -1, -1
                time.sleep(1)

            # Índice arriba (dibujo o selección de herramienta)
            is_index_finger_up = (
                index_finger_tip.y < hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].y and
                hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y > hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y and
                hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y > hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].y and
                hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y > hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP].y
            )

            if is_index_finger_up:
                # Si el dedo está sobre la barra de herramientas
                if y <= toolbar_y + color_rect_height:
                    now = time.time()
                    if now - last_toolbar_action > 0.5:  # "debounce" para evitar repeticiones
                        for i, color in enumerate(colors):
                            if (i * color_rect_width) < x < ((i + 1) * color_rect_width):
                                draw_color = color
                                erase_mode = False
                                prev_x, prev_y = -1, -1
                                last_toolbar_action = now
                                break
                        if (len(colors) * color_rect_width) < x < ((len(colors) + 1) * color_rect_width):
                            erase_mode = True
                            prev_x, prev_y = -1, -1
                            last_toolbar_action = now
                        if ((len(colors) + 1) * color_rect_width) < x < ((len(colors) + 2) * color_rect_width):
                            canvas = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
                            cv2.putText(frame, "Canvas Cleared!", (w // 2 - 100, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                            prev_x, prev_y = -1, -1
                            last_toolbar_action = now
                else:
                    # Dibuja en el lienzo
                    if prev_x != -1:
                        if erase_mode:
                            cv2.line(canvas, (prev_x, prev_y), (x, y), (0, 0, 0), eraser_thickness)
                        else:
                            cv2.line(canvas, (prev_x, prev_y), (x, y), draw_color, brush_thickness)
                    prev_x, prev_y = x, y
            else:
                prev_x, prev_y = -1, -1

    # --- Combina el lienzo con la imagen de la cámara ---
    gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, inv_mask = cv2.threshold(gray_canvas, 1, 255, cv2.THRESH_BINARY_INV)
    inv_mask = cv2.cvtColor(inv_mask, cv2.COLOR_GRAY2BGR)
    frame = cv2.bitwise_and(frame, inv_mask)
    frame = cv2.bitwise_or(frame, canvas)

    cv2.imshow("Air Canvas", frame)

    # --- Controles de teclado ---
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        filename = f"artwork_{int(time.time())}.png"
        cv2.imwrite(filename, canvas)
        print(f"Artwork saved as {filename}")

cap.release()
cv2.destroyAllWindows()