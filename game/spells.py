from . import entity, resources, util


def load_spell_images():
    resources.load_image("explosion", True)
    resources.load_image("projectile-fire", True)


class Spell(entity.Entity):
    # Static state name constants for all spells, subclasses should define their own based on behavior
    ENDED = -1
    CHARGING = 0
    CAST_READY = 1

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
        self.deal_damage = False
        self.DAMAGE = 0

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


class Fire(Spell):
    # State constants
    PROJECTILE = 2
    AOE = 3

    def __init__(self, start_x, start_y, target_x, target_y):
        super(Fire, self).__init__("fire", 30, "explosion")

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
                self.deal_damage = True
                self.aoe_timer = 0
                self.state = Fire.AOE
        elif self.state == Fire.AOE:
            self.aoe_timer += dt
            if self.aoe_timer >= self.AOE_DURATION:
                self.deal_damage = False
                self.state = Spell.ENDED

    def cast(self):
        if self.state == Spell.CAST_READY:
            distance_vector = ((self.target_x - self.x, self.target_y - self.y))
            self.vx, self.vy = util.scale_vector(distance_vector, self.PROJECTILE_SPEED)
            self.image = "projectile-fire"
            self.state = Fire.PROJECTILE