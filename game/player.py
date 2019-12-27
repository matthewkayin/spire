from . import entity
import pygame.image


class Player(entity.Entity):
    """
    Player class
    """

    def __init__(self):
        super(Player, self).__init__(pygame.image.load("game/res/player-idle.png").convert_alpha())

        self.SPEED = 2

    def update(self, dt, input_queue, input_states):
        while len(input_queue) != 0:
            event = input_queue.pop()
            if event == ("player up", True):
                self.vy = -self.SPEED
            elif event == ("player down", True):
                self.vy = self.SPEED
            elif event == ("player right", True):
                self.vx = self.SPEED
            elif event == ("player left", True):
                self.vx = -self.SPEED
            elif event == ("player up", False):
                if input_states["player down"]:
                    self.vy = self.SPEED
                else:
                    self.vy = 0
            elif event == ("player down", False):
                if input_states["player up"]:
                    self.vy = -self.SPEED
                else:
                    self.vy = 0
            elif event == ("player right", False):
                if input_states["player left"]:
                    self.vx = -self.SPEED
                else:
                    self.vx = 0
            elif event == ("player left", False):
                if input_states["player right"]:
                    self.vx = self.SPEED
                else:
                    self.vx = 0

        super(Player, self).update(dt)
