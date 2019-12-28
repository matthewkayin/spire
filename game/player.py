from . import entity


class Player(entity.Entity):
    """
    Player class
    """

    def __init__(self):
        super(Player, self).__init__("player-idle", True)

        self.camera_x = 0
        self.camera_y = 0
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

        self.camera_x += self.vx * dt
        self.camera_y += self.vy * dt
        super(Player, self).update(dt)

    def check_collision(self, dt, collider):
        if self.collides(collider):
            x_step = self.vx * dt
            y_step = self.vy * dt

            # Since there was a collision, rollback our previous movement
            self.x -= x_step
            self.y -= y_step
            self.camera_x -= x_step
            self.camera_y -= y_step

            # Check to see if that collision happened due to x movement
            self.x += x_step
            x_caused_collision = self.collides(collider)
            self.x -= x_step

            # Check to see if that collision happened due to y movement
            self.y += y_step
            y_caused_collision = self.collides(collider)
            self.y -= y_step

            # If x/y didn't cause collision, we can move in x/y direction
            if not x_caused_collision:
                self.x += x_step
                self.camera_x += x_step
            if not y_caused_collision:
                self.y += y_step
                self.camera_y += y_step

    def get_camera_x(self):
        return int(round(self.camera_x))

    def get_camera_y(self):
        return int(round(self.camera_y))
