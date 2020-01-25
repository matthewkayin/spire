from . import entity, util, spells


class Enemy(entity.Entity):
    """
    Class for a basic enemy
    """

    def __init__(self, image, x, y, move_speed, starting_health):
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
        self.interactions = []

    def update(self, dt, player_rect):
        self.do_ai(dt, player_rect)

        # reset attack speed each update so that when interactions fizzle out attack speed returns to normal
        self.attack_speed_percent = 1

        self.image_append = ""
        for interaction in self.interactions:
            interaction.update(dt, self)
        self.interactions = [interaction for interaction in self.interactions if not interaction.ended]

        super(Enemy, self).update(dt)

    def do_ai(self, dt, player_rect):
        """
        This is a to-be-implimented function for each enemy and it describes the specific AI behavior
        for the enemy. The function is then called during update
        """
        raise NotImplementedError("Need to impliment abstract function enemy.do_ai()")

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


class Enemy_Zombie(Enemy):
    """
    Class for the zombie
    """

    def __init__(self, x, y):
        super(Enemy_Zombie, self).__init__("mummy", x, y, 1, 3)
        self.x = x
        self.y = y

        self.FOLLOW_RANGE = 600

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
