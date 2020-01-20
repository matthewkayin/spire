# import math
from . import entity, resources, util


"""
INTERACTIONS
"""

interaction_source_counter = 0


def get_interaction_source():
    global interaction_source_counter

    if interaction_source_counter >= 100:
        interaction_source_counter = 0
    else:
        interaction_source_counter += 1
    return interaction_source_counter


class Interaction():
    # state constants
    INTERACTING = 0
    END_LAGGING = 1
    ENDED = -1

    # duplication behavior constants
    EXCLUDE_SAME_TAG = 0
    EXCLUDE_SAME_SOURCE = 1
    EXTEND_SAME_TAG = 2

    def __init__(self, tag, source, duration, end_lag=0, duplicate_behavior=EXCLUDE_SAME_TAG):
        self.DURATION = duration
        self.END_LAG = end_lag
        self.tag = tag
        self.source = source
        self.duplicate_behavior = duplicate_behavior

        self.reset()

    def update(self, dt, target):
        if self.state == Interaction.INTERACTING:
            self.duration_timer += dt
            if self.duration_timer >= self.DURATION:
                self.enable_effect = False
                self.state = Interaction.END_LAGGING
        elif self.state == Interaction.END_LAGGING:
            self.end_lag_timer += dt
            if self.end_lag_timer >= self.END_LAG:
                self.ended = True
                self.state = Interaction.ENDED

    def reset(self):
        self.duration_timer = 0
        self.end_lag_timer = 0
        self.enable_effect = True
        self.ended = False
        self.state = Interaction.INTERACTING


class Interaction_Damage(Interaction):
    def __init__(self, tag, source, damage, end_lag=0):
        super(Interaction_Damage, self).__init__(tag, source, 0, end_lag, Interaction.EXCLUDE_SAME_SOURCE)
        self.DAMAGE = damage

    def update(self, dt, target):
        if self.enable_effect:
            target.health -= self.DAMAGE

        super(Interaction_Damage, self).update(dt, target)


class Interaction_Stun(Interaction):
    def __init__(self, tag, source, duration):
        super(Interaction_Stun, self).__init__(tag, source, duration, 0, Interaction.EXTEND_SAME_TAG)

    def update(self, dt, target):
        if self.enable_effect:
            target.vx, target.vy = (0, 0)

        super(Interaction_Stun, self).update(dt, target)


"""
SPELLS
"""


def load_spell_images():
    resources.load_image("fire", True)
    resources.load_image("spellbook-fire", True)


def get_by_name(shortname):
    if shortname == "fire":
        return Fire()


class Spell(entity.Entity):
    # State constants
    ENDED = -1
    AIMING = 0
    CHARGING = 1
    CAST_READY = 2

    def __init__(self, images, aim_image_index, charge_time, aim_radius):
        super(Spell, self).__init__(images[aim_image_index], True)

        self.state = Spell.AIMING
        self.charge_timer = 0
        self.CHARGE_TIME = charge_time
        self.AIM_RADIUS = aim_radius

        self.start = None
        self.target = None

        self.source_id = get_interaction_source()
        self.interact = False

        for image in images:
            resources.load_image(image, True)
        resources.create_fade_image(images[aim_image_index], 128)  # For when aiming, always use first image at alpha 128
        # The shortname is exclusively used to image loading

        self.images = images
        self.image = self.images[aim_image_index]

    def update(self, dt):
        if self.state == Spell.CHARGING:
            self.charge_timer += dt
            if self.charge_timer >= self.CHARGE_TIME:
                self.state = Spell.CAST_READY

        super(Spell, self).update(dt)

    def get_image(self):
        if self.state == Spell.AIMING:
            return super(Spell, self).get_image(128)
        else:
            return super(Spell, self).get_image()

    def end_spell(self):
        self.interact = False
        self.state = Spell.ENDED

    def begin_charging(self, start, target):
        self.state = Spell.CHARGING
        self.start = start
        self.target = target

    def cast(self):
        raise NotImplementedError("Need to impliment abstract function Spell.cast()")

    def get_interactions(self):
        raise NotImplementedError("Need to impliment abstract function Spell.get_interactions()")

    def handle_collision(self):
        raise NotImplementedError("Need to impliment abstract function Spell.handle_collision()")

    def is_aim_valid(self, start, target):
        raise NotImplementedError("Need to impliment abstract function Spell.is_aim_valid()")

    def get_aim_coords(self, start, target):
        raise NotImplementedError("Need to impliment abstract function Spell.get_aim_coords()")


class Fire(Spell):
    # State constants
    PROJECTILE = 3
    AOE = 4

    PROJECTILE_SPEED = 3

    def __init__(self):
        super(Fire, self).__init__(["projectile-fire", "explosion"], 1, 60, 250)

        self.aoe_timer = 0
        self.AOE_DURATION = 60 * 3

    def update(self, dt):
        if self.state == Fire.PROJECTILE:
            if util.get_distance((self.x, self.y), self.target) <= 5:
                self.vx, self.vy = (0, 0)
                self.x, self.y = self.target[0] - 25, self.target[1] - 25
                self.interact = True
                self.image = self.images[1]
                self.update_rect()
                self.state = Fire.AOE
        elif self.state == Fire.AOE:
            self.aoe_timer += dt
            if self.aoe_timer >= self.AOE_DURATION:
                self.end_spell()

        super(Fire, self).update(dt)

    def cast(self):
        self.x, self.y = self.start
        distance_vector = (self.target[0] - self.start[0], self.target[1] - self.start[1])
        self.vx, self.vy = util.scale_vector(distance_vector, Fire.PROJECTILE_SPEED)
        self.image = self.images[0]
        self.update_rect()
        self.state = Fire.PROJECTILE

    def get_interactions(self):
        return [Interaction_Damage("fire_damage", self.source_id, 1, 60)]

    def handle_collision(self):
        return

    def is_aim_valid(self, start, target):
        return util.get_distance(start, target) <= self.AIM_RADIUS

    def get_aim_coords(self, start, target):
        return (target[0] - 25, target[1] - 25)
