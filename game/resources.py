import pygame.image
import pygame.transform


image_cache = {}
tileset_cache = {}


def load_image(path, has_alpha):
    if path not in image_cache.keys():
        if has_alpha:
            image_cache[path] = pygame.image.load("game/res/" + path + ".png").convert_alpha()
        else:
            image_cache[path] = pygame.image.load("game/res/" + path + ".png").convert()

    return image_cache[path]


def get_image(path):
    if path not in image_cache.keys():
        print("Error! Image " + path + " has not been loaded in yet!")
        return None

    return image_cache[path]


def create_fade_image(path, alpha):
    if path not in image_cache.keys():
        print("Error! You tried to apply transparency to an image that you haven't loaded yet!")
        return None

    new_path = path + "&alpha=" + str(alpha)
    if new_path not in image_cache.keys():
        new_image = image_cache[path].copy()
        new_image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
        image_cache[new_path] = new_image

    return image_cache[new_path]


def get_fade_image(path, alpha):
    new_path = path + "&alpha=" + str(alpha)
    if new_path not in image_cache.keys():
        print("Error! Tried to get a faded image that hasn't been created yet!")
        return None

    return image_cache[new_path]


def rotate(image, angle):
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
    offset = (min_box[0] - origin_pos[0] - pivot_move[0], max_box[1] - origin_pos[1] - pivot_move[1])

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
