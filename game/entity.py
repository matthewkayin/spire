class Entity():
    """
    Class for game objects with movement
    """

    def __init__(self, image):
        self.image = image
        self.x = 0
        self.y = 0
        self.w = self.image.get_rect().width
        self.h = self.image.get_rect().height
        self.vx = 0
        self.vy = 0

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def get_x(self):
        return int(round(self.x))

    def get_y(self):
        return int(round(self.y))
