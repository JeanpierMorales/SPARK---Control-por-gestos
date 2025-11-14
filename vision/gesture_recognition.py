import numpy as np

class GestureRecognizer:
    def __init__(self):
        self.last_gesture = None

    def recognize(self, landmarks):
        if not landmarks:
            return "none"

        lm = np.array(landmarks[0])
        
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
        # El pulgar debe estar extendido y los otros dedos doblados
        thumb_extended = thumb_tip[1] < thumb_base[1]  # Pulgar hacia arriba (asumiendo coordenadas normalizadas)
        index_folded = index_tip[1] > index_base[1]  # Índice doblado
        middle_folded = middle_tip[1] > middle_base[1]  # Medio doblado
        ring_folded = ring_tip[1] > ring_base[1]  # Anular doblado
        pinky_folded = pinky_tip[1] > pinky_base[1]  # Meñique doblado
        
        if thumb_extended and index_folded and middle_folded and ring_folded and pinky_folded:
            gesture = "thumb_up"
        elif distance_thumb_index < 0.05:
            gesture = "pinch"
        else:
            gesture = "open"

        self.last_gesture = gesture
        return gesture
