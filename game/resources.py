import pygame.image


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
