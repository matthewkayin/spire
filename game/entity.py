from . import resources


class Entity():
    """
    Class for game objects with movement
    """

    def __init__(self, image, has_alpha):
        image_object = resources.load_image(image, has_alpha)

        self.image = image
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
        center_x = self.x + (self.width // 2)
        other_center_x = other[0] + (other[2] // 2)
        center_y = self.y + (self.height // 2)
        other_center_y = other[1] + (other[3] // 2)
        return abs(center_x - other_center_x) * 2 < other[2] + self.width and abs(center_y - other_center_y) * 2 < other[3] + self.height

    def get_image(self):
        return resources.get_image(self.image)
