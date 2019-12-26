from pyglet.window import key
from . import entity, resources


class Player(entity.Entity):
    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(img=resources.player_idle_image, *args, **kwargs)

        # movement variables
        self.old_dx = 0
        self.old_dy = 0
        self.dx = 0
        self.dy = 0
        self.SPEED = 3 * 60

        # event handler variables
        self.key_handler = key.KeyStateHandler()
        self.event_handlers = [self, self.key_handler]

    def on_key_press(self, symbol, modifiers):
        if symbol == key.W:
            self.dy = 1
        elif symbol == key.S:
            self.dy = -1
        elif symbol == key.D:
            self.dx = 1
        elif symbol == key.A:
            self.dx = -1

    def on_key_release(self, symbol, modifiers):
        """
        For each of the movement key releases, we want to check if the opposite key is being
        pressed and if it is, continue moving in that direction, otherwise just stop moving
        """
        if symbol == key.W:
            if self.key_handler[key.S]:
                self.dy = -1
            else:
                self.dy = 0
        elif symbol == key.S:
            if self.key_handler[key.W]:
                self.dy = 1
            else:
                self.dy = 0
        elif symbol == key.D:
            if self.key_handler[key.A]:
                self.dx = -1
            else:
                self.dx = 0
        elif symbol == key.A:
            if self.key_handler[key.D]:
                self.dx = 1
            else:
                self.dx = 0

    def update(self, dt):
        # if direction x/y have changed, update vx/vy accordingly
        if self.dx != self.old_dx or self.dy != self.old_dy:
            self.set_direction(self.dx, self.dy, self.SPEED)
        self.old_dx = self.dx
        self.old_dy = self.dy

        super(Player, self).update(dt)
