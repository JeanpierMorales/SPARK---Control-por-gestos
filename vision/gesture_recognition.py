import numpy as np

class GestureRecognizer:
    def __init__(self):
        self.last_gestures = {}

    def recognize(self, landmarks_list, handedness_list):
        gestures = {}
        for i, (landmarks, hand) in enumerate(zip(landmarks_list, handedness_list)):
            gesture = self._recognize_single(landmarks)
            gestures[hand] = gesture
            self.last_gestures[hand] = gesture
        return gestures

    def _recognize_single(self, landmarks):
        if not landmarks:
            return "none"

        lm = np.array(landmarks)

        # Coordenadas de los dedos clave
        thumb_tip = lm[4]  # Punta del pulgar
        index_tip = lm[8]  # Punta del índice
        middle_tip = lm[12]  # Punta del medio
        ring_tip = lm[16]  # Punta del anular
        pinky_tip = lm[20]  # Punta del meñique

        # Bases de los dedos para comparación
        thumb_base = lm[2]
        index_base = lm[5]
        middle_base = lm[9]
        ring_base = lm[13]
        pinky_base = lm[17]

        # Distancia entre pulgar e índice para pinch/open
        distance_thumb_index = np.linalg.norm(np.array(thumb_tip[:2]) - np.array(index_tip[:2]))

        # Verificar si el pulgar está arriba (thumb_up)
        thumb_extended_up = thumb_tip[1] < thumb_base[1]  # Pulgar hacia arriba
        thumb_extended_down = thumb_tip[1] > thumb_base[1]  # Pulgar hacia abajo
        index_folded = index_tip[1] > index_base[1]  # Índice doblado
        middle_folded = middle_tip[1] > middle_base[1]  # Medio doblado
        ring_folded = ring_tip[1] > ring_base[1]  # Anular doblado
        pinky_folded = pinky_tip[1] > pinky_base[1]  # Meñique doblado

        # Índice extendido arriba/abajo
        index_extended_up = index_tip[1] < index_base[1] and middle_folded and ring_folded and pinky_folded
        index_extended_down = index_tip[1] > index_base[1] and middle_folded and ring_folded and pinky_folded

        # Peace: índice y medio extendidos, otros doblados
        peace = (index_tip[1] < index_base[1]) and (middle_tip[1] < middle_base[1]) and ring_folded and pinky_folded

        # Mano cerrada: todos dedos doblados
        closed = index_folded and middle_folded and ring_folded and pinky_folded and not thumb_extended_up

        if thumb_extended_up and index_folded and middle_folded and ring_folded and pinky_folded:
            gesture = "thumb_up"
        elif thumb_extended_down and index_folded and middle_folded and ring_folded and pinky_folded:
            gesture = "thumb_down"
        elif index_extended_up:
            gesture = "index_up"
        elif index_extended_down:
            gesture = "index_down"
        elif peace:
            gesture = "peace"
        elif closed:
            gesture = "closed"
        elif distance_thumb_index < 0.05:
            gesture = "pinch"
        else:
            gesture = "open"

        return gesture
