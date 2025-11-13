# hand_report.py
import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque
import os

from FSM import HandStateMachine

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Parameters
MAX_HANDS = 2
SMOOTHING_WINDOW = 5  # frames for simple smoothing of velocities

def landmarks_to_array(landmarks, image_shape):
    h, w = image_shape[:2]
    pts = []
    for lm in landmarks.landmark:
        x_px = int(lm.x * w)
        y_px = int(lm.y * h)
        z_rel = lm.z  # relative z (negative towards camera in MediaPipe)
        pts.append((x_px, y_px, z_rel))
    return np.array(pts, dtype=float)

def bounding_box_from_landmarks(pts):
    xs = pts[:,0]; ys = pts[:,1]
    x_min, x_max = xs.min(), xs.max()
    y_min, y_max = ys.min(), ys.max()
    return int(x_min), int(y_min), int(x_max), int(y_max)

def palm_normal(pts):
    # pick wrist (0), index_mcp (5), pinky_mcp (17)
    p0 = pts[0][:3]
    p1 = pts[5][:3]
    p2 = pts[17][:3]
    v1 = p1 - p0
    v2 = p2 - p0
    n = np.cross(v1, v2)
    n = n / (np.linalg.norm(n) + 1e-8)
    return n

def estimate_orientation(pts):
    # crude orientation estimate (radians)
    # forward vector wrist -> middle_finger_mcp (9)
    p0 = pts[0][:3]
    pf = pts[9][:3]
    f = pf - p0
    f = f / (np.linalg.norm(f) + 1e-8)

    n = palm_normal(pts)  # palm normal
    # Use f and n to define a local hand frame
    # yaw: rotation around vertical axis (approx): atan2(f.x, f.z)
    yaw  = np.arctan2(f[0], f[2])
    # pitch: rotation around lateral axis: atan2(f[1], f[2])
    pitch = np.arctan2(f[1], f[2])
    # roll: rotation around forward axis -> from palm normal
    roll = np.arctan2(n[1], n[2])
    # convert to degrees
    return np.degrees([roll, pitch, yaw])

def joint_angle(a, b, c):
    # angle at vertex b between vectors ba and bc
    ba = a - b
    bc = c - b
    na = ba / (np.linalg.norm(ba)+1e-8)
    nc = bc / (np.linalg.norm(bc)+1e-8)
    dot = np.clip(np.dot(na, nc), -1.0, 1.0)
    return np.degrees(np.arccos(dot))

def finger_curls(pts):
    # compute curl for each finger using MCP-PIP-DIP-TIP indices
    finger_idx = {
        'thumb':  [1, 2, 3, 4],
        'index':  [5, 6, 7, 8],
        'middle': [9,10,11,12],
        'ring':   [13,14,15,16],
        'pinky':  [17,18,19,20],
    }
    curls = {}
    for name, ids in finger_idx.items():
        mcp, pip, dip, tip = [pts[i][:3] for i in ids]
        # measure angle at pip (MCP-PIP-DIP) as rough curl indicator
        angle = joint_angle(mcp, pip, dip)
        curls[name] = angle
    return curls

def euclidean(a,b):
    return np.linalg.norm(a[:3] - b[:3])

def format_report(hand_id, handedness, score, pts, orientation_deg, curls, pinch_dist, bbox, wrist_vel=None):
    out = {
        "hand_id": hand_id,
        "handedness": handedness,
        "score": float(score),
        "bbox": bbox,
        "orientation_deg": {"roll": float(orientation_deg[0]), "pitch": float(orientation_deg[1]), "yaw": float(orientation_deg[2])},
        "pinch_distance_px": float(pinch_dist),
        "finger_curls_deg": curls,
        "landmarks": pts.tolist(),
    }
    if wrist_vel is not None:
        out["wrist_velocity_px_per_s"] = float(wrist_vel)
    return out


def imprimir_reporte(data_reporte):
    print("=== FRAME REPORT ===")
    for key, value in data_reporte.items():
        if key=="hands":
            if len(value)>0:
                for index, mano in enumerate(value):
                    print(f"MANO {index}:")
                    for llave, valor in mano.items():
                        if llave!="landmarks":
                            print(f"{llave}: {valor}")
                        else:
                            print(f"{key}: {value}")


