import tkinter as tk
from tkinter import messagebox

class UIManager:
    def __init__(self, controller=None):
        self.controller = controller  # Puede ser None si se ejecuta en modo prueba
        
        self.root = tk.Tk()
        self.root.title("Proyecto Control X Gestos")
        self.root.geometry("350x350")

        # Variables de estado
        self.estado_captura = tk.StringVar(value="Apagado")
        self.estado_conexion = tk.StringVar(value="Desconectado")
        self.url_ws = tk.StringVar(value="ws://localhost:8000")

        self._generar_interfaz()

    def _generar_interfaz(self):
        """Genera y configura la interfaz completa"""
        # Sección superior: estado e inicio
        tk.Label(self.root, text="Estado del sistema:").pack(pady=(10, 0))
        self.label_estado = tk.Label(self.root, textvariable=self.estado_captura, font=("Arial", 12, "bold"))
        self.label_estado.pack(pady=5)

        self.boton_inicio = tk.Button(
            self.root,
            text="Iniciar",
            command=self._on_toggle_inicio,
            width=12
        )
        self.boton_inicio.pack(pady=5)

        # Sección central: conexión WebSocket
        frame_conexion = tk.Frame(self.root)
        frame_conexion.pack(pady=(15, 5))

        tk.Label(frame_conexion, text="Endpoint WebSocket:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.input_url = tk.Entry(frame_conexion, textvariable=self.url_ws, width=25)
        self.input_url.grid(row=0, column=1, padx=5, pady=5)
        
        self.boton_conectar = tk.Button(
            frame_conexion,
            text="Conectarse",
            command=self._on_conectar
        )
        self.boton_conectar.grid(row=0, column=2, padx=5)

        # Campo de texto de estado de conexión
        tk.Label(self.root, text="Estado conexión:").pack(pady=(10, 0))
        self.label_conexion = tk.Label(self.root, textvariable=self.estado_conexion, font=("Arial", 10))
        self.label_conexion.pack(pady=5)

        # Campo informativo (último gesto detectado)
        self.label_gesto = tk.Label(self.root, text="Esperando gesto...", font=("Arial", 11))
        self.label_gesto.pack(pady=(15, 10))

    # EVENTOS DE BOTONES
    def _on_toggle_inicio(self):
        """Alterna el estado de captura."""
        if self.estado_captura.get() == "Apagado":
            self.estado_captura.set("Encendido")
            self.boton_inicio.config(text="Detener")
            if self.controller:
                self.controller.iniciar_captura()
        else:
            self.estado_captura.set("Apagado")
            self.boton_inicio.config(text="Iniciar")
            if self.controller:
                self.controller.detener_captura()

    def _on_conectar(self):
        """Intentar conexión WebSocket"""
        url = self.url_ws.get()
        if not self.controller:
            messagebox.showinfo("Sin controlador", "No hay controlador asignado.")
            return

        exito = self.controller.conectar_ws(url)
        if exito:
            self.estado_conexion.set("Conectado")
            self.input_url.config(state="disabled")
            self.boton_conectar.config(state="disabled")
        else:
            self.estado_conexion.set("Desconectado")
            messagebox.showerror("Error de conexión", "No se pudo conectar al WebSocket.")

    # MÉTODOS PÚBLICOS DE ACTUALIZACIÓN
    def actualizar_datos_pantalla(self, gesture_data: dict):
        """Actualiza la etiqueta con el último gesto detectado."""
        gesture_text = f"Gesto: {gesture_data.get('type', 'Desconocido')}"
        self.label_gesto.config(text=gesture_text)

    def run(self):
        self.root.mainloop()
