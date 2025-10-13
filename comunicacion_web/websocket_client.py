import json
import websocket

# Clase para controlar los datos que llegaran a la web
class WebSocketClient:
    def __init__(self, url: str):
        self.url = url
        self.ws : websocket.WebSocket = None # type: ignore

    def connect(self):
        #self.ws = websocket.WebSocket()
        #self.ws.connect(self.url)
        print("SIMULANDO UNA CONEXION EXITOSA")

    def send(self, gesture_data: dict):
        if not self.ws:
            self.connect()
        #self.ws.send(json.dumps(gesture_data))
        print("Simulando un envio de esta data: ")
