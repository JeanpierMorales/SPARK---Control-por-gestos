from core.controls import change_color, scale_sphere, move_up, move_down, rotate_clockwise, rotate_counterclockwise

class CommandInterpreter:
    def __init__(self, sphere_obj):
        self.sphere = sphere_obj

    def execute(self, gestures):
        left_gesture = gestures.get("Left", "none")
        right_gesture = gestures.get("Right", "none")

        # Mano izquierda: control de tamaño
        if left_gesture == "open":
            scale_sphere(self.sphere, 1.02)  # Crecer
        elif left_gesture == "pinch":
            scale_sphere(self.sphere, 0.95)  # Disminuir
        elif left_gesture == "closed":
            pass  # Mantener tamaño

        # Mano derecha: movimiento, rotación, color
        if right_gesture == "thumb_up":
            move_up(self.sphere)
        elif right_gesture == "thumb_down":
            move_down(self.sphere)
        elif right_gesture == "index_up":
            rotate_clockwise(self.sphere)
        elif right_gesture == "index_down":
            rotate_counterclockwise(self.sphere)
        elif right_gesture == "peace":
            change_color(self.sphere)  # Ciclar colores
