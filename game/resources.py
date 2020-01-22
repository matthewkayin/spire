import pygame.image
import pygame.transform
import random


image_cache = {}
tileset_cache = {}


def get_image(path, has_alpha, alpha=255):
    if path not in image_cache.keys():
        if has_alpha:
            image_cache[path] = pygame.image.load("game/res/" + path + ".png").convert_alpha()
        else:
            image_cache[path] = pygame.image.load("game/res/" + path + ".png").convert()

    return_path = path
    if alpha != 255:
        return_path = path + "&alpha=" + str(alpha)
        if return_path not in image_cache.keys():
            new_image = image_cache[path].copy()
            new_image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
            image_cache[return_path] = new_image

    return image_cache[return_path]


def rotate(image, angle, origin_pos=None):
    if origin_pos is None:
        origin_pos = image.get_rect().center

    # calcaulate the axis aligned bounding box of the rotated image
    w, h = image.get_size()
    box = [pygame.math.Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
    box_rotate = [p.rotate(angle) for p in box]
    min_box = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
    max_box = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])

    # calculate the translation of the pivot
    pivot = pygame.math.Vector2(origin_pos[0], -origin_pos[1])
    pivot_rotate = pivot.rotate(angle)
    pivot_move = pivot_rotate - pivot

    rotated_image = pygame.transform.rotate(image, angle)
    offset = (int(min_box[0] - origin_pos[0] - pivot_move[0]), int(pivot_move[1] - max_box[1] - origin_pos[1]))

    return rotated_image, offset


def load_tileset(path):
    if path not in tileset_cache.keys():
        TILE_WIDTH = 50
        TILE_HEIGHT = 50

        tileset_cache[path] = []

        tileset_surface = pygame.image.load("game/res/" + path + ".png").convert()
        print("Loaded tileset \"" + path + "\", has dimensions " + str(tileset_surface.get_width()) + "x" + str(tileset_surface.get_height()))

        width_in_tiles = tileset_surface.get_width() // TILE_WIDTH
        height_in_tiles = tileset_surface.get_height() // TILE_HEIGHT
        for y in range(0, height_in_tiles):
            for x in range(0, width_in_tiles):
                tileset_cache[path].append(tileset_surface.subsurface(pygame.rect.Rect(x * TILE_WIDTH, y * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT)))
    else:
        print("Error! Tileset " + path + " already loaded!")


def get_tile(path, index):
    if path not in tileset_cache:
        print("Error! You need to load tileset " + path + " before you use it!")
        return None
    if index >= len(tileset_cache[path]):
        print("Error! Tileset index of " + index + " is out of bounds for tileset " + path + "!")
        return None

    return tileset_cache[path][index]


def create_lightning(length, angle):
    JAGGEDNESS = 10  # Make smaller for more points per bolt
    SWAY = 6  # Make larger for more possible variation per point

    lightning = pygame.Surface((50, length), pygame.SRCALPHA)

    point_ys = []
    for i in range(0, length // JAGGEDNESS):
        num = random.randint(10, length - 10)
        while num in point_ys:
            num = random.randint(10, length - 10)
        point_ys.append(num)
    point_ys.insert(0, 4)
    point_ys.append(196)
    point_ys.sort()

    points = []
    points.append((25 - 3, point_ys[0]))
    for i in range(1, len(point_ys) - 1):
        offset = random.randint(1, SWAY)
        negative = 0 == random.randint(0, 1)
        if negative:
            offset *= -1
        x_value = points[i - 1][0] + offset
        if x_value < 0 or x_value >= 50:
            offset *= -1
            x_value += (offset * 2)
        points.append((x_value, point_ys[i]))
    points.append((25 - 3, point_ys[len(point_ys) - 1]))

    for i in range(1, len(points)):
        pygame.draw.line(lightning, (200, 200, 255, 70), points[i - 1], points[i], 4)
        pygame.draw.line(lightning, (200, 200, 255, 120), points[i - 1], points[i], 3)
        pygame.draw.line(lightning, (200, 200, 255, 255), points[i - 1], points[i], 2)

    return rotate(lightning, angle, (26, 0))
