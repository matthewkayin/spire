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
        target.take_hit(self.damage)
        self.ended = True


class Interaction_Impulse(Interaction):
    def __init__(self, source_pos, speed_scale=1, degree=0):
        self.source_pos = source_pos
        self.speed_scale = speed_scale
        self.degree = degree

    def update(self, dt, target):
        distance_vector = (target.x - self.source_pos[0], target.y - self.source_pos[1])
        target.impulse_x, target.impulse_y = util.scale_vector(distance_vector, target.IMPULSE_SPEED * self.speed_scale)
        if self.degree != 0:
            old_x = target.impulse_x
            old_y = target.impulse_y
            angle = math.radians(self.degree)
            target.impulse_x = (old_x * math.cos(angle)) - (old_y * math.sin(angle))
            target.impulse_y = (old_x * math.sin(angle)) + (old_y * math.cos(angle))
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

    def __init__(self, image, x, y, move_speed, starting_health):
        super(Enemy, self).__init__(image, True)
        self.x, self.y = x, y
        self.check_entity_collisions = True

        self.MOVE_SPEED = move_speed

        self.attacking = False
        self.attack_timer = 0
        self.attack_speed_percent = 1
        self.ATTACK_SPEED = 10

        self.deal_damage = False
        self.hurtbox = None
        self.POWER = 0.5

        self.is_boss = False
        self.health = starting_health
        self.max_health = starting_health
        self.delete_me = False
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
    FOLLOW_RANGE = 300
    SLIMEBALL_STAY_TIME = 20 * 60
    PROJECTILE_SPEED = 3

    def __init__(self, x, y):
        super(Enemy_Slime, self).__init__("slime", x, y, 1, 3)

        self.slimeballs = []

        self.ATTACK_SPEED = 20
        self.next_attack_timer = 0
        self.NEXT_ATTACK_TIME = 60

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
            else:
                player_center = util.get_center(player_rect)
                self_center = self.get_center()
                player_distance = util.get_distance(self_center, player_center)
                if player_distance <= Enemy_Slime.FOLLOW_RANGE:
                    self.next_attack_timer += dt
                    if player_distance <= Enemy_Slime.ATTACK_RANGE:
                        self.vx, self.vy = (0, 0)
                        if self.next_attack_timer >= self.NEXT_ATTACK_TIME:
                            self.attacking = True
                            self.attack_timer = 0
                            self.next_attack_timer = 0
                            self.NEXT_ATTACK_TIME = random.randint(1, 10) * 60
                    else:
                        # Vectorize movement relative to player
                        vector_to_player = ((player_center[0] - self_center[0]), (player_center[1] - self_center[1]))
                        self.vx, self.vy = util.scale_vector(vector_to_player, self.MOVE_SPEED)

    def shoot_slimeball(self, target_pos):
        slimeball_entity = entity.Entity("slimeball", True)
        slimeball_entity.x, slimeball_entity.y = self.get_center()
        self.slimeballs.append([slimeball_entity, target_pos, -1])

    def get_hurtboxes(self):
        hurtboxes = []
        for slimeball in self.slimeballs:
            if slimeball[2] == 0:
                hurtboxes.append([slimeball[0].get_rect(), Interaction_Damage(1), Interaction_Slow(0.5)])
            elif slimeball[2] > 0:
                hurtboxes.append([slimeball[0].get_rect(), Interaction_Slow(0.5)])

        return hurtboxes


