import math
from . import entity, util, spells


class Player(entity.Entity):
    """
    Player class
    """

    def __init__(self, DISPLAY_WIDTH, DISPLAY_HEIGHT):
        super(Player, self).__init__("player-idle", True)

        self.SCREEN_CENTER_X = DISPLAY_WIDTH // 2
        self.SCREEN_CENTER_Y = DISPLAY_HEIGHT // 2
        self.CAMERA_OFFSET_X = (self.width // 2) - self.SCREEN_CENTER_X
        self.CAMERA_OFFSET_Y = (self.height // 2) - self.SCREEN_CENTER_Y
        self.camera_x = 0
        self.camera_y = 0
        self.CAMERA_SENSITIVITY = 0.2

        self.dx = 0
        self.dy = 0
        self.SPEED = 2

        self.health = 3
        self.max_health = 3

        self.active_spells = []
        self.pending_spell = None
        self.recent_spell = None
        self.has_room_aim = False

        self.inventory = {}
        self.add_item("spellbook-fire", 3)
        self.add_item("spellbook-golem", 3)
        self.add_item("spellbook-thorns", 3)

        # UI state constants
        self.NONE = 0
        self.SPELLWHEEL = 1
        self.CHOOSE_SPELL = 1
        self.AIM_SPELL = 2
        self.ui_state = self.NONE
        self.ui_substate = self.NONE

    def handle_input(self, input_queue, input_states, mouse_x, mouse_y):
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y
        self.update_velocity = False

        while len(input_queue) != 0:
            event = input_queue.pop()
            if event == ("player up", True):
                self.dy = -1
                self.update_velocity = True
            elif event == ("player down", True):
                self.dy = 1
                self.update_velocity = True
            elif event == ("player right", True):
                self.dx = 1
                self.update_velocity = True
            elif event == ("player left", True):
                self.dx = -1
                self.update_velocity = True
            elif event == ("player up", False):
                if input_states["player down"]:
                    self.dy = 1
                else:
                    self.dy = 0
                self.update_velocity = True
            elif event == ("player down", False):
                if input_states["player up"]:
                    self.dy = -1
                else:
                    self.dy = 0
                self.update_velocity = True
            elif event == ("player right", False):
                if input_states["player left"]:
                    self.dx = -1
                else:
                    self.dx = 0
                self.update_velocity = True
            elif event == ("player left", False):
                if input_states["player right"]:
                    self.dx = 1
                else:
                    self.dx = 0
                self.update_velocity = True
            elif event == ("left click", True):
                if self.ui_state == self.SPELLWHEEL and self.ui_substate == self.CHOOSE_SPELL:
                    for item in self.spellcircle_items:
                        if util.point_in_rect((self.mouse_x, self.mouse_y), item[2]):
                            self.ui_substate = self.AIM_SPELL
                            self.recent_spell = item[0][item[0].index("-") + 1:]
                            self.pending_spell = spells.get_by_name(self.recent_spell)
                elif self.ui_substate == self.AIM_SPELL and (self.ui_state == self.NONE or self.ui_state == self.SPELLWHEEL):
                    if self.pending_spell.is_aim_valid(self.get_center(), self.get_aim()) and (self.has_room_aim if self.pending_spell.NEEDS_ROOM_AIM else True):
                        self.begin_spellcast()
                        self.ui_state = self.NONE
                        self.ui_substate = self.NONE
            elif event == ("spellwheel", True):
                self.toggle_spellwheel()
            elif event == ("quickcast", True):
                if self.ui_state == self.NONE:
                    if self.ui_substate == self.NONE and self.recent_spell is not None:
                        self.ui_substate = self.AIM_SPELL
                        self.pending_spell = spells.get_by_name(self.recent_spell)
                    elif self.ui_substate == self.AIM_SPELL:
                        self.ui_substate = self.NONE

    def update(self, dt):
        # If update velocity is true, that means we changed the direction vector so we should update the velocity to match it
        if self.update_velocity:
            # player vx/vy is direction (dx/dy) scaled up to SPEED
            self.vx, self.vy = util.scale_vector((self.dx, self.dy), self.SPEED)

        if self.ui_state == self.NONE:

            if self.pending_spell is not None:
                if self.pending_spell.state == spells.Spell.CHARGING and (self.vx != 0 or self.vy != 0):
                    self.cancel_spellcast()
                elif self.pending_spell.state == spells.Spell.CAST_READY:
                    if self.recent_spell == "needle":
                        self.health -= 1
                    else:
                        self.remove_item("spellbook-" + self.recent_spell)
                        if "spellbook-" + self.recent_spell not in self.inventory.keys():
                            self.recent_spell = None
                    self.pending_spell.cast()
                    self.active_spells.append(self.pending_spell)
                    self.pending_spell = None
                else:
                    # It's important to put the update in the else otherwise we will update the spell twice in one update
                    self.pending_spell.update(dt)

            for spell in self.active_spells:
                spell.update(dt)
            # Remove ended spells from our active spell list
            self.active_spells = [spell for spell in self.active_spells if spell.state != spells.Spell.ENDED]

            super(Player, self).update(dt)
        elif self.ui_state == self.SPELLWHEEL:
            if self.fade_alpha < 100:
                self.fade_alpha += dt * 10
                if self.fade_alpha > 100:
                    self.fade_alpha = 100

        if self.ui_substate == self.AIM_SPELL:
            self.has_room_aim = False

    def update_camera(self):
        """
        Sets the camera position based on the player position and offset with the mouse relative to the screen center
        """
        self.camera_x = self.x + self.CAMERA_OFFSET_X + ((self.mouse_x - self.SCREEN_CENTER_X) * self.CAMERA_SENSITIVITY)
        self.camera_y = self.y + self.CAMERA_OFFSET_Y + ((self.mouse_y - self.SCREEN_CENTER_Y) * self.CAMERA_SENSITIVITY)

    def check_collision(self, dt, collider):
        """
        This checks for a collision with a wall-like object and handles it if necessary
        """
        if self.collides(collider):
            x_step = self.vx * dt
            y_step = self.vy * dt

            # Since there was a collision, rollback our previous movement
            self.x -= x_step
            self.y -= y_step
            self.camera_x -= x_step
            self.camera_y -= y_step

            # Check to see if that collision happened due to x movement
            self.x += x_step
            x_caused_collision = self.collides(collider)
            self.x -= x_step

            # Check to see if that collision happened due to y movement
            self.y += y_step
            y_caused_collision = self.collides(collider)
            self.y -= y_step

            # If x/y didn't cause collision, we can move in x/y direction
            if not x_caused_collision:
                self.x += x_step
                self.camera_x += x_step
            if not y_caused_collision:
                self.y += y_step
                self.camera_y += y_step

    def get_aim(self):
        return (int(self.mouse_x + self.camera_x), int(self.mouse_y + self.camera_y))

    def get_camera_x(self):
        return int(round(self.camera_x))

    def get_camera_y(self):
        return int(round(self.camera_y))

    def begin_spellcast(self):
        if self.pending_spell is None:
            return
        self.pending_spell.begin_charging(self.get_center(), self.get_aim())

    def cancel_spellcast(self):
        self.pending_spell = None

    def get_chargebar_percentage(self):
        if self.pending_spell is not None and self.pending_spell.state == spells.Spell.CHARGING:
            return (self.pending_spell.charge_timer / self.pending_spell.CHARGE_TIME)
        else:
            return 0

    def toggle_spellwheel(self):
        if self.ui_state == self.NONE:
            self.ui_state = self.SPELLWHEEL
            self.ui_substate = self.CHOOSE_SPELL
            self.fade_alpha = 0
            self.make_spellcircle_items()
        elif self.ui_state == self.SPELLWHEEL:
            self.ui_state = self.NONE

    def get_spellcircle_coords(self, degree):
        ITEM_SIZE = 36

        y_offset = int(round(125 * math.sin(math.radians(degree))))
        x_offset = int(round(125 * math.cos(math.radians(degree))))

        return (self.SCREEN_CENTER_X - x_offset - (ITEM_SIZE // 2), self.SCREEN_CENTER_Y - y_offset - (ITEM_SIZE // 2), ITEM_SIZE, ITEM_SIZE)

    def make_spellcircle_items(self):
        self.spellcircle_items = []

        castable_spells = []
        for item in self.inventory.keys():
            if item.startswith("spellbook-"):
                castable_spells.append((item, self.inventory[item]))
        if self.health >= 1:
            needle_charges = int(self.health)
            castable_spells.append(("spellbook-needle", needle_charges))

        if len(castable_spells) == 0:
            return

        degree_padding = 360 / len(castable_spells)
        for i in range(0, len(castable_spells)):
            entry = []
            entry.append(castable_spells[i][0])
            entry.append(castable_spells[i][1])
            entry.append(self.get_spellcircle_coords(90 + (i * degree_padding)))
            self.spellcircle_items.append(entry)

    def add_item(self, shortname, quantity=1):
        if shortname in self.inventory.keys():
            self.inventory[shortname] += quantity
        else:
            self.inventory[shortname] = quantity

    def remove_item(self, shortname, quantity=1):
        if shortname not in self.inventory.keys():
            print("Error! Tried to remove item of which player has none")
            return

        self.inventory[shortname] -= quantity
        if self.inventory[shortname] <= 0:
            self.inventory.pop(shortname)
