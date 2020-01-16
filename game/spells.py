import math
from . import entity, resources, util


def load_spell_images():
    resources.load_image("fire", True)
    resources.load_image("explosion", True)
    resources.create_fade_image("explosion", 128)
    resources.load_image("projectile-fire", True)
    resources.load_image("icicle", True)
    resources.create_fade_image("icicle", 128)
    resources.load_image("spellbook-fire", True)
    resources.load_image("spellbook-ice", True)
    resources.load_image("ice", True)
    resources.load_image("lightning", True)
    resources.load_image("target", True)
    resources.create_fade_image("target", 128)


def get_aim_info(shortname, start_x, start_y, target_x, target_y):
    if shortname == "fire":
        coords = Fire.get_aim_coords(start_x, start_y, target_x, target_y)
        return (resources.get_fade_image("explosion", 128), coords)
    elif shortname == "ice":
        coords = Ice.get_aim_coords(start_x, start_y, target_x, target_y)
        angle = util.get_point_angle((start_x, start_y), (target_x, target_y)) - 90
        image, offset = resources.rotate(resources.get_fade_image("icicle", 128), angle)
        coords = (coords[0] + offset[0], coords[1] + offset[1])
        return (image, coords)
    elif shortname == "lightning":
        coords = (target_x - 4, target_y - 4)
        image = resources.get_fade_image("target", 128)

        return (image, coords)


def get_aim_radius(shortname):
    if shortname == "fire":
        return Fire.AOE_RANGE
    elif shortname == "ice":
        return 50
    elif shortname == "lightning":
        return Lightning.AIM_RANGE


def requires_specific_target(shortname):
    return shortname == "lightning"


def is_aim_valid(shortname, start_x, start_y, target_x, target_y):
    if shortname == "fire":
        return Fire.check_target(start_x, start_y, target_x, target_y)
    elif shortname == "ice":
        return True
    elif shortname == "lightning":
        return True


def get_spell(shortname, start_x, start_y, target_x, target_y):
    if shortname == "fire":
        return Fire(start_x + 5, start_y, target_x, target_y)
    elif shortname == "ice":
        return Ice(start_x, start_y, target_x, target_y)
    elif shortname == "lightning":
        return Lightning(start_x + 5, start_y - 7, target_x, target_y)


class Spell(entity.Entity):
    # Static state name constants for all spells, subclasses should define their own based on behavior
    ENDED = -1
    CHARGING = 0
    CAST_READY = 1

    # Spell action constants
    DAMAGE = 0
    FREEZE = 1

    def get_aim_coords(shortname, start_x, start_y, target_x, target_y):
        raise NotImplementedError("Cannot get aim coords on a generic spell, please impliment abstract method Spell.get_aim_coords()")

    """
    A note on states and behaviors
    When casting the spell the player class should check if the required spellbook is in their inventory
    If it is, then they should begin casting, but if the player cancels the spellcast we want them to keep
    their item, so we should charge, then when we're done charging the player sees the spell is in state CAST_READY
    The player subtracts the item from their inventory and then calls Spell.cast(), which begins the rest of the spell
    """

    def __init__(self, shortname, charge_time, image):
        super(Spell, self).__init__(image, True)

        self.shortname = shortname
        self.CHARGE_TIME = charge_time
        self.charge_timer = 0
        self.state = Spell.CHARGING
        self.image = image
        self.action = None
        self.action_value = 0
        self.target = None  # Target is a specific use case spell

    def update(self, dt):
        if self.state == self.CHARGING:
            self.charge_timer += dt
            if self.charge_timer >= self.CHARGE_TIME:
                self.state = self.CAST_READY
        elif self.state != self.CAST_READY:
            super(Spell, self).update(dt)

    def cast(self):
        """
        Specific to the spell, called by the player cast after subtracting the required item
        """
        raise NotImplementedError("Cannot cast spell without implimenting abstract method Spell.cast()")

    def end_spell(self):
        self.action = None
        self.state = Spell.ENDED

    def handle_collision(self):
        """
        Needs to be castable on all spells but only implimented in some spells
        """
        return