class Enemy_Lizard(Enemy):
    """
    Class for the lizard
    """

    ATTACK_RANGE = 100
    FOLLOW_RANGE = 250
    LUNGE_DISTANCE = 200

    def __init__(self, x, y):
        super(Enemy_Lizard, self).__init__("lizard", x, y, 1, 3)

        self.angle_direction = 1
        if random.randint(0, 1) == 0:
            self.angle_direction *= -1
        self.randomize_angle = False
        self.target_pos = None
        self.source_pos = None
        self.lunging = False

        self.LUNGE_SPEED = 10
        self.ATTACK_SPEED = 60
        self.next_attack_timer = 0
        self.NEXT_ATTACK_TIME = 2 * 60

    def do_ai(self, dt, player_rect):
        if self.lunging:
            self_center = self.get_center()
            distance_vector = (self.target_pos[0] - self_center[0], self.target_pos[1] - self_center[1])
            self.vx, self.vy = util.scale_vector(distance_vector, self.LUNGE_SPEED)
            if util.get_distance(self_center, self.target_pos) <= 20:
                self.target_pos = None
                self.source_pos = None
                self.lunging = False
                self.check_entity_collisions = True
                self.vx, self.vy = (0, 0)
        elif self.attacking:
            self.attack_timer += (dt * self.attack_speed_percent)
            if self.attack_timer >= self.ATTACK_SPEED:
                # self.start_lunge(util.get_center(player_rect))
                self.lunging = True
                self.check_entity_collisions = False
                self.attacking = False
        else:
            player_center = util.get_center(player_rect)
            self_center = self.get_center()
            player_distance = util.get_distance(self_center, player_center)
            if player_distance <= Enemy_Lizard.FOLLOW_RANGE:
                self.next_attack_timer += dt
                if player_distance <= Enemy_Lizard.ATTACK_RANGE:
                    self.vx, self.vy = (0, 0)
                    if self.next_attack_timer >= self.NEXT_ATTACK_TIME:
                        distance_vector = (player_center[0] - self_center[0], player_center[1] - self_center[1])
                        self.target_pos = util.sum_vectors(util.scale_vector(distance_vector, Enemy_Lizard.LUNGE_DISTANCE), self_center)
                        self.source_pos = self_center
                        self.attacking = True
                        self.attack_timer = 0
                        self.next_attack_timer = 0
                        self.NEXT_ATTACK_TIME = random.randint(3, 10) * 60
                else:
                    # Vectorize movement relative to player
                    vector_to_player = ((player_center[0] - self_center[0]), (player_center[1] - self_center[1]))
                    self.vx, self.vy = util.scale_vector(vector_to_player, self.MOVE_SPEED)

    def check_collision(self, dt, collider):
        collided = super(Enemy_Lizard, self).check_collision(dt, collider)
        if collided:
            self.lunging = False
            self.target_pos = None
            self.vx, self.vy = (0, 0)
            self.check_entity_collisions = True

    def get_hurtboxes(self):
        if self.lunging:
            return [(self.get_rect(), Interaction_Damage(1)), (self.get_rect(), Interaction_Impulse(self.source_pos, 2, 90))]
        else:
            return []


