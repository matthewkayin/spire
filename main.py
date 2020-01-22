from game import player, resources, map
import pygame
import sys
import os

# Resoltuion variables, Display is stretched to match Screen which can be set by user
DISPLAY_WIDTH = 640
DISPLAY_HEIGHT = 360
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 360
if os.path.isfile("data/settings.txt"):
    print("Settings file found!")
    video_settings = open("data/settings.txt").read().splitlines()
    for line in video_settings:
        if line.startswith("resolution="):
            SCREEN_WIDTH = int(line[line.index("=") + 1:line.index("x")])
            SCREEN_HEIGHT = int(line[line.index("x") + 1:])
            aspect_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
            if aspect_ratio == 4 / 3:
                DISPLAY_HEIGHT = 480
            elif aspect_ratio == 16 / 10:
                DISPLAY_HEIGHT = 420
            elif aspect_ratio == 16 / 9:
                DISPLAY_HEIGHT = 360
else:
    print("No settings file found!")
print("Resolution set to " + str(SCREEN_WIDTH) + "x" + str(SCREEN_HEIGHT) + ".")
SCALE = SCREEN_WIDTH / DISPLAY_WIDTH
display_rect = (0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT)

# Timing variables
TARGET_FPS = 60
SECOND = 1000
UPDATE_TIME = SECOND / 60.0
fps = 0
frames = 0
dt = 0
before_time = 0
before_sec = 0

