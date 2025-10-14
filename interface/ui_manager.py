import tkinter as tk
from tkinter import messagebox
import subprocess
import os
from tkinter import ttk

class UIManager:
    def __init__(self, controller=None):
        self.controller = controller  # Puede ser None si se ejecuta en modo prueba
        
        self.root = tk.Tk()
        self.root.title("Proyecto Control X Gestos")
        self.root.geometry("400x450")

        # Variables de estado
        self.estado_captura = tk.StringVar(value="Apagado")
        self.estado_conexion = tk.StringVar(value="Desconectado")
        self.url_ws = tk.StringVar(value="ws://localhost:8000")
        self.selected_program = tk.StringVar(value="Seleccionar programa")

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

        # Sección de selección de programas
        frame_programas = tk.Frame(self.root)
        frame_programas.pack(pady=(10, 5))

        tk.Label(frame_programas, text="Programas de gestos:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_programas = ttk.Combobox(
            frame_programas,
            textvariable=self.selected_program,
            values=["Seleccionar programa", "Hand Control", "Hand Cursor", "Pintar Con Gestos", "Prueba", "Volverse Invisible"],
            state="readonly",
            width=20
        )
        self.combo_programas.grid(row=0, column=1, padx=5, pady=5)

        self.boton_lanzar = tk.Button(
            frame_programas,
            text="Lanzar Programa",
            command=self._on_lanzar_programa
        )
        self.boton_lanzar.grid(row=0, column=2, padx=5, pady=5)

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

    def _on_lanzar_programa(self):
        """Lanzar el programa seleccionado."""
        programa = self.selected_program.get()
        if programa == "Seleccionar programa":
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un programa para lanzar.")
            return

        # Mapear nombres a rutas de archivos en la carpeta gestures (integrada al MVC)
        programas_map = {
            "Hand Control": "gestures/hand_control.py",
            "Hand Cursor": "gestures/hand_cursor.py",
            "Pintar Con Gestos": "gestures/PintarConGestos.py",
            "Prueba": "gestures/prueba.py",
            "Volverse Invisible": "gestures/VolverseInvisibleConGestos.py"
        }

        script_path = programas_map.get(programa)
        if not script_path:
            messagebox.showerror("Error", "Programa no encontrado.")
            return

        # Verificar si el archivo existe
        if not os.path.exists(script_path):
            messagebox.showerror("Error", f"El archivo {script_path} no existe.")
            return

        try:
            # Lanzar el script en un proceso separado sin bloquear
            subprocess.Popen(["python", script_path])
            messagebox.showinfo("Programa lanzado", f"{programa} se ha lanzado correctamente.")
        except FileNotFoundError:
            messagebox.showerror("Error", "Python no encontrado en el PATH o archivo no existe.")
        except Exception as e:
            messagebox.showerror("Error al lanzar", f"No se pudo ejecutar el programa: {e}")

    # MÉTODOS PÚBLICOS DE ACTUALIZACIÓN
    def actualizar_datos_pantalla(self, gesture_data: dict):
        """Actualiza la etiqueta con el último gesto detectado."""
        gesture_text = f"Gesto: {gesture_data.get('type', 'Desconocido')}"
        self.label_gesto.config(text=gesture_text)

    def run(self):
        self.root.mainloop()