class Fire(Spell):
    # State constants
    PROJECTILE = 2
    AOE = 3

    AOE_RANGE = 200

    def get_aim_coords(start_x, start_y, target_x, target_y):
        return (target_x - 25, target_y - 25)

    def check_target(start_x, start_y, target_x, target_y):
        return math.sqrt(((target_x - start_x) ** 2) + ((target_y - start_y) ** 2)) <= Fire.AOE_RANGE

    def __init__(self, start_x, start_y, target_x, target_y):
        super(Fire, self).__init__("fire", 120, "explosion")

        self.target_x = target_x
        self.target_y = target_y
        self.x = start_x
        self.y = start_y

        self.DAMAGE = 1
        self.PROJECTILE_SPEED = 3
        self.AOE_DURATION = 60
        self.aoe_timer = 0

    def update(self, dt):
        super(Fire, self).update(dt)
        if self.state == Fire.PROJECTILE:
            if abs(self.x - self.target_x) <= 5 and abs(self.y - self.target_y) <= 5:
                self.x = self.target_x - (self.width // 2)
                self.y = self.target_y - (self.height // 2)
                self.vx, self.vy = (0, 0)
                self.image = "explosion"
                self.action = Spell.DAMAGE
                self.action_value = self.DAMAGE
                self.aoe_timer = 0
                self.state = Fire.AOE
        elif self.state == Fire.AOE:
            self.aoe_timer += dt
            if self.aoe_timer >= self.AOE_DURATION:
                self.end_spell()

    def cast(self):
        if self.state == Spell.CAST_READY:
            distance_vector = (self.target_x - self.x, self.target_y - self.y)
            self.vx, self.vy = util.scale_vector(distance_vector, self.PROJECTILE_SPEED)
            self.image = "projectile-fire"
            self.state = Fire.PROJECTILE


class Ice(Spell):
    # State constants
    PROJECTILE = 2

    def get_aim_coords(start_x, start_y, target_x, target_y):
        distance_vector = (target_x - start_x, target_y - start_y)
        scaled_vector = util.scale_vector(distance_vector, 50)
        return (start_x + scaled_vector[0], start_y + scaled_vector[1])

    def __init__(self, start_x, start_y, target_x, target_y):
        super(Ice, self).__init__("ice", 30, "icicle")

        self.x, self.y = Ice.get_aim_coords(start_x, start_y, target_x, target_y)
        self.start_x = start_x
        self.start_y = start_y
        self.rotation = util.get_point_angle((start_x, start_y), (target_x, target_y)) - 90

        self.PROJECTILE_SPEED = 3

    def cast(self):
        if self.state == Spell.CAST_READY:
            distance_vector = (self.x - self.start_x, self.y - self.start_y)
            self.vx, self.vy = util.scale_vector(distance_vector, self.PROJECTILE_SPEED)
            self.state = Ice.PROJECTILE
            self.action = Spell.FREEZE
            self.action_value = 60 * 5

    def handle_collision(self):
        self.end_spell()


class Lightning(Spell):
    # State constants
    EFFECT = 2

    AIM_RANGE = 200

    def __init__(self, start_x, start_y, target_x, target_y):
        super(Lightning, self).__init__("lightning", 60, "bolt")

        self.start_x, self.start_y = start_x, start_y

        self.effect_timer = 0
        self.EFFECT_DURATION = 30

    def update(self, dt):
        super(Lightning, self).update(dt)

        if self.state == Lightning.EFFECT:
            if self.action_value > 0:
                self.target.handle_spell_action(self.action, self.action_value)
                self.action_value = 0
            self.effect_timer += dt
            if self.effect_timer >= self.EFFECT_DURATION:
                self.end_spell()

    def cast(self):
        if self.state == Spell.CAST_READY:
            target_x, target_y = self.target.get_x() + self.target.width // 2, self.target.get_y() + self.target.height // 2
            self.x, self.y = target_x, target_y
            self.length = int(math.sqrt(((target_x - self.start_x) ** 2) + ((target_y - self.start_y) ** 2)))
            self.rotation = util.get_point_angle((self.start_x, self.start_y), (target_x, target_y))
            self.state = Lightning.EFFECT
            self.action = Spell.DAMAGE
            self.action_value = 1
