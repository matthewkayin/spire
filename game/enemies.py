from . import entity, util, spells
import random
import math


class Interaction():
    """
    A player specific interaction class.
    These are the same concept as the ones used to affect enemies but they affect players instead
    """

    def __init__(self):
        self.ended = False

    def update(self, dt, target):
        raise NotImplementedError("Need to impliement abstract function enemy.Interaction.update()")


class Interaction_Damage(Interaction):
    def __init__(self, damage):
        self.damage = damage

    def update(self, dt, target):
        target.health -= self.damage
        self.ended = True


class Interaction_Impulse(Interaction):
    def __init__(self, source_pos):
        self.source_pos = source_pos

    def update(self, dt, target):
        distance_vector = (target.x - self.source_pos[0], target.y - self.source_pos[1])
        target.impulse_x, target.impulse_y = util.scale_vector(distance_vector, target.IMPULSE_SPEED)
        target.impulse_timer = 0
        self.ended = True


class Interaction_Slow(Interaction):
    def __init__(self, speed_percent):
        self.speed_percent = speed_percent

    def update(self, dt, target):
        target.speed_percent = self.speed_percent
        self.ended = True


class Enemy(entity.Entity):
    """
    Class for a basic enemy
    """

    def __init__(self, image, x, y, move_speed, starting_health, ignores_some_interactions=False):
        super(Enemy, self).__init__(image, True)
        self.x, self.y = x, y

        self.MOVE_SPEED = move_speed

        self.attacking = False
        self.attack_timer = 0
        self.attack_speed_percent = 1
        self.ATTACK_SPEED = 10

        self.deal_damage = False
        self.hurtbox = None
        self.POWER = 0.5

        self.health = starting_health
        self.max_health = starting_health
        self.delete_me = False
        self.ignores_some_interactions = ignores_some_interactions
        self.interactions = []

    def get_subrenderables(self):
        return []

    def update(self, dt, player_rect):
        if self.health <= 0:
            self.handle_death()

        self.do_ai(dt, player_rect)

        # reset attack speed each update so that when interactions fizzle out attack speed returns to normal
        self.attack_speed_percent = 1

        self.image_append = ""
        for interaction in self.interactions:
            interaction.update(dt, self)
        self.interactions = [interaction for interaction in self.interactions if not interaction.ended]

        super(Enemy, self).update(dt)

    def handle_death(self):
        self.delete_me = True

    def do_ai(self, dt, player_rect):
        """
        This is a to-be-implimented function for each enemy and it describes the specific AI behavior
        for the enemy. The function is then called during update
        """
        raise NotImplementedError("Need to impliment abstract function enemy.do_ai()")

    def get_hurtboxes(self):
        raise NotImplementedError("Need to impliment abstract function Enemy.get_hurtboxes()")

    def add_interaction(self, interaction):
        if interaction.tag in [other_interaction.tag for other_interaction in self.interactions]:
            if interaction.duplicate_behavior == spells.Interaction.EXCLUDE_SAME_TAG:
                return
            elif interaction.duplicate_behavior == spells.Interaction.EXCLUDE_SAME_SOURCE:
                if interaction.source in [interaction.source for interaction in self.interactions]:
                    return
            elif interaction.duplicate_behavior == spells.Interaction.EXTEND_SAME_TAG:
                for extended_interaction in [ext_interaction for ext_interaction in self.interactions if ext_interaction.tag == interaction.tag]:
                    extended_interaction.reset()
                return
        self.interactions.append(interaction)

    def get_plague_meter_percent(self):
        has_plague = False
        smallest_time_left = None
        max_time = None
        for interaction in self.interactions:
            if isinstance(interaction, spells.Interaction_Plague):
                has_plague = True
                if smallest_time_left is None or interaction.duration_timer < smallest_time_left:
                    smallest_time_left = interaction.duration_timer
                    max_time = interaction.DURATION
                break

        if not has_plague:
            return None
        else:
            return smallest_time_left / max_time


class Enemy_Zombie(Enemy):
    """
    Class for the zombie
    """

    def __init__(self, x, y):
        super(Enemy_Zombie, self).__init__("mummy", x, y, 1, 3)

        self.FOLLOW_RANGE = 600
        self.ATTACK_SPEED = 10

    def do_ai(self, dt, player_rect):
        # If we finished an attack last turn, we want to reset these variables so the hit happens only once
        if self.deal_damage:
            self.hurtbox = None
            self.deal_damage = False

        # If we're in an attack windup
        if self.attacking:
            self.attack_timer += (dt * self.attack_speed_percent)
            if self.attack_timer >= self.ATTACK_SPEED:
                self.deal_damage = True
                self.attacking = False
        else:
            player_center = util.get_center(player_rect)
            self_center = self.get_center()
            player_distance = util.get_distance(self_center, player_center)
            if self.collides(player_rect):
                # begin an attack windup
                self.attacking = True
                self.hurtbox = player_rect
                self.attack_timer = 0
                self.vx, self.vy = (0, 0)
            elif player_distance <= self.FOLLOW_RANGE:
                # Vectorize movement relative to player
                vector_to_player = ((player_center[0] - self_center[0]), (player_center[1] - self_center[1]))
                self.vx, self.vy = util.scale_vector(vector_to_player, self.MOVE_SPEED)

    def get_hurtboxes(self):
        if self.deal_damage:
            return [(self.hurtbox, Interaction_Damage(self.POWER)), (self.hurtbox, Interaction_Impulse(self.get_center()))]
        else:
            return []


