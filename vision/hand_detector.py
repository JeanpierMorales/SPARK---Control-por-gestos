import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self, detection_confidence=0.7, max_hands=2):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils

    def detect(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        landmarks = []
        handedness = []

        if results.multi_hand_landmarks and results.multi_handedness:
            for handLms, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                self.mp_draw.draw_landmarks(frame, handLms, self.mp_hands.HAND_CONNECTIONS)
                landmarks.append([(lm.x, lm.y, lm.z) for lm in handLms.landmark])
                handedness.append(hand_handedness.classification[0].label)  # 'Left' or 'Right'

        return frame, landmarks, handedness
