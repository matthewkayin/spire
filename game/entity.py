from . import resources, util


class Entity():
    """
    Class for game objects with movement
    """

    def __init__(self, image, has_alpha):
        image_object = resources.load_image(image, has_alpha)

        self.image = image
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
        image_obj = resources.get_image(self.image)
        self.width, self.height = image_obj.get_rect().width, image_obj.get_rect().height

    def get_rect(self):
        return (self.x, self.y, self.width, self.height)

    def get_center(self):
        return (self.x + self.width // 2, self.y + self.height // 2)

    def collides(self, other):
        return util.rects_collide(self.get_rect(), other)

    def get_image(self, alpha=255):
        image = None
        if alpha == 255:
            return resources.get_image(self.image)
        else:
            return resources.get_fade_image(self.image, alpha)
        if self.rotation is None:
            return image
        else:
            image, offset = resources.rotate(image, self.rotation)
            self.offset_x, self.offset_y = offset
            return image
        """
        if self.rotation is None:
            return resources.get_image(self.image)
        elif self.image == "bolt":
            image, offset = resources.create_lightning(self.length, self.rotation - 90)
            self.offset_x, self.offset_y = offset
            return image
        else:
            image, offset = resources.rotate(resources.get_image(self.image), self.rotation)
            self.offset_x, self.offset_y = offset
            return image
        """
