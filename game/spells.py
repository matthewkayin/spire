# import math
from . import entity, util


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

    def __init__(self, tag, source, duration, end_lag=0, duplicate_behavior=EXCLUDE_SAME_TAG, ignoreable=False):
        self.DURATION = duration
        self.END_LAG = end_lag
        self.tag = tag
        self.source = source
        self.duplicate_behavior = duplicate_behavior
        self.ignoreable = ignoreable

        self.reset()

    def update(self, dt, target):
        if self.ignoreable and target.ignores_some_interactions:
            self.duration_timer = self.DURATION
            self.end_lag_timer = self.END_LAG
            self.ended = True
            self.state = Interaction.ENDED
            self.enable_effect = False
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
    def __init__(self, tag, source, duration, image_append=""):
        super(Interaction_Stun, self).__init__(tag, source, duration, 0, Interaction.EXTEND_SAME_TAG)
        self.image_append = image_append

    def update(self, dt, target):
        if self.enable_effect:
            target.vx, target.vy = (0, 0)
            target.image_append = self.image_append
            target.attacking = False
            target.deal_damage = False

        super(Interaction_Stun, self).update(dt, target)


class Interaction_Slow(Interaction):
    def __init__(self, tag, source, duration, percent):
        super(Interaction_Slow, self).__init__(tag, source, duration, 0, Interaction.EXTEND_SAME_TAG)
        self.percent = percent

    def update(self, dt, target):
        if self.enable_effect:
            target.vx *= self.percent
            target.vy *= self.percent
            target.attack_speed_percent = self.percent

        super(Interaction_Slow, self).update(dt, target)


class Interaction_Plague(Interaction):
    def __init__(self, tag, source, duration):
        super(Interaction_Plague, self).__init__(tag, source, duration, 10, Interaction.EXCLUDE_SAME_SOURCE, True)

    def update(self, dt, target):
        if self.state == Interaction.END_LAGGING:
            target.health = 0

        super(Interaction_Plague, self).update(dt, target)


"""
SPELLS
"""


def get_by_name(shortname):
    if shortname == "fire":
        return Fire()
    elif shortname == "needle":
        return Needle()
    elif shortname == "golem":
        return Golem()
    elif shortname == "thorns":
        return Thorns()
    elif shortname == "teleport":
        return Teleport()
    else:
        print("Error! Spell " + shortname + " hasn't been added to spells.get_by_name()")
        return None


# TODO handle spell projectile collisions when they exit the room without hitting the walls
# TODO prevent golem from spawn outside map


class Spell(entity.Entity):
    # State constants
    ENDED = -1
    AIMING = 0
    CHARGING = 1
    CAST_READY = 2

    def __init__(self, images, aim_image_index, charge_time, aim_radius, needs_room_aim=False):
        super(Spell, self).__init__(images[aim_image_index], True)

        self.state = Spell.AIMING
        self.charge_timer = 0
        self.CHARGE_TIME = charge_time
        self.AIM_RADIUS = aim_radius
        self.NEEDS_ROOM_AIM = needs_room_aim

        self.start = None
        self.target = None

        self.source_id = get_interaction_source()
        self.interact = False
        self.handles_collisions = False
        self.requests_enemies = False

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

    def get_subrenderables(self):
        return []

    def end_spell(self):
        self.interact = False
        self.handles_collisions = False
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


