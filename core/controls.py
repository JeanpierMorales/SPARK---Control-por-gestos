import vpython

def change_color(sphere_obj, new_color):
    """
    Cambia el color de la esfera geodésica (objeto compound).
    """
    # Para un objeto compound, necesitamos cambiar el color de cada sub-objeto
    # Nota: En VPython, los objetos compound no tienen atributo 'objects' directamente
    # Necesitamos acceder a los objetos internos de otra manera
    try:
        # Intentar acceder a los objetos internos del compound
        for obj in sphere_obj._objlist:
            obj.color = new_color
    except AttributeError:
        # Si no funciona, cambiar el color del compound directamente
        sphere_obj.color = new_color

def scale_sphere(sphere_obj, factor):
    """
    Escala la esfera geodésica (objeto compound).
    """
    # Para objetos compound, usar size en lugar de scale
    sphere_obj.size *= factor

def rotate_sphere(sphere_obj, angle_x=0.05, angle_y=0.05):
    """
    Rota la esfera geodésica (objeto compound) alrededor de los ejes X e Y.
    """
    sphere_obj.rotate(angle=angle_x, axis=vpython.vector(1, 0, 0))
    sphere_obj.rotate(angle=angle_y, axis=vpython.vector(0, 1, 0))
