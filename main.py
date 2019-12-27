from game import player
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
dt = 0
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

# Input variables
input_queue = []
input_states = {"player left": False, "player right": False, "player up": False, "player down": False}

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
    player_obj = player.Player()
    player_obj.x = DISPLAY_WIDTH // 2
    player_obj.y = DISPLAY_HEIGHT // 2
    running = True

    while running:
        handle_input()

        player_obj.update(dt, input_queue, input_states)

        clear_display()
        display.blit(player_obj.image, (player_obj.get_x(), player_obj.get_y()))

        if debug_mode or INDEV_BUILD:
            render_fps()

        flip_display()
        pygame.display.flip()

        tick()
    pygame.quit()


def handle_input():
    global input_states

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                input_queue.append(("player up", True))
                input_states["player up"] = True
            elif event.key == pygame.K_s:
                input_queue.append(("player down", True))
                input_states["player down"] = True
            elif event.key == pygame.K_d:
                input_queue.append(("player right", True))
                input_states["player right"] = True
            elif event.key == pygame.K_a:
                input_queue.append(("player left", True))
                input_states["player left"] = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                input_queue.append(("player up", False))
                input_states["player up"] = False
            elif event.key == pygame.K_s:
                input_queue.append(("player down", False))
                input_states["player down"] = False
            elif event.key == pygame.K_d:
                input_queue.append(("player right", False))
                input_states["player right"] = False
            elif event.key == pygame.K_a:
                input_queue.append(("player left", False))
                input_states["player left"] = False


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
    global before_time, before_sec, fps, frames, dt

    # Update delta based on time elapsed
    after_time = pygame.time.get_ticks()
    dt = (after_time - before_time) / UPDATE_TIME

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
