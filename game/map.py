from . import enemies


class Map():
    def __init__(self):
        self.current_rooms = []
        self.rooms = []
        self.rooms.append(Room(0, 0, "empty-one"))
        self.rooms.append(Room(0, -600, "empty-two"))
        self.rooms[0].enemies.append(enemies.Enemy(500, 10))
        self.current_room = 0
        self.previous_room = -1

    def update(self, player):
        self.current_rooms = []
        for i in range(0, len(self.rooms)):
            if player.collides(self.rooms[i].get_rect()):
                self.current_rooms.append(self.rooms[i])


class Room():
    def __init__(self, base_x, base_y, generator):
        self.colliders = []
        self.render_points = []
        self.entrances = []
        self.base_x = base_x
        self.base_y = base_y
        self.width = 12 * 50
        self.height = 12 * 50
        self.enemies = []

        if generator == "empty-one":
            self.create_empty_one()
        elif generator == "empty-two":
            self.create_empty_two()

        self.offset_coords(base_x, base_y)

    def get_rect(self):
        return (self.base_x, self.base_y, self.width, self.height)

    def create_empty_one(self):
        render_map = [[3, 4, 4, 4,14,-1,-1,12, 4, 4, 4, 5],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [15,16,16,16,16,16,16,16,16,16,16,17]]

        self.colliders.append((0, 0, 250, 50))
        self.colliders.append((350, 0, 250, 50))
        self.colliders.append((0, 550, 600, 50))
        self.colliders.append((0, 50, 50, 500))
        self.colliders.append((550, 50, 50, 500))

        for y in range(0, len(render_map)):
            for x in range(0, len(render_map[0])):
                if render_map[y][x] != -1:
                    self.render_points.append((("tileset", render_map[y][x]), x * 50, y * 50))
                else:
                    self.render_points.append(("floor", x * 50, y * 50))

    def create_empty_two(self):
        render_map = [[3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [9,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,11],
                      [15,16,16,16,2,-1,-1,0,16,16,16,17]]

        self.colliders.append((0, 0, 600, 50))
        self.colliders.append((0, 550, 250, 50))
        self.colliders.append((350, 550, 250, 50))
        self.colliders.append((0, 50, 50, 500))
        self.colliders.append((550, 50, 50, 500))

        for y in range(0, len(render_map)):
            for x in range(0, len(render_map[0])):
                if render_map[y][x] != -1:
                    self.render_points.append((("tileset", render_map[y][x]), x * 50, y * 50))
                else:
                    self.render_points.append(("floor", x * 50, y * 50))

    def offset_coords(self, base_x, base_y):
        self.base_x = base_x
        self.base_y = base_y
        for i in range(0, len(self.colliders)):
            self.colliders[i] = (self.colliders[i][0] + self.base_x, self.colliders[i][1] + self.base_y, self.colliders[i][2], self.colliders[i][3])
        for i in range(0, len(self.render_points)):
            self.render_points[i] = (self.render_points[i][0], self.render_points[i][1] + self.base_x, self.render_points[i][2] + self.base_y)
