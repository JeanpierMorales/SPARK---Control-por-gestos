from core.controls import change_color, scale_sphere
from vpython import color

class CommandInterpreter:
    def __init__(self, sphere_obj):
        self.sphere = sphere_obj

    def execute(self, gesture):
        if gesture == "pinch":
            scale_sphere(self.sphere, 0.95)
            change_color(self.sphere, color.red)
        elif gesture == "open":
            scale_sphere(self.sphere, 1.02)
            change_color(self.sphere, color.blue)
        elif gesture == "thumb_up":
            change_color(self.sphere, color.green)
        elif gesture == "none":
            pass
