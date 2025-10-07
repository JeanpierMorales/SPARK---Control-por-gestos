class Config:
    websocket_url = "ws://localhost:8000"

    @staticmethod
    def load():
        # En el futuro puede cargar desde JSON o archivo .env
        return Config()
