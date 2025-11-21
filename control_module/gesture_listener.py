class GestureListener:
    def __init__(self):
        self.active = True
        self.gesture_history = []  # Historial de gestos para análisis futuro

    def listen(self, gestures):
        """
        Escucha y registra gestos detectados.
        Puede expandirse para análisis de patrones o integración con IA.

        Parámetros:
        - gestures: Los gestos detectados (dict con 'Left' y 'Right')
        """
        if self.active:
            self.gesture_history.append(gestures)
            # Mantener solo los últimos 100 gestos para no consumir mucha memoria
            if len(self.gesture_history) > 100:
                self.gesture_history.pop(0)
            # Aquí se puede agregar lógica para detectar patrones o enviar a modelos IA

    def get_recent_gestures(self, count=10):
        """
        Devuelve los gestos más recientes.
        
        Parámetros:
        - count: Número de gestos a devolver
        
        Retorna:
        - Lista de los últimos 'count' gestos
        """
        return self.gesture_history[-count:] if len(self.gesture_history) >= count else self.gesture_history

    def clear_history(self):
        """
        Limpia el historial de gestos.
        """
        self.gesture_history.clear()
