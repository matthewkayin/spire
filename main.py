from game import player, resources, map, util
import pygame
import random
import math
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

# Game states
EXIT = -1
MAIN_LOOP = 0
DEATH_SCREEN = 1


def game():
    player_obj = player.Player(DISPLAY_WIDTH, DISPLAY_HEIGHT)
    player_obj.x = DISPLAY_WIDTH // 2
    player_obj.y = DISPLAY_HEIGHT // 2

    level = map.Map()
    resources.load_tileset("tileset")

    running = True
    next_state = EXIT

    while running:
        handle_input()
        player_obj.handle_input(input_queue, input_states, mouse_x, mouse_y)

        """
        BEGIN UPDATING
        """
        player_obj.update(dt)
        player_interaction = player_obj.click_interaction
        if player_obj.ui_substate == player_obj.AIM_SPELL:
            if player_obj.pending_spell.NEEDS_ROOM_AIM:
                pending_spell_rect = (player_obj.mouse_x + player_obj.get_camera_x(), player_obj.mouse_y + player_obj.get_camera_y(), player_obj.pending_spell.width, player_obj.pending_spell.height)
                player_obj.has_room_aim = level.rect_in_map(pending_spell_rect)
        for spell in player_obj.active_spells:
            if not level.rect_in_current_rooms(spell.get_rect()):
                spell.end_spell()
                continue
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
                    for other_enemy in room.enemies:
                        if other_enemy != enemy:
                            enemy.check_collision(dt, other_enemy.get_rect())
                    player_obj.check_collision(dt, enemy.get_rect())
                    if enemy.deal_damage:
                        if player_obj.collides(enemy.hurtbox):
                            player_obj.health -= enemy.POWER
                            player_obj.take_hit(enemy.POWER, (enemy.x, enemy.y))
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
                for chest in room.chests:
                    player_obj.check_collision(dt, chest[0])
                    if not chest[1]:
                        if player_interaction is not None:
                            if util.point_in_rect((mouse_x + player_obj.get_camera_x(), mouse_y + player_obj.get_camera_y()), chest[0]):
                                if util.get_distance(player_obj.get_center(), util.get_center(chest[0])) <= 50:
                                    chest[1] = True
                                    old_spawn_degrees = []
                                    for item in chest[2]:
                                        spawn_degree = 0
                                        distance = 70
                                        x_dist = 0
                                        y_dist = 0
                                        spawn_degree_okay = False
                                        while not spawn_degree_okay:
                                            spawn_degree = random.randint(0, 360)
                                            spawn_degree_okay = True
                                            for degree in old_spawn_degrees:
                                                if abs(degree - spawn_degree) < 10:
                                                    spawn_degree_okay = False
                                            if spawn_degree_okay:
                                                x_dist = int(distance * math.cos(math.radians(spawn_degree)))
                                                y_dist = int(distance * math.sin(math.radians(spawn_degree)))
                                                if player_obj.collides((x_dist + util.get_center(chest[0])[0], y_dist + util.get_center(chest[0])[1], 20, 20)):
                                                    spawn_degree_okay = False
                                        old_spawn_degrees.append(spawn_degree)
                                        room.items.append([item[0], item[1], (x_dist + util.get_center(chest[0])[0], y_dist + util.get_center(chest[0])[1])])
                for item in room.items:
                    if player_obj.collides((item[2][0], item[2][1], 20, 20)):
                        player_obj.add_item(item[0], item[1])
                        item[1] = 0
                room.items = [item for item in room.items if item[1] != 0]
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
            for chest in room.chests:
                if chest[1]:
                    display.blit(resources.get_image("chest-open", True), (chest[0][0] - player_obj.get_camera_x(), chest[0][1] - player_obj.get_camera_y()))
                else:
                    display.blit(resources.get_image("chest", True), (chest[0][0] - player_obj.get_camera_x(), chest[0][1] - player_obj.get_camera_y()))
            for item in room.items:
                display.blit(resources.get_image(item[0], True), (item[2][0] - player_obj.get_camera_x(), item[2][1] - player_obj.get_camera_y()))
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

        for i in range(0, player_obj.max_health):
            x_coord = 5 + (30 * i)
            y_coord = 5
            if player_obj.health == i + 0.5:
                display.blit(resources.get_subimage("heart", True, (0, 0, 10, 20)), (x_coord, y_coord))
                display.blit(resources.get_subimage("heart-empty", True, (10, 0, 10, 20)), (x_coord + 10, y_coord))
            elif player_obj.health > i:
                display.blit(resources.get_image("heart", True), (x_coord, y_coord))
            else:
                display.blit(resources.get_image("heart-empty", True), (x_coord, y_coord))
        if player_obj.recent_spell is not None:
            display.blit(resources.get_image(player_obj.recent_spell, True), (DISPLAY_WIDTH - 36 - 5, 5))
            spell_count = 0
            if player_obj.recent_spell == "needle":
                spell_count = int(player_obj.health)
            else:
                spell_count = player_obj.inventory["spellbook-" + player_obj.recent_spell]
            count_surface = font_small.render(str(spell_count), False, WHITE)
            display.blit(count_surface, (DISPLAY_WIDTH - 36 - 5 + int(36 * 0.8), 5 + int(36 * 0.8)))
        if player_obj.recent_item is not None:
            display.blit(pygame.transform.scale(resources.get_image(player_obj.recent_item, True), (36, 36)), (DISPLAY_WIDTH - 36 - 5 - 36 - 5, 5))
            item_count = player_obj.inventory[player_obj.recent_item]
            count_surface = font_small.render(str(item_count), False, WHITE)
            display.blit(count_surface, (DISPLAY_WIDTH - 36 - 5 - 36 - 5 + int(36 * 0.8), 5 + int(36 * 0.8)))

        """
        RENDER SPELLWHEEL UI
        """
        if player_obj.ui_state == player_obj.SPELLWHEEL and player_obj.ui_substate == player_obj.CHOOSE_SPELL:
            fade_surface = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, player_obj.fade_alpha))
            display.blit(fade_surface, (0, 0))
            if player_obj.fade_alpha == 100:
                display.blit(resources.get_image("spellwheel", True), ((DISPLAY_WIDTH // 2) - 150, (DISPLAY_HEIGHT // 2) - 150))
                for item in player_obj.spellcircle_items:
                    display.blit(resources.get_image(item[0][item[0].index("-") + 1:], True), (item[2][0], item[2][1]))
                    count_surface = font_small.render(str(item[1]), False, BLUE)
                    display.blit(count_surface, ((item[2][0] + int(item[2][2] * 0.8), item[2][1] + int(item[2][3] * 0.8))))
        """
        RENDER INVENTORY UI
        """
        if player_obj.ui_state == player_obj.INVENTORY:
            ICON_SIZE = 40
            ICON_RENDER_SIZE = 36
            RENDER_OFFSET = (ICON_SIZE - ICON_RENDER_SIZE) // 2
            INVENTORY_ROWS = 3
            INVENTORY_COLUMNS = 4
            INVENTORY_WIDTH = ICON_SIZE * INVENTORY_COLUMNS
            INVENTORY_HEIGHT = ICON_SIZE * INVENTORY_ROWS
            inventory_rect = ((640 // 2) - (INVENTORY_WIDTH // 2), (360 // 2) - (INVENTORY_HEIGHT // 2), INVENTORY_WIDTH, INVENTORY_HEIGHT)
            pygame.draw.rect(display, WHITE, inventory_rect, True)
            for i in range(1, INVENTORY_ROWS):
                pygame.draw.line(display, WHITE, (inventory_rect[0], inventory_rect[1] + (i * ICON_SIZE)), (inventory_rect[0] + inventory_rect[2] - 1, inventory_rect[1] + (i * ICON_SIZE)))
            for i in range(1, INVENTORY_COLUMNS):
                pygame.draw.line(display, WHITE, (inventory_rect[0] + (i * ICON_SIZE), inventory_rect[1]), (inventory_rect[0] + (i * ICON_SIZE), inventory_rect[1] + inventory_rect[3] - 1))
            item_coords = (0, 0)
            for name in player_obj.inventory.keys():
                if name in player_obj.equipped_spellbooks or name == player_obj.recent_item:
                    pygame.draw.rect(display, YELLOW, (inventory_rect[0] + item_coords[0], inventory_rect[1] + item_coords[1], ICON_SIZE, ICON_SIZE), True)
                display.blit(pygame.transform.scale(resources.get_image(name, True), (ICON_RENDER_SIZE, ICON_RENDER_SIZE)), (inventory_rect[0] + item_coords[0] + RENDER_OFFSET, inventory_rect[1] + item_coords[1] + RENDER_OFFSET))
                count_surface = font_small.render(str(player_obj.inventory[name]), False, WHITE)
                display.blit(count_surface, (inventory_rect[0] + item_coords[0] + RENDER_OFFSET + int(ICON_RENDER_SIZE * 0.8), inventory_rect[1] + item_coords[1] + RENDER_OFFSET + int(ICON_RENDER_SIZE * 0.8)))
                item_coords = (item_coords[0] + ICON_SIZE, item_coords[1])
                if item_coords[0] >= INVENTORY_WIDTH:
                    item_coords = (0, item_coords[1] + ICON_SIZE)

        if debug_mode or show_fps:
            render_fps()

        flip_display()
        # pygame.display.flip()

        tick()

        if player_obj.health <= 0:
            running = False
            next_state = DEATH_SCREEN

    if next_state == DEATH_SCREEN:
        death_screen()


def death_screen():
    continue_button_rect = ((DISPLAY_WIDTH // 2) - 50, (DISPLAY_HEIGHT // 2) + 40, 100, 20)
    exit_button_rect = ((DISPLAY_WIDTH // 2) - 50, (DISPLAY_HEIGHT // 2) + 70, 100, 20)
    death_message = font_small.render("You Heckin Died", False, WHITE)
    continue_text = font_small.render("Play Again", False, WHITE)
    continue_text_x = continue_button_rect[0] + (continue_button_rect[2] // 2) - (continue_text.get_width() // 2)
    continue_text_y = continue_button_rect[1] + (continue_button_rect[3] // 2) - (continue_text.get_height() // 2)
    exit_text = font_small.render("Yeet", False, WHITE)
    exit_text_x = exit_button_rect[0] + (exit_button_rect[2] // 2) - (exit_text.get_width() // 2)
    exit_text_y = exit_button_rect[1] + (exit_button_rect[3] // 2) - (exit_text.get_height() // 2)

    running = True
    next_state = EXIT

    while running:
        hovered_button = 0
        if util.point_in_rect((mouse_x, mouse_y), continue_button_rect):
            hovered_button = 1
        elif util.point_in_rect((mouse_x, mouse_y), exit_button_rect):
            hovered_button = 2

        handle_input()
        while len(input_queue) != 0:
            event = input_queue.pop()
            if event == ("left click", True):
                if hovered_button == 1:
                    next_state = MAIN_LOOP
                    running = False
                elif hovered_button == 2:
                    next_state = EXIT
                    running = False

        clear_display()

        display.blit(death_message, ((DISPLAY_WIDTH // 2) - (death_message.get_width() // 2), (DISPLAY_HEIGHT // 2) - (death_message.get_height() // 2) - 100))
        pygame.draw.rect(display, WHITE, continue_button_rect, hovered_button != 1)
        display.blit(continue_text, (continue_text_x, continue_text_y))
        pygame.draw.rect(display, WHITE, exit_button_rect, hovered_button != 2)
        display.blit(exit_text, (exit_text_x, exit_text_y))

        if debug_mode or show_fps:
            render_fps()

        flip_display()

        tick()

    if next_state == MAIN_LOOP:
        game()


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
            elif event.key == pygame.K_i:
                input_queue.append(("inventory", True))
            elif event.key == pygame.K_e:
                input_queue.append(("quickitem", True))
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
            elif event.button == pygame.BUTTON_RIGHT:
                input_queue.append(("right click", True))
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
    pygame.quit()
