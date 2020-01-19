import math
from . import entity, resources, util


"""
TODO
Think of a better tag system that incorporates the ability to differentiate between the
behavior of duplicate effects from the same source (i.e. don't stack damage on the same
spell) and effects from different sources (i.e. do stack damage on spells of the same type
but that are different spells).

Example "user story" of this. Say we have an aoe fire spell. Say the spell deals 3 damage/per
second so long as an enemy is within the fire, beginning when the enemy enters. This is easy
to impliment with unique tags: fire damage is given a tag like "fire damage" and then we say don't
duplicate this tag. So each update the game tries to give the enemy a "fire damage" tag but the
enemy rejects this tag because it already has one. So it will only accept a fire damage tag when
the old fire damage tag has expired, and is cleaned out of the inventory. So we can create the
desired spell interaction with an Interaction_Damage tag that has a damage of 3 and an end lag
of 60 updates (1 second).

The problem with this is in two cases. Case 1, the enemy steps outside of the AOE fire spell and
then steps back inside of it. Expected behavior in my mind is that the enemy will receive a second
dose of fire damage when they step back inside of it, however if the enemy steps in and out of the
fire in one second, the end lag on the first Interaction_Damage will still be going, and that end
lag is for 3 seconds, so the enemy won't actually take any additional damage. Case 2, the player
somehow lays down two fire AOE spells at once. They're both of the same class so they have an the
same tag, which means that the effects of an Interaction_Damage tag won't stack and the enemy
will receive damage from only one AOE even if they step into both. Also there's another case I can
think of: Say the player freezes an enemy and then applies a new freeze spell to the enemy. Expected
behavior of this is that the enemy should have the freeze effect extended to the duration of one whole
freeze spell. You could solve this by allowing the freeze effects to stack, then they would both time
out at once which would create the effect we want, but I can see this being inefficient in the long term
because we're updating an object that doesn't need to be updated, I would suggest a different tag system
to somehow reconcile all three of these cases lol
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
We're doing a separate branch to attempt a revamp of the current spell system
The current spell system is very tightly coupled with other elements of the game
and while there are hints of loose coupling present in the code the current design
of the code ultimately makes adding new spells and making changes overall very difficult

To me, the sign that I needed to change the code design was when I needed to edit the Ice
class to make the damage effects work for the Lightning class...
"""


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


def get_aim_radius(shortname):
    if shortname == "fire":
        return Fire.AOE_RANGE
    elif shortname == "ice":
        return 50


def is_aim_valid(shortname, start_x, start_y, target_x, target_y):
    if shortname == "fire":
        return Fire.check_target(start_x, start_y, target_x, target_y)
    elif shortname == "ice":
        return True


def get_spell(shortname, start_x, start_y, target_x, target_y):
    if shortname == "fire":
        return Fire(start_x + 5, start_y, target_x, target_y)
    elif shortname == "ice":
        return Ice(start_x, start_y, target_x, target_y)


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
        self.interact = False
        self.target = None  # Target is a specific use case spell

        self.source_id = get_interaction_source()

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
        self.interact = False
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
        super(Fire, self).__init__("fire", 10, "explosion")

        self.target_x = target_x
        self.target_y = target_y
        self.x = start_x
        self.y = start_y

        self.DAMAGE = 1
        self.PROJECTILE_SPEED = 3
        self.AOE_DURATION = 60 * 3
        self.aoe_timer = 0

    def update(self, dt):
        super(Fire, self).update(dt)
        if self.state == Fire.PROJECTILE:
            if abs(self.x - self.target_x) <= 5 and abs(self.y - self.target_y) <= 5:
                self.x = self.target_x - (self.width // 2)
                self.y = self.target_y - (self.height // 2)
                self.vx, self.vy = (0, 0)
                self.image = "explosion"
                self.interact = True
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

    def get_interactions(self):
        return [Interaction_Damage("fire_damage", self.source_id, 1, 60)]


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
            self.interact = True

    def handle_collision(self):
        self.end_spell()

    def get_interactions(self):
        return [Interaction_Stun("freeze", self.source_id, 60 * 5)]
