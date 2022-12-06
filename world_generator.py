import random
import math

import block
import world

def interpolate(start, end, step: float) -> float:
    return start + step * (end - start)

def random_gradient(ix: int, iy: int) -> tuple[float, float]:
    w = 64
    s = w // 2
    a = ix
    b = iy
    a *= 3284157443
    b ^= a << s | a >> w-s
    b *= 1911520717
    a ^= b << s | b >> w-s
    a *= 2048419325
    r = a * 3.14159265
    
    return math.cos(r), math.sin(r)

def dot_grid_gradient(ix: int, iy: int, x: float, y: float) -> float:
    gradient_x, gradient_y = random_gradient(ix, iy)
    dx = x - ix
    dy = y - iy
    return(dx * gradient_x) + (dy * gradient_y)
        
def perlin_noise(x: float, y: float) -> float:
    x0 = math.floor(x)
    y0 = math.floor(y)
    x1 = x0 + 1
    y1 = y0 + 1

    sx = x - x0
    sy = y - y0

    n0 = dot_grid_gradient(x0, y0, x, y)
    n1 = dot_grid_gradient(x1, y0, x, y)
    ix0 = interpolate(n0, n1, sx)

    n0 = dot_grid_gradient(x0, y1, x, y)
    n1 = dot_grid_gradient(x1, y1, x, y)
    ix1 = interpolate(n0, n1, sx)

    return interpolate(ix0, ix1, sy)

def empty_world_generator(width: int, height: int, length: int, seed: int) -> bytes:
    return b'\x00\x00' * width * height * length

def flat_world_generator(width: int, height: int, length: int, seed: int) -> bytes:
    return (b'\x00\x07' * width * length) + (b'\x00\x03' * width * (height // 2 - 2) * length) + (b'\x00\x05' * width * length) + (b'\x00\x00' * width * (height // 2) * length)
'''
def perlin_world_generator(width: int, height: int, length: int, seed: int) -> bytes:
    r = []
    
    heightmap = [[perlin_noise(i/20, j/20)+0.5 for j in range(length) ] for i in range(width)]

    for i in range(height):
        for j in range(length):
            for k in range(width):
                if (heightmap[k][j]*height)<i:
                    r.append(1)
                else:
                    r.append(0)

    return r'''