class Enemy_Slime(Enemy):
    """
    Class for the slime
    """

    ATTACK_RANGE = 200
    DESIRED_STRAFE_RADIUS = 200
    SLIMEBALL_STAY_TIME = 20 * 60
    PROJECTILE_SPEED = 3

    def __init__(self, x, y):
        super(Enemy_Slime, self).__init__("slime", x, y, 1, 3)

        self.angle_direction = 1
        self.randomize_angle = False
        self.target_pos = None

        self.slimeballs = []

        self.ATTACK_SPEED = 20
        self.next_attack_timer = 0
        self.NEXT_ATTACK_DURATION = 0

    def get_subrenderables(self):
        subrenderables = []
        for slimeball in self.slimeballs:
            subrenderables.append((slimeball[0].image, (slimeball[0].x, slimeball[0].y)))

        return subrenderables

    def handle_death(self):
        if len(self.slimeballs) == 0:
            self.delete_me = True

    def do_ai(self, dt, player_rect):
        for slimeball in self.slimeballs:
            if slimeball[2] == -1:
                distance_vector = (slimeball[1][0] - slimeball[0].x, slimeball[1][1] - slimeball[0].y)
                slimeball[0].vx, slimeball[0].vy = util.scale_vector(distance_vector, Enemy_Slime.PROJECTILE_SPEED)
                slimeball[0].update(dt)
                if util.point_in_rect(slimeball[1], slimeball[0].get_rect()):
                    slimeball[0].vx, slimeball[0].vy = (0, 0)
                    slimeball[0].image = "slime-puddle"
                    slimeball[0].update_rect()
                    slimeball[0].x, slimeball[0].y = (slimeball[1][0] - (slimeball[0].width // 2), slimeball[1][1] - (slimeball[0].height // 2))
                    slimeball[2] = 0
            else:
                slimeball[2] += dt
        self.slimeballs = [slimeball for slimeball in self.slimeballs if slimeball[2] < Enemy_Slime.SLIMEBALL_STAY_TIME]

        if self.health > 0:
            if self.attacking:
                self.attack_timer += (dt * self.attack_speed_percent)
                if self.attack_timer >= self.ATTACK_SPEED:
                    self.shoot_slimeball(util.get_center(player_rect))
                    self.attacking = False
            elif util.get_distance(util.get_center(player_rect), self.get_center()) <= Enemy_Slime.DESIRED_STRAFE_RADIUS + 100:
                if self.target_pos is not None:
                    distance_vector = (self.target_pos[0] - self.get_center()[0], self.target_pos[1] - self.get_center()[1])
                    self.vx, self.vy = util.scale_vector(distance_vector, self.MOVE_SPEED)
                    if util.point_in_rect(self.target_pos, (self.get_center()[0] - 2, self.get_center()[1] - 2, 2, 2)):
                        self.target_pos = None
                if self.target_pos is None:
                    player_center = util.get_center(player_rect)
                    current_angle = util.get_point_angle(player_center, self.get_center())
                    new_angle = 0
                    if self.randomize_angle:
                        self.randomize_angle = False
                        new_angle = random.randint(0, 359)
                    else:
                        new_angle = current_angle + (5 * self.angle_direction)
                    self.target_pos = (player_center[0] + (Enemy_Slime.DESIRED_STRAFE_RADIUS * math.cos(math.radians(new_angle))), player_center[1] - (Enemy_Slime.DESIRED_STRAFE_RADIUS * math.sin(math.radians(new_angle))))
                self.next_attack_timer += dt
                if self.next_attack_timer >= self.NEXT_ATTACK_DURATION:
                    self.attacking = True
                    self.attack_timer = 0
                    self.next_attack_timer = 0
                    self.NEXT_ATTACK_DURATION = random.randint(20, 40) * 60
                    self.vx, self.vy = (0, 0)
                    self.target_pos = None

    def shoot_slimeball(self, target_pos):
        slimeball_entity = entity.Entity("slimeball", True)
        slimeball_entity.x, slimeball_entity.y = self.get_center()
        self.slimeballs.append([slimeball_entity, target_pos, -1])

    def check_collision(self, dt, collider):
        collided = super(Enemy_Slime, self).check_collision(dt, collider)
        if collided:
            self.target_pos = None
            self.vx, self.vy = (0, 0)
            self.randomize_angle = True

    def get_hurtboxes(self):
        hurtboxes = []
        for slimeball in self.slimeballs:
            if slimeball[2] == 0:
                hurtboxes.append([slimeball[0].get_rect(), Interaction_Damage(1), Interaction_Slow(0.5)])
            elif slimeball[2] > 0:
                hurtboxes.append([slimeball[0].get_rect(), Interaction_Slow(0.5)])

        return hurtboxes
