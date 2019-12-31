import math


def get_distance(point1, point2):
    return math.sqrt(((point2[0] - point1[0]) ** 2) + ((point2[1] - point1[0]) ** 2))


def scale_vector(old_vector, new_magnitude):
    old_magnitude = math.sqrt((old_vector[0] ** 2) + (old_vector[1] ** 2))
    if old_magnitude == 0:
        return (0, 0)
    scale = new_magnitude / old_magnitude
    new_x = old_vector[0] * scale
    new_y = old_vector[1] * scale
    return (new_x, new_y)


def get_center(rect):
    return ((rect[0] + (rect[2] // 2)), (rect[1] + (rect[3] // 2)))