class Boss_Scorpion(Enemy):
    # State constants
    MOVE = 0
    CLAW = 1
    STING = 2
    ROLLY_POLLY = 3
    WEAK = 4

    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    def __init__(self, x, y):
        super(Boss_Scorpion, self).__init__("scorpion", x, y, 1, 25)
        self.is_boss = True

        self.state = Boss_Scorpion.MOVE
        self.timer = 0
        self.direction = Boss_Scorpion.DOWN
        self.target = None
        self.source_pos = None

        self.sting_number = random.randint(1, 3)
        # self.sting_number = 0
        self.sting_counter = 0

        self.CLAW_DURATION = 70
        self.CLAW_ONE_START = 10
        self.CLAW_TWO_START = 40
        self.CLAW_SWIPE_DURATION = 20
        self.CLAW_DAMAGE = 0.5

        self.STING_DURATION = 60 * 2
        self.STING_START = 20
        self.STING_SWIPE_DURATION = 20
        self.STING_DAMAGE = 1

        self.ROLLY_DAMAGE = 1
        self.ROLLY_SPEED = 4
        self.ROLLY_DELAY = 10

        self.WEAK_DURATION = 60 * 5

    def do_ai(self, dt, player_rect):
        if self.state == Boss_Scorpion.MOVE:
            met_target = False

            if self.target is not None:
                distance_vector = (self.target[0] - self.x, self.target[1] - self.y)
                if abs(distance_vector[0]) <= self.MOVE_SPEED * 2:
                    distance_vector = (0, distance_vector[1])
                if abs(distance_vector[1]) <= self.MOVE_SPEED * 2:
                    distance_vector = (distance_vector[0], 0)
                self.vx, self.vy = util.scale_vector(distance_vector, self.MOVE_SPEED)
                if (self.vx, self.vy) == (0, 0):
                    met_target = True
            else:
                self.vx, self.vy = (0, 0)

            if met_target:
                if self.sting_number != self.sting_counter:
                    self.timer = 0
                    self.state = Boss_Scorpion.CLAW
                    self.target = None
                    self.hurtboxes = []
                    if self.direction == Boss_Scorpion.DOWN:
                        self.hurtboxes.append((self.x, self.y + self.height, self.width // 2, 10))
                        self.hurtboxes.append((self.x + (self.width // 2), self.y + self.height, self.width // 2, 10))
                    elif self.direction == Boss_Scorpion.UP:
                        self.hurtboxes.append((self.x, self.y - 10, self.width // 2, 10))
                        self.hurtboxes.append((self.x + (self.width // 2), self.y - 10, self.width // 2, 10))
                    elif self.direction == Boss_Scorpion.RIGHT:
                        self.hurtboxes.append((self.x + self.width, self.y, 10, self.height // 2))
                        self.hurtboxes.append((self.x + self.width, self.y + (self.height // 2), 10, self.height // 2))
                    elif self.direction == Boss_Scorpion.LEFT:
                        self.hurtboxes.append((self.x - 10, self.y, 10, self.height // 2))
                        self.hurtboxes.append((self.x - 10, self.y + (self.height // 2), 10, self.height // 2))
                else:
                    self.timer = 0
                    self.state = Boss_Scorpion.STING
                    self.sting_counter = 0
                    self.sting_number = random.randint(1, 3)
                    self.target = None
                    self.hurtboxes = []
                    if self.direction == Boss_Scorpion.DOWN:
                        self.hurtboxes.append((self.x, self.y + self.height, self.width, 10))
                    elif self.direction == Boss_Scorpion.UP:
                        self.hurtboxes.append((self.x, self.y - 10, self.width, 10))
                    elif self.direction == Boss_Scorpion.RIGHT:
                        self.hurtboxes.append((self.x + self.width, self.y, 10, self.height))
                    elif self.direction == Boss_Scorpion.LEFT:
                        self.hurtboxes.append((self.x - 10, self.y, 10, self.height))
                self.sting_counter += 1
            else:
                player_center = util.get_center(player_rect)
                self_center = self.get_center()
                x_dist = player_center[0] - self_center[0]
                y_dist = player_center[1] - self_center[1]

                if abs(y_dist) >= abs(x_dist):
                    if y_dist > 0:
                        self.direction = Boss_Scorpion.DOWN
                        self.target = (player_center[0] - (self.width // 2), player_rect[1] - self.height)
                    else:
                        self.direction = Boss_Scorpion.UP
                        self.target = (player_center[0] - (self.width // 2), player_rect[1] + player_rect[3])
                else:
                    if x_dist > 0:
                        self.direction = Boss_Scorpion.RIGHT
                        self.target = (player_rect[0] - self.width, player_center[1] - (self.height // 2))
                    else:
                        self.direction = Boss_Scorpion.LEFT
                        self.target = (player_rect[0] + player_rect[2], player_center[1] - (self.height // 2))
        elif self.state == Boss_Scorpion.CLAW:
            self.timer += dt
            if self.timer >= self.CLAW_DURATION:
                self.timer = 0
                self.state = Boss_Scorpion.MOVE
        elif self.state == Boss_Scorpion.STING:
            self.timer += dt
            if self.timer >= self.STING_START and self.timer <= self.STING_START + self.STING_SWIPE_DURATION:
                if util.rects_collide(self.hurtboxes[0], player_rect):
                    self.timer = 0
                    self.source_pos = self.get_center()
                    self.state = Boss_Scorpion.MOVE
            if self.timer >= self.STING_DURATION:
                self.timer = 0
                self.state = Boss_Scorpion.ROLLY_POLLY
        elif self.state == Boss_Scorpion.ROLLY_POLLY:
            if self.timer < self.ROLLY_DELAY:
                self.timer += dt
                if self.timer >= self.ROLLY_DELAY:
                    self.source_pos = self.get_center()
                    if self.direction == Boss_Scorpion.DOWN:
                        self.vx, self.vy = (0, self.ROLLY_SPEED)
                    elif self.direction == Boss_Scorpion.UP:
                        self.vx, self.vy = (0, -self.ROLLY_SPEED)
                    elif self.direction == Boss_Scorpion.RIGHT:
                        self.vx, self.vy = (self.ROLLY_SPEED, 0)
                    elif self.direction == Boss_Scorpion.LEFT:
                        self.vx, self.vy = (-self.ROLLY_SPEED, 0)
                    self.check_entity_collisions = False
                    self.image = "scorpion-ball"
                    self.update_rect()
        elif self.state == Boss_Scorpion.WEAK:
            self.timer += dt
            if self.timer >= self.WEAK_DURATION:
                self.timer = 0
                self.state = Boss_Scorpion.MOVE

    def check_collision(self, dt, collider):
        collided = super(Boss_Scorpion, self).check_collision(dt, collider)
        if collided and self.state == Boss_Scorpion.ROLLY_POLLY:
            self.state = Boss_Scorpion.WEAK
            self.vx, self.vy = (0, 0)
            self.check_entity_collisions = True
            self.timer = 0
            self.image = "scorpion"
            self.update_rect()

            if self.direction == Boss_Scorpion.DOWN:
                self.y = collider[1] - self.height - 1
            elif self.direction == Boss_Scorpion.UP:
                self.y = collider[1] + collider[3] + 1
            elif self.direction == Boss_Scorpion.RIGHT:
                self.x = collider[0] - self.width - 1
            elif self.direction == Boss_Scorpion.LEFT:
                self.x = collider[0] + collider[2] + 1

    def get_hurtboxes(self):
        if self.state == Boss_Scorpion.CLAW:
            if self.timer >= self.CLAW_ONE_START and self.timer <= self.CLAW_ONE_START + self.CLAW_SWIPE_DURATION:
                return [(self.hurtboxes[0], Interaction_Damage(self.CLAW_DAMAGE)), (self.hurtboxes[0], Interaction_Impulse(util.get_center(self.hurtboxes[0])))]
            elif self.timer >= self.CLAW_TWO_START and self.timer <= self.CLAW_TWO_START + self.CLAW_SWIPE_DURATION:
                return [(self.hurtboxes[1], Interaction_Damage(self.CLAW_DAMAGE)), (self.hurtboxes[1], Interaction_Impulse(util.get_center(self.hurtboxes[1])))]
        elif self.state == Boss_Scorpion.STING:
            if self.timer >= self.STING_START and self.timer <= self.STING_START + self.STING_SWIPE_DURATION:
                return [(self.hurtboxes[0], Interaction_Damage(self.STING_DAMAGE)), (self.hurtboxes[0], Interaction_Impulse(util.get_center(self.hurtboxes[0])))]
        elif self.state == Boss_Scorpion.ROLLY_POLLY:
            return [(self.get_rect(), Interaction_Damage(self.ROLLY_DAMAGE)), (self.get_rect(), Interaction_Impulse(self.source_pos, 2, 90))]
        return []

    def add_interaction(self, interaction):
        if self.state != Boss_Scorpion.WEAK:
            return
        if isinstance(interaction, spells.Interaction_Plague):
            return
        super(Boss_Scorpion, self).add_interaction(interaction)