def main():
    cap = cv2.VideoCapture(0)
    fsm = HandStateMachine(transition_delay=2.0)

    report = {}

    # Variables generales de control
    p_zoom = 0.0
    p_color = [0.0, 0.0, 0.0]
    p_rotation = 0.0
    p_move = [0.0, 0.0]


    def dibujar_estado_actual(image):
        # Draw the current FSM state on the top-left corner
        cv2.putText(image, f"STATE: {current_state}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2, cv2.LINE_AA)

    def dibujar_variables(image):
        # Draw your parameter values below
        color_texto = (0,0,0)
        cv2.putText(image, f"Zoom: {p_zoom:.2f}", (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_texto, 2, cv2.LINE_AA)
        cv2.putText(image, f"Color: {p_color[0]:.2f}, {p_color[1]:.2f}, {p_color[2]:.2f}", (30, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_texto, 2, cv2.LINE_AA)
        cv2.putText(image, f"Rotation: {p_rotation:.2f}", (30, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_texto, 2, cv2.LINE_AA)
        cv2.putText(image, f"Move: {p_move[0]:.2f}, {p_move[1]:.2f}", (30, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_texto, 2, cv2.LINE_AA)
        
        
        if current_state == "COLOR":
            color_display = tuple(int(c * 255) for c in p_color)
            cv2.rectangle(image, (30, 210), (130, 260), color_display, -1)
    
    # Variables para controlar los gestos
    base_pinch = 0
    base_pos = 0

    with mp_hands.Hands(static_image_mode=False,
                        max_num_hands=MAX_HANDS,
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5) as hands:

        prev_wrist_positions = {}
        wrist_vel_buffers = {}

        prev_time = time.time()
        
        # ===== Bucle principal del programa
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = hands.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            report = {"timestamp": time.time(), "hands": []}

            # ==== CALCULO DE DATOS DE LAS MANOS
            if results.multi_hand_landmarks:
                ih, iw = frame.shape[:2]
                for i, (landmarks, handedness) in enumerate(zip(results.multi_hand_landmarks,
                                                               results.multi_handedness)):
                    pts = landmarks_to_array(landmarks, frame.shape)
                    bbox = bounding_box_from_landmarks(pts)
                    orientation = estimate_orientation(pts)
                    curls = finger_curls(pts)
                    pinch_dist = euclidean(pts[4], pts[8])  # thumb tip(4) - index tip(8)
                    # wrist velocity
                    wrist = pts[0]
                    label = handedness.classification[0].label
                    score = handedness.classification[0].score

                    # smooth velocity over window
                    key = f"hand_{i}"
                    if key not in prev_wrist_positions:
                        prev_wrist_positions[key] = deque(maxlen=SMOOTHING_WINDOW)
                        wrist_vel_buffers[key] = deque(maxlen=SMOOTHING_WINDOW)
                    # push current wrist
                    prev_wrist_positions[key].append((wrist, time.time()))
                    # compute instantaneous velocity if we have previous
                    wrist_vel = None
                    if len(prev_wrist_positions[key]) >= 2:
                        p0, t0 = prev_wrist_positions[key][-2]
                        p1, t1 = prev_wrist_positions[key][-1]
                        dist = np.linalg.norm(p1[:2] - p0[:2])
                        dt = max(t1 - t0, 1e-6)
                        v = dist / dt
                        wrist_vel_buffers[key].append(v)
                        wrist_vel = float(np.mean(wrist_vel_buffers[key]))

                    # draw
                    mp_drawing.draw_landmarks(image, landmarks, mp_hands.HAND_CONNECTIONS)

                    rep = format_report(
                        hand_id=i,
                        handedness=label,
                        score=score,
                        pts=pts,
                        orientation_deg=orientation,
                        curls=curls,
                        pinch_dist=pinch_dist,
                        bbox=bbox,
                        wrist_vel=wrist_vel
                    )
                    report["hands"].append(rep)

                # inter-hand distance if two hands
                if len(report["hands"]) >= 2:
                    w0 = np.array(report["hands"][0]["landmarks"][0])
                    w1 = np.array(report["hands"][1]["landmarks"][0])
                    inter_hand = float(np.linalg.norm(w0[:2] - w1[:2]))
                    report["inter_hand_distance_px"] = inter_hand


            # ==== Imprimir el reporte
            os.system('cls')
            #imprimir_reporte(report)
            #ahorita no estoy imprimiendo nada


            # ==== FSM update and overlay ===
            current_state = fsm.update(report["hands"])
            print("Current FSM State:", current_state)

            # Reset the base pinch when entering ZOOM for the first time
            if current_state != "ZOOM":
                base_pinch = None
            if current_state != "MOVER":
                base_pos = None

            # === Behavior logic depending on FSM state ===

            if current_state == "COLOR":
                # Find right hand if available
                right_hand = next((h for h in report["hands"] if h["handedness"] == "Right"), None)
                if right_hand:
                    # Get wrist position
                    wrist = np.array(right_hand["landmarks"][0])[:2]
                    ih, iw = frame.shape[:2]

                    # Normalize position (0–1 range)
                    norm_x = wrist[0] / iw
                    norm_y = wrist[1] / ih

                    # Map to your color tuple (example: RGB with normalized values)
                    p_color = (norm_x, norm_y, 1 - norm_x)  # for testing — you’ll define your mapping later

            if current_state == "ZOOM":
                right_hand = next((h for h in report["hands"] if h["handedness"] == "Right"), None)
                if right_hand:
                    pinch_dist = right_hand["pinch_distance_px"]

                    # Initialize the base pinch when entering the state
                    if base_pinch is None:
                        base_pinch = pinch_dist

                    # Compute difference and update p_zoom proportionally
                    delta = pinch_dist - base_pinch
                    p_zoom += delta * 0.1  # adjust sensitivity if needed
                    base_pinch = pinch_dist  # update for smooth continuous control

            if current_state == "MOVER":
                left_hand = next((h for h in report["hands"] if h["handedness"] == "Right"), None)
                if left_hand:
                    # Extract the current wrist or palm center position (2D)
                    hand_pos = np.array(left_hand["landmarks"][0][:2])  # wrist coords in pixels

                    # Initialize reference position
                    if base_pos is None:
                        base_pos = hand_pos

                    # Compute displacement relative to base position
                    delta = hand_pos - base_pos

                    # Update the movement variable with scaled displacement
                    p_move[0] += delta[0] * 0.05  # scale factors tune sensitivity
                    p_move[1] += delta[1] * 0.05

                    # Update base for next frame (smooth continuous motion)
                    base_pos = hand_pos


            # ===== Dibujar los datos de reporte
            dibujar_estado_actual(image)

            dibujar_variables(image)


            # ===== Mostrar la camara (con todos los dibujos incluidos)
            cv2.imshow('Hand Report', image)


            # ===== Indicacion de cerrar en caso se presione Esc
            if cv2.waitKey(1) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
