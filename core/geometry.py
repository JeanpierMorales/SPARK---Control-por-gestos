import vpython
import math

# =================================================================
# FUNCIONES AUXILIARES DE GEOMETRÍA PARA ESFERA GEODÉSICA
# =================================================================

def normalizar_vector(vec):
    """
    Normaliza un vector (lo hace de longitud 1).
    """
    mag = vpython.mag(vec)
    if mag == 0:
        return vpython.vector(0, 0, 0)
    return vec / mag

def get_midpoint_index(p1, p2, all_vertices, cache, radius):
    """
    Calcula el punto medio entre dos vértices, lo proyecta a la esfera
    y devuelve el índice de ese nuevo punto. Si ya existe, devuelve el índice
    del punto cacheado, evitando duplicados.

    Parámetros:
    p1, p2 (vpython.vector): Los dos vectores de vértice.
    all_vertices (list): La lista global de vértices.
    cache (dict): El caché de puntos medios.
    radius (float): El radio de la esfera.
    """

    # Conversión crítica: Convertimos los vectores a tuplas de floats (x,y,z) para poder ordenarlos
    # Esto soluciona el 'TypeError' al usar 'sorted' con objetos vpython.vector.
    p1_tuple = (p1.x, p1.y, p1.z)
    p2_tuple = (p2.x, p2.y, p2.z)

    # Creamos una clave única e inmutable
    key = tuple(sorted((p1_tuple, p2_tuple)))

    if key in cache:
        return cache[key]

    # 1. Calcular y normalizar el nuevo punto (proyectado en la esfera)
    mid_vec = normalizar_vector((p1 + p2) / 2) * radius

    # 2. Añadir el nuevo punto a la lista global de vértices y cachear su índice
    new_index = len(all_vertices)
    all_vertices.append(mid_vec)
    cache[key] = new_index

    return new_index

# =================================================================
# GENERACIÓN DE LA ESFERA GEODÉSICA (WIRE-FRAME)
# =================================================================

def crear_malla_geodesica(radius, subdivisions, vertex_color, edge_color):
    """
    Genera la malla de la Esfera Geodésica mediante subdivisión del icosaedro
    y la renderiza usando cilindros (aristas) y esferas pequeñas (vértices).

    Retorna: Un objeto vpython.compound que contiene la malla completa.
    """
    t = (1 + math.sqrt(5)) / 2

    # 1. Vértices iniciales del Icosaedro
    initial_vectors = [
        vpython.vector(-1,  t,  0), vpython.vector( 1,  t,  0),
        vpython.vector(-1, -t,  0), vpython.vector( 1, -t,  0),
        vpython.vector( 0, -1,  t), vpython.vector( 0,  1,  t),
        vpython.vector( 0, -1, -t), vpython.vector( 0,  1, -t),
        vpython.vector( t,  0, -1), vpython.vector( t,  0,  1),
        vpython.vector(-t,  0, -1), vpython.vector(-t,  0,  1),
    ]

    # 2. Caras iniciales del Icosaedro (usando índices)
    initial_faces = [
        (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
        (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
        (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
        (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1),
    ]

    # 3. Inicialización para la subdivisión
    # Lista global de vértices proyectados
    all_vertices = [normalizar_vector(v) * radius for v in initial_vectors]
    # Lista de caras actuales (tuplas de índices)
    current_faces_indices = list(initial_faces)
    midpoint_cache = {} # Caché para evitar duplicar vértices

    # 4. Proceso de Subdivisión
    for _ in range(subdivisions):
        new_faces_indices = []
        for v1_idx, v2_idx, v3_idx in current_faces_indices:
            # Obtener los vectores para los cálculos (necesarios para el midpoint)
            v1, v2, v3 = all_vertices[v1_idx], all_vertices[v2_idx], all_vertices[v3_idx]

            # Encontrar o crear midpoints y obtener sus nuevos índices
            idx_a = get_midpoint_index(v1, v2, all_vertices, midpoint_cache, radius)
            idx_b = get_midpoint_index(v2, v3, all_vertices, midpoint_cache, radius)
            idx_c = get_midpoint_index(v3, v1, all_vertices, midpoint_cache, radius)

            # Crear 4 nuevos triángulos (usando solo índices)
            new_faces_indices.extend([
                (v1_idx, idx_a, idx_c),
                (v2_idx, idx_b, idx_a),
                (v3_idx, idx_c, idx_b),
                (idx_a, idx_b, idx_c)
            ])
        current_faces_indices = new_faces_indices

    # 5. Renderización (Wireframe)

    # Usaremos un set para almacenar las aristas de forma única (para no dibujar duplicados)
    edges = set()
    for v1_idx, v2_idx, v3_idx in current_faces_indices:
        # Una arista es una tupla de dos índices ordenados
        edges.add(tuple(sorted((v1_idx, v2_idx))))
        edges.add(tuple(sorted((v2_idx, v3_idx))))
        edges.add(tuple(sorted((v3_idx, v1_idx))))

    vpython_objects = []
    EDGE_RADIUS = radius / 800 # Radio muy pequeño para las aristas (efecto delgado)
    VERTEX_SIZE = radius / 100  # Tamaño pequeño para los vértices (efecto punto brillante)

    # Dibujar Aristas (Cilindros)
    for idx1, idx2 in edges:
        pos1 = all_vertices[idx1]
        pos2 = all_vertices[idx2]
        edge = vpython.cylinder(
            pos=pos1,
            axis=pos2 - pos1,
            radius=EDGE_RADIUS,
            color=edge_color
        )
        vpython_objects.append(edge)

    # Dibujar Vértices (Pequeñas Esferas)
    for pos in all_vertices:
        vertex = vpython.sphere(
            pos=pos,
            radius=VERTEX_SIZE,
            color=vertex_color,
        )
        vpython_objects.append(vertex)

    # Agrupar todos los objetos en un objeto compuesto
    return vpython.compound(vpython_objects, pos=vpython.vector(0, 0, 0))

def create_sphere(radius=1, color_value=vpython.color.blue):
    """
    Crea una esfera geodésica wireframe usando subdivisión de icosaedro.
    Retorna un objeto compound de VPython con aristas y vértices.
    """
    subdivisions = 2  # Nivel de detalle (2 es un buen equilibrio)
    vertex_color = vpython.color.white
    edge_color = vpython.color.cyan
    return crear_malla_geodesica(radius, subdivisions, vertex_color, edge_color)
