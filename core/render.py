from vpython import canvas, color, vector
from .geometry import create_sphere

def setup_scene():
    # Configurar escena en pantalla completa ocupando toda la ventana del navegador
    scene = canvas(title="SPARK - Esfera Interactiva",
                   fullscreen=True,
                   background=color.gray(0.1),
                   width=1500,  # Ancho máximo para pantalla completa
                   height=750)  # Alto máximo para pantalla completa
    scene.camera.pos = vector(0, 0, 5)
    sphere_obj = create_sphere()
    return scene, sphere_obj
