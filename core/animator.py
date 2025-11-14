import time
from .controls import rotate_sphere

def auto_rotate(sphere_obj, speed=0.03):
    while True:
        rotate_sphere(sphere_obj, speed, speed)
        time.sleep(0.05)
