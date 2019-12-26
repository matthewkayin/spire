import pyglet
import math


class Entity(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        super(Entity, self).__init__(*args, **kwargs)

        self.vx = 0
        self.vy = 0

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def set_direction(self, dx, dy, speed):
        """
        Sets the entity velocity based on the given speed and (dx, dy) which should
        be a unit-vector equivalent of the desired direction of the entity.

        This function is to ensure the entity always moves as the desired speed in all
        angles (if dx=speed and dy=speed, the magnitude of their movement will be greater
        than the desired speed)
        """
        old_magnitude = math.sqrt((dx ** 2) + (dy ** 2))
        if old_magnitude == 0:
            self.vx = 0
            self.vy = 0
            return
        scale = speed / old_magnitude
        self.vx = dx * scale
        self.vy = dy * scale
