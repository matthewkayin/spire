from . import entity, util, spells


class Enemy(entity.Entity):
    """
    Class for a basic enemy
    """

    def __init__(self, x, y):
        super(Enemy, self).__init__("mummy", True)
        self.x = x
        self.y = y

        self.FOLLOW_RANGE = 600
        self.MOVE_SPEED = 1

        """
        The attack windup occurs when the enemy is in melee range of the player (self.ATTACK_RANGE)
        The windup hurtbox is based on the player location when the attack begins. After timer goes off,
        if the player is still in the hurtbox, the player will be dealt self.POWER damage
        """
        self.attacking = False
        self.attack_timer = 0
        self.attack_speed_percent = 1
        self.ATTACK_SPEED = 20

        self.deal_damage = False
        self.hurtbox = None
        self.POWER = 1

        self.health = 3
        self.interactions = []

    def update(self, dt, player_rect):
        # If we finished an attack last turn, we want to reset these variables so the hit happens only once
        if self.deal_damage:
            self.hurtbox = None
            self.deal_damage = False

        # If we're in an attack windup...
        if self.attacking:
            self.attack_timer += (dt * self.attack_speed_percent)
            # If the attack windup has finished, set the variables needed for us to deal the player damage in the update loop
            if self.attack_timer >= self.ATTACK_SPEED:
                self.deal_damage = True
                self.attacking = False
        else:
            player_center = util.get_center(player_rect)
            self_center = util.get_center((self.x, self.y, self.width, self.height))
            player_distance = util.get_distance(self_center, player_center)
            if self.collides(player_rect):
                # begin an attack windup
                self.attacking = True
                self.hurtbox = player_rect
                self.attack_timer = 0
                self.vx, self.vy = (0, 0)
            elif player_distance <= self.FOLLOW_RANGE:
                # Vetorize movement relative to player
                vector_to_player = ((player_center[0] - self_center[0]), (player_center[1] - self_center[1]))
                self.vx, self.vy = util.scale_vector(vector_to_player, self.MOVE_SPEED)

        self.attack_speed_percent = 1  # Reset attack speed each update in case it was affected by a slow

        self.image_append = ""
        for interaction in self.interactions:
            interaction.update(dt, self)
        self.interactions = [interaction for interaction in self.interactions if not interaction.ended]

        super(Enemy, self).update(dt)

    def handle_spell_action(self, action, action_value):
        if action == spells.Spell.DAMAGE:
            self.health -= action_value
        elif action == spells.Spell.FREEZE:
            self.freeze_timer = action_value

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