# Handle cli flags
debug_mode = "--debug" in sys.argv
show_fps = "--showfps" in sys.argv  # This is for if you want to see fps even in no-debug

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
mouse_x = 0
mouse_y = 0

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
    player_obj = player.Player(DISPLAY_WIDTH, DISPLAY_HEIGHT)
    player_obj.x = DISPLAY_WIDTH // 2
    player_obj.y = DISPLAY_HEIGHT // 2

    level = map.Map()
    resources.load_tileset("tileset")

    running = True

    while running:
        handle_input()
        player_obj.handle_input(input_queue, input_states, mouse_x, mouse_y)

        """
        BEGIN UPDATING
        """
        player_obj.update(dt)
        for spell in player_obj.active_spells:
            if spell.requests_enemies:
                spell.enemies = []
                for room in level.current_rooms:
                    for enemy in room.enemies:
                        spell.enemies.append((enemy.x, enemy.y))
        if player_obj.ui_state == player_obj.NONE:
            level.update(player_obj)
            for room in level.current_rooms:
                for collider in room.colliders:
                    player_obj.check_collision(dt, collider)
                for enemy in room.enemies:
                    enemy.update(dt, player_obj.get_rect())
                    if enemy.deal_damage:
                        if player_obj.collides(enemy.hurtbox):
                            player_obj.health -= enemy.POWER
                    for spell in player_obj.active_spells:
                        if spell.handles_collisions:
                            if spell.collides(enemy.get_rect()):
                                if spell.interact:
                                    for interaction in spell.get_interactions():
                                        enemy.add_interaction(interaction)
                                spell.handle_collision()
                room.enemies = [enemy for enemy in room.enemies if enemy.health > 0]
                for spell in player_obj.active_spells:
                    if spell.handles_collisions:
                        for collider in room.colliders:
                            if spell.collides(collider):
                                spell.handle_collision()
            player_obj.update_camera()

        """
        BEGIN RENDERING
        """
        clear_display()

        """
        RENDER ROOMS
        """
        for room in level.rooms:
            for tile in room.render_points:
                tile_img = tile[0]
                tile_x = tile[1] - player_obj.get_camera_x()
                tile_y = tile[2] - player_obj.get_camera_y()
                if rect_in_screen((tile_x, tile_y, 50, 50)):
                    if isinstance(tile_img, str):
                        display.blit(resources.get_image(tile_img, False), (tile_x, tile_y))
                    else:
                        if tile_img[1] != 16:
                            display.blit(resources.get_tile(tile_img[0], tile_img[1]), (tile_x, tile_y))
        """
        RENDER SPELLS
        """
        for spell in player_obj.active_spells:
            spell_x = spell.get_x() - player_obj.get_camera_x()
            spell_y = spell.get_y() - player_obj.get_camera_y()
            display.blit(spell.get_image(), (spell_x, spell_y))
            for subrenderable in spell.get_subrenderables():
                subrender_img = subrenderable[0]
                for subrender_coords in subrenderable[1:]:
                    coords = (subrender_coords[0] - player_obj.get_camera_x(), subrender_coords[1] - player_obj.get_camera_y())
                    display.blit(subrender_img, coords)
        if player_obj.ui_substate == player_obj.AIM_SPELL:
            pygame.draw.circle(display, WHITE, (player_obj.get_x() - player_obj.get_camera_x() + player_obj.width // 2, player_obj.get_y() - player_obj.get_camera_y() + player_obj.height // 2), player_obj.pending_spell.AIM_RADIUS, 3)
            if player_obj.pending_spell.is_aim_valid(player_obj.get_center(), player_obj.get_aim()):
                aim_coords = player_obj.pending_spell.get_aim_coords(player_obj.get_center(), player_obj.get_aim())
                aim_coords = (int(aim_coords[0] - player_obj.get_camera_x()), int(aim_coords[1] - player_obj.get_camera_y()))
                display.blit(player_obj.pending_spell.get_image(), aim_coords)
        """
        RENDER ENEMIES
        """
        for room in level.rooms:
            for enemy in room.enemies:
                enemy_x = enemy.get_x() - player_obj.get_camera_x()
                enemy_y = enemy.get_y() - player_obj.get_camera_y()
                if rect_in_screen((enemy_x, enemy_y, enemy.width, enemy.height)):
                    if enemy.attacking:
                        pygame.draw.rect(display, RED, (enemy_x, enemy_y, enemy.width, enemy.height), False)
                    else:
                        display.blit(enemy.get_image(), (enemy_x, enemy_y))
        """
        RENDER PLAYER
        """
        display.blit(player_obj.get_image(), (player_obj.get_x() - player_obj.get_camera_x(), player_obj.get_y() - player_obj.get_camera_y()))
        if player_obj.get_chargebar_percentage() > 0:
            chargebar_rect = (player_obj.get_x() - player_obj.get_camera_x() - 5, player_obj.get_y() - player_obj.get_camera_y() - 5, int(round(30 * player_obj.get_chargebar_percentage())), 5)
            pygame.draw.rect(display, YELLOW, chargebar_rect, False)
        for room in level.rooms:
            for tile in room.render_points:
                tile_img = tile[0]
                tile_img = tile[0]
                tile_x = tile[1] - player_obj.get_camera_x()
                tile_y = tile[2] - player_obj.get_camera_y()
                if rect_in_screen((tile_x, tile_y, 50, 50)):
                    if not isinstance(tile_img, str):
                        if tile_img[1] == 16:
                            display.blit(resources.get_tile(tile_img[0], tile_img[1]), (tile_x, tile_y))

        for i in range(0, player_obj.health):
            display.blit(player_obj.get_heart_image(), (5 + (30 * i), 5))

        """
        RENDER SPELLWHEEL UI
        """
        if player_obj.ui_state == player_obj.SPELLWHEEL and player_obj.ui_substate == player_obj.CHOOSE_SPELL:
            fade_surface = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, player_obj.fade_alpha))
            display.blit(fade_surface, (0, 0))

            if player_obj.fade_alpha == 100:
                # pygame.draw.circle(display, WHITE, (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2), 150, 50)
                display.blit(resources.get_image("spellwheel", True), ((DISPLAY_WIDTH // 2) - 150, (DISPLAY_HEIGHT // 2) - 150))
                for item in player_obj.spellcircle_items:
                    display.blit(resources.get_image(item[0][item[0].index("-") + 1:], True), (item[2][0], item[2][1]))
                    count_surface = font_small.render(str(item[1]), False, BLUE)
                    display.blit(count_surface, ((item[2][0] + int(item[2][2] * 0.8), item[2][1] + int(item[2][3] * 0.8))))

        if debug_mode or show_fps:
            render_fps()

        flip_display()
        pygame.display.flip()

        tick()
    pygame.quit()


def handle_input():
    global input_states, mouse_x, mouse_y

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
            elif event.key == pygame.K_SPACE:
                input_queue.append(("spellwheel", True))
            elif event.key == pygame.K_q:
                input_queue.append(("quickcast", True))
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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                input_queue.append(("left click", True))
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            mouse_x = int(mouse_pos[0] / SCALE)
            mouse_y = int(mouse_pos[1] / SCALE)


def rect_in_screen(rect):
    center_x = DISPLAY_WIDTH // 2
    other_center_x = rect[0] + (rect[2] // 2)
    center_y = DISPLAY_HEIGHT // 2
    other_center_y = rect[1] + (rect[3] // 2)
    return abs(center_x - other_center_x) * 2 < rect[2] + DISPLAY_WIDTH and abs(center_y - other_center_y) * 2 < rect[3] + DISPLAY_HEIGHT


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
