from . import resources, util


class Entity():
    """
    Class for game objects with movement
    """

    def __init__(self, image, has_alpha):
        image_object = resources.get_image(image, has_alpha)

        self.image = image
        self.image_append = ""
        self.has_alpha = has_alpha
        self.rotation = None
        self.offset_x = 0
        self.offset_y = 0
        self.x = 0
        self.y = 0
        self.width = image_object.get_rect().width
        self.height = image_object.get_rect().height
        self.vx = 0
        self.vy = 0

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def get_x(self):
        return int(round(self.x)) + self.offset_x

    def get_y(self):
        return int(round(self.y)) + self.offset_y

    def update_rect(self):
        image_obj = resources.get_image(self.image, self.has_alpha)
        self.width, self.height = image_obj.get_rect().width, image_obj.get_rect().height

    def get_rect(self):
        return (self.x, self.y, self.width, self.height)

    def get_center(self):
        return (self.x + self.width // 2, self.y + self.height // 2)

    def collides(self, other):
        return util.rects_collide(self.get_rect(), other)

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
            if not y_caused_collision:
                self.y += y_step

    def get_image(self, alpha=255):
        image = None
        if alpha == 255:
            image = resources.get_image(self.image + self.image_append, self.has_alpha)
        else:
            image = resources.get_image(self.image + self.image_append, self.has_alpha, alpha)
        if self.rotation is None:
            return image
        else:
            image, offset = resources.rotate(image, self.rotation)
            self.offset_x, self.offset_y = offset
            return image