class Needle(Spell):
    # State constants
    PROJECTILE = 3
    AOE = 4

    PROJECTILE_SPEED = 3
    AOE_DURATION = 30

    def __init__(self):
        super(Needle, self).__init__(["icicle", "plague-cloud"], 0, 20, 50)

        self.aoe_timer = 0
        self.applied_needle_damage = False

    def update(self, dt):
        if self.state == Needle.AOE:
            self.aoe_timer += dt
            if self.aoe_timer >= Needle.AOE_DURATION:
                self.end_spell()

        super(Needle, self).update(dt)

    def cast(self):
        if self.state == Spell.CAST_READY:
            self.x, self.y = self.get_aim_coords(self.start, self.target)
            distance_vector = ((self.x + 10) - self.start[0], (self.y + 10) - self.start[1])
            self.vx, self.vy = util.scale_vector(distance_vector, self.PROJECTILE_SPEED)
            self.interact = True
            self.handles_collisions = True
            self.state = Needle.PROJECTILE

    def get_interactions(self):
        if self.state == Needle.PROJECTILE and not self.applied_needle_damage:
            return [Interaction_Damage("blood_damage", self.source_id, 3), Interaction_Plague("needle_plague", self.source_id, 60 * 15)]
            self.applied_needle_damage = True
        else:
            return [Interaction_Plague("needle_plague", self.source_id, 60 * 15)]

    def handle_collision(self):
        if self.state == Needle.PROJECTILE:
            self.vx, self.vy = (0, 0)
            self.rotation = None
            self.image = self.images[1]
            self.update_rect()
            self.x, self.y = (self.x - (self.width // 2), self.y - (self.height // 2))
            self.state = Needle.AOE

    def is_aim_valid(self, start, target):
        return True

    def get_aim_coords(self, start, target):
        distance_vector = (target[0] - start[0], target[1] - start[1])
        scaled_vector = util.scale_vector(distance_vector, 50)
        self.rotation = util.get_point_angle(start, target) - 90
        return (start[0] + scaled_vector[0] + self.offset_x, start[1] + scaled_vector[1] + self.offset_y)


class Fire(Spell):
    # State constants
    PROJECTILE = 3
    AOE = 4

    PROJECTILE_SPEED = 3
    AOE_DURATION = 60 * 3

    def __init__(self):
        super(Fire, self).__init__(["projectile-fire", "explosion"], 1, 60, 250)

        self.aoe_timer = 0

    def update(self, dt):
        if self.state == Fire.PROJECTILE:
            if util.get_distance((self.x + self.width // 2, self.y + self.height // 2), self.target) <= 5:
                self.vx, self.vy = (0, 0)
                self.x, self.y = self.target[0] - 35, self.target[1] - 35
                self.interact = True
                self.image = self.images[1]
                self.update_rect()
                self.state = Fire.AOE
        elif self.state == Fire.AOE:
            self.aoe_timer += dt
            if self.aoe_timer >= Fire.AOE_DURATION:
                self.end_spell()

        super(Fire, self).update(dt)

    def cast(self):
        self.x, self.y = self.start
        distance_vector = (self.target[0] - self.start[0], self.target[1] - self.start[1])
        self.vx, self.vy = util.scale_vector(distance_vector, Fire.PROJECTILE_SPEED)
        self.image = self.images[0]
        self.update_rect()
        self.handles_collisions = True
        self.state = Fire.PROJECTILE

    def get_interactions(self):
        return [Interaction_Damage("fire_damage", self.source_id, 1 / 10.0, 1), Interaction_Slow("fire_slow", self.source_id, 1, 0.4)]

    def handle_collision(self):
        if self.state == Fire.PROJECTILE:
            self.target = self.x, self.y
            self.vx, self.vy = (0, 0)
        return

    def is_aim_valid(self, start, target):
        return util.get_distance(start, target) <= self.AIM_RADIUS

    def get_aim_coords(self, start, target):
        return (target[0] - 35, target[1] - 35)


class Golem(Spell):
    # State constants
    GOLEM = 3
    WAIT = 4

    GOLEM_DURATION = 30 * 60
    FIRE_DURATION = 20

    BULLET_SPEED = 3

    def __init__(self):
        super(Golem, self).__init__(["golem-guy", "projectile-rock"], 0, 60, 200, True)

        self.golem_timer = 0
        self.fire_timer = 0
        self.requests_enemies = True
        self.enemies = []
        self.recent_collider = None

        self.bullets = []
        self.bullet_targets = []

    def get_subrenderables(self):
        subrenderables = []
        if len(self.bullets) > 0:
            subrenderable_item = []
            subrenderable_item.append(self.bullets[0].get_image())
            for bullet in self.bullets:
                subrenderable_item.append((bullet.get_x(), bullet.get_y()))
            subrenderables.append(subrenderable_item)

        return subrenderables

    def update(self, dt):
        for bullet in self.bullets:
            if len(self.enemies) != 0:
                nearest_index = 0
                nearest_distance = util.get_distance(bullet.get_center(), self.enemies[0])
                for i in range(1, len(self.enemies)):
                    distance = util.get_distance(bullet.get_center(), self.enemies[i])
                    if distance < nearest_distance:
                        nearest_distance = distance
                        nearest_index = i
                distance_vector = (self.enemies[nearest_index][0] - bullet.x, self.enemies[nearest_index][1] - bullet.y)
                bullet.vx, bullet.vy = util.scale_vector(distance_vector, Golem.BULLET_SPEED)
            bullet.update(dt)

        if self.state == Golem.GOLEM:
            self.golem_timer += dt
            if self.golem_timer >= Golem.GOLEM_DURATION:
                self.state = Golem.WAIT
            self.fire_timer += dt
            if self.fire_timer >= Golem.FIRE_DURATION:
                if len(self.enemies) != 0:
                    self.fire_timer = 0
                    self.spawn_bullet()
        elif self.state == Golem.WAIT:
            if len(self.bullets) == 0:
                self.end_spell()

        super(Golem, self).update(dt)

    def spawn_bullet(self):
        new_bullet = entity.Entity(self.images[1], True)
        new_bullet.x, new_bullet.y = self.x, self.y
        self.bullets.append(new_bullet)

    def collides(self, other):
        self.recent_collider = other
        remove_indeces = [i for i in range(0, len(self.bullets)) if self.bullets[i].collides(other)]
        self.bullets = [self.bullets[i] for i in range(0, len(self.bullets)) if i not in remove_indeces]

        return len(remove_indeces) > 0

    def cast(self):
        self.state = Golem.GOLEM
        self.x, self.y = self.get_aim_coords(self.start, self.target)
        self.handles_collisions = True
        self.interact = True

    def get_interactions(self):
        return [Interaction_Damage("golem_damage", self.source_id, 1)]

    def handle_collision(self):
        return

    def is_aim_valid(self, start, target):
        return util.get_distance(start, target) <= self.AIM_RADIUS

    def get_aim_coords(self, start, target):
        return (target[0] - (self.width // 2), target[1] - (self.height // 2))


class Thorns(Spell):
    # State constants
    AOE = 3

    AOE_DURATION = 10

    def __init__(self):
        super(Thorns, self).__init__(["brambles"], 0, 60, 142)

        self.aoe_timer = 0

    def update(self, dt):
        if self.state == Thorns.AOE:
            self.aoe_timer += dt
            if self.aoe_timer >= Thorns.AOE_DURATION:
                self.end_spell()

        super(Thorns, self).update(dt)

    def cast(self):
        self.state = Thorns.AOE
        self.x, self.y = self.get_aim_coords(self.start, self.target)
        self.handles_collisions = True
        self.interact = True

    def get_interactions(self):
        return [Interaction_Damage("thorn_damage", self.source_id, 2, 10), Interaction_Stun("thorn_stun", self.source_id, 60 * 2, "-brambles")]

    def handle_collision(self):
        return

    def is_aim_valid(self, start, target):
        return True

    def get_aim_coords(self, start, target):
        return (start[0] - (self.width // 2), start[1] - (self.height // 2))


class Teleport(Spell):
    TELEPORT = 3

    def __init__(self):
        super(Teleport, self).__init__(["player-idle"], 0, 20, 300, True)

    def get_teleport_coords(self):
        return self.get_aim_coords(self.start, self.target)

    def cast(self):
        return

    def get_interactions(self):
        return []

    def handle_collision(self):
        return

    def is_aim_valid(self, start, target):
        return util.get_distance(start, target) <= self.AIM_RADIUS

    def get_aim_coords(self, start, target):
        return (target[0] - (self.width // 2), target[1] - (self.height // 2))
