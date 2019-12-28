import pygame.image


image_cache = {}


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
