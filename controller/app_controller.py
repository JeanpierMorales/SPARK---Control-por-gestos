from interface.ui_manager import UIManager
from video_stream.stream_handler import VideoStreamHandler
from comunicacion_web.websocket_client import WebSocketClient

class AppController:
    def __init__(self):
        self.ui = UIManager(controller=self)
        self.stream = None
        self.websocket = None

    def run(self):
        self.ui.run()

    # METODOS INVOCADOS POR LA UI
    def iniciar_captura(self):
        """Inicializa y arranca el flujo de video."""
        if not self.stream:
            self.stream = VideoStreamHandler(send_callback=self.on_gesture_detected)
        self.stream.start()

    def detener_captura(self):
        """Detiene la captura de video."""
        if self.stream:
            self.stream.stop()

    def conectar_ws(self, url: str) -> bool:
        """Intenta conectar al WebSocket. Devuelve True/False."""
        try:
            self.websocket = WebSocketClient(url)
            self.websocket.connect()
            return True
        except Exception as e:
            print("Error al conectar WS:", e)
            return False

    # CALLBACK DE GESTOS
    def on_gesture_detected(self, gesture_data: dict):
        print(f"Gesto detectado aca en Controlador: {gesture_data}")
        self.ui.actualizar_datos_pantalla(gesture_data)
        if self.websocket:
            self.websocket.send(gesture_data)
