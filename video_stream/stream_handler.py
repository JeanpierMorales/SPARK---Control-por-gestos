import cv2
import time

class VideoStreamHandler:
    def __init__(self, send_callback=None):
        """
        send_callback: función que se ejecuta cada vez que hay un nuevo dato para enviarlos a algun lugar
        """
        self.send_callback = send_callback or self.default_send
        self.capture = None
        self.running = False

    def default_send(self, data):
        """Método de envío por defecto: solo imprime los datos."""
        print("Datos listos para enviar:", data)

    def start(self):
        """Inicia el flujo de video (bloqueante y estable)."""
        try:
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                raise Exception("No se pudo acceder a la cámara.")

            self.running = True
            print("[VideoStream] Cámara iniciada. Presiona 'q' para salir.")

            while self.running:
                ret, frame = self.capture.read()
                if not ret:
                    time.sleep(0.05)
                    continue

                # Muestra la cámara
                cv2.imshow("Vista de la cámara", frame)

                # Simulación de procesamiento o detección
                gesture_data = {
                    "timestamp": time.time(),
                    "gesture": "wave",
                    "confidence": 0.92,
                }

                # Envía los datos (sin bloquear)
                self.send_callback(gesture_data)

                # Salida con 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.stop()

            self._release_resources()

        except Exception as e:
            print(f"[VideoStream] Error: {e}")
            self._release_resources()

    def stop(self):
        """Detiene el flujo."""
        if self.running:
            print("[VideoStream] Deteniendo flujo...")
        self.running = False

    def _release_resources(self):
        """Libera recursos."""
        if self.capture:
            self.capture.release()
        cv2.destroyAllWindows()
        print("[VideoStream] Cámara liberada y ventana cerrada.")
