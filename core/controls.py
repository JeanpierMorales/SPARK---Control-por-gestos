import vpython

def change_color(sphere_obj, new_color=None):
    """
    Cambia el color de la esfera geodésica (objeto compound).
    Si new_color es None, cicla a través de colores predefinidos.
    """
    colors = [vpython.color.red, vpython.color.blue, vpython.color.green, vpython.color.yellow, vpython.color.magenta]
    if new_color is None:
        # Ciclar colores (asumiendo que sphere_obj tiene un atributo para rastrear)
        if not hasattr(sphere_obj, 'color_index'):
            sphere_obj.color_index = 0
        sphere_obj.color_index = (sphere_obj.color_index + 1) % len(colors)
        new_color = colors[sphere_obj.color_index]

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

def move_up(sphere_obj, amount=0.1):
    """
    Mueve la esfera hacia arriba en el eje Y.
    """
    sphere_obj.pos += vpython.vector(0, amount, 0)

def move_down(sphere_obj, amount=0.1):
    """
    Mueve la esfera hacia abajo en el eje Y.
    """
    sphere_obj.pos += vpython.vector(0, -amount, 0)

def rotate_clockwise(sphere_obj, angle=0.05):
    """
    Rota la esfera en sentido horario alrededor del eje Y.
    """
    sphere_obj.rotate(angle=angle, axis=vpython.vector(0, 1, 0))

def rotate_counterclockwise(sphere_obj, angle=0.05):
    """
    Rota la esfera en sentido antihorario alrededor del eje Y.
    """
    sphere_obj.rotate(angle=-angle, axis=vpython.vector(0, 1, 0))
