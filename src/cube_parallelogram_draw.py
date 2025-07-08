import math
from pygame.math import Vector2
PARALLELOGRAM_OFFSET = {
    "left": (Vector2(0, 0), Vector2(-math.sqrt(3) / 2, -0.5), Vector2(-math.sqrt(3) / 2, 0.5), Vector2(0, 1)), #CCW
    "right": (Vector2(0, 0), Vector2(math.sqrt(3) / 2, -0.5), Vector2(math.sqrt(3) / 2, 0.5), Vector2(0, 1)),  #CW
    "top": (Vector2(0, 0), Vector2(-math.sqrt(3) / 2, -0.5), Vector2(0, -1), Vector2(math.sqrt(3) / 2, -0.5)), #CW
}

def cal_parallelogram(position : Vector2, face: str, size: float) -> tuple[Vector2, Vector2, Vector2, Vector2]:
    points = [position] * 4
    for i in range(4):
        points[i] = Vector2(position.x + size * PARALLELOGRAM_OFFSET[face][i].x, position.y + size * PARALLELOGRAM_OFFSET[face][i].y)
    return tuple(points) #type: ignore
