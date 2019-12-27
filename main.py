import pygame
import sys
import os

# Resoltuion variables, Display is stretched to match Screen which can be set by user
DISPLAY_WIDTH = 640
DISPLAY_HEIGHT = 360
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Timing variables
TARGET_FPS = 60
SECOND = 1000
UPDATE_TIME = SECOND / TARGET_FPS
fps = 0
frames = 0
delta = 0
before_time = 0
before_sec = 0

# Handle cli flags
debug_mode = "--debug" in sys.argv
INDEV_BUILD = True

# Init pygame
os.environ["SDL_VIDEO_CENTERED"] = '1'
pygame.init()
global screen
if debug_mode:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
else:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN)
display = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
clock = pygame.time.Clock()

# Color variables
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Font variables
font_small = pygame.font.SysFont("Serif", 11)


def game():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        clear_display()
        if debug_mode or INDEV_BUILD:
            render_fps()
        flip_display()
        tick()
    pygame.quit()


def clear_display():
    pygame.draw.rect(display, BLACK, (0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT), False)


def flip_display():
    global frames

    pygame.transform.scale(display, (SCREEN_WIDTH, SCREEN_HEIGHT), screen)
    pygame.display.flip()
    frames += 1


def render_fps():
    text = font_small.render("FPS: " + str(fps), False, YELLOW)
    display.blit(text, (0, 0))


def tick():
    global before_time, before_sec, fps, frames, delta

    # Update delta based on time elapsed
    after_time = pygame.time.get_ticks()
    delta = (after_time - before_time) / UPDATE_TIME

    # Update fps if a second has passed
    if after_time - before_sec >= SECOND:
        fps = frames
        frames = 0
        before_sec += SECOND
    before_time = pygame.time.get_ticks()

    # Update pygame clock
    clock.tick(TARGET_FPS)


if __name__ == "__main__":
    before_time = pygame.time.get_ticks()
    before_sec = before_time
    game()
