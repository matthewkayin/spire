from . import resources, util


class Entity():
    """
    Class for game objects with movement
    """

    def __init__(self, image, has_alpha):
        image_object = resources.load_image(image, has_alpha)

        self.image = image
        self.rotation = None
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
        return int(round(self.x))

    def get_y(self):
        return int(round(self.y))

    def get_rect(self):
        return (self.x, self.y, self.width, self.height)

    def collides(self, other):
        return util.rects_collide(self.get_rect(), other)

    def get_image(self):
        if self.rotation is None:
            return resources.get_image(self.image)
        else:
            return resources.rotate(resources.get_image(self.image), self.rotation)
