from . import entity, resources, util


class Player(entity.Entity):
    """
    Player class
    """

    def __init__(self, DISPLAY_WIDTH, DISPLAY_HEIGHT):
        super(Player, self).__init__("player-idle", True)

        resources.load_image("heart", True)

        self.SCREEN_CENTER_X = DISPLAY_WIDTH // 2
        self.SCREEN_CENTER_Y = DISPLAY_HEIGHT // 2
        self.CAMERA_OFFSET_X = (self.width // 2) - self.SCREEN_CENTER_X
        self.CAMERA_OFFSET_Y = (self.height // 2) - self.SCREEN_CENTER_Y
        self.camera_x = 0
        self.camera_y = 0
        self.CAMERA_SENSITIVITY = 0.2

        self.dx = 0
        self.dy = 0
        self.SPEED = 2

        self.health = 3

    def update(self, dt, input_queue, input_states, mouse_x, mouse_y):
        update_velocity = False

        # Handle input
        while len(input_queue) != 0:
            event = input_queue.pop()
            if event == ("player up", True):
                self.dy = -1
                update_velocity = True
            elif event == ("player down", True):
                self.dy = 1
                update_velocity = True
            elif event == ("player right", True):
                self.dx = 1
                update_velocity = True
            elif event == ("player left", True):
                self.dx = -1
                update_velocity = True
            elif event == ("player up", False):
                if input_states["player down"]:
                    self.dy = 1
                else:
                    self.dy = 0
                update_velocity = True
            elif event == ("player down", False):
                if input_states["player up"]:
                    self.dy = -1
                else:
                    self.dy = 0
                update_velocity = True
            elif event == ("player right", False):
                if input_states["player left"]:
                    self.dx = -1
                else:
                    self.dx = 0
                update_velocity = True
            elif event == ("player left", False):
                if input_states["player right"]:
                    self.dx = 1
                else:
                    self.dx = 0
                update_velocity = True

        # If update velocity is true, that means we changed the direction vector so we should update the velocity to match it
        if update_velocity:
            # player vx/vy is direction (dx/dy) scaled up to SPEED
            self.vx, self.vy = util.scale_vector((self.dx, self.dy), self.SPEED)

        super(Player, self).update(dt)

    def update_camera(self, mouse_x, mouse_y):
        """
        Sets the camera position based on the player position and offset with the mouse relative to the screen center
        """
        self.camera_x = self.x + self.CAMERA_OFFSET_X + ((mouse_x - self.SCREEN_CENTER_X) * self.CAMERA_SENSITIVITY)
        self.camera_y = self.y + self.CAMERA_OFFSET_Y + ((mouse_y - self.SCREEN_CENTER_Y) * self.CAMERA_SENSITIVITY)

    def check_collision(self, dt, collider):
        """
        This checks for a collision with a wall-like object and handles it if necessary
        """
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

    def get_heart_image(self):
        return resources.get_image("heart")
