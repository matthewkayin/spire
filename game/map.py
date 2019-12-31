from . import enemies


class Map():
    def __init__(self):
        self.current_rooms = []
        self.rooms = []
        self.rooms.append(Room(0, 0, "empty", [0]))
        self.rooms.append(Room(0, -600, "empty", [2]))
        self.rooms[0].enemies.append(enemies.Enemy(500, 10))
        self.current_room = 0
        self.previous_room = -1

    def update(self, player):
        self.current_rooms = []
        for i in range(0, len(self.rooms)):
            if player.collides(self.rooms[i].get_rect()):
                self.current_rooms.append(self.rooms[i])


class Room():
    def __init__(self, base_x, base_y, generator, exits):
        self.colliders = []
        self.render_points = []
        self.entrances = []
        self.base_x = base_x
        self.base_y = base_y
        self.width = 12 * 50
        self.height = 12 * 50
        self.enemies = []

        if generator == "empty":
            self.generate_empty(exits)
        elif generator == "two-pillars":
            self.generate_two_pillars(exits)

        self.offset_coords(base_x, base_y)

    def get_rect(self):
        return (self.base_x, self.base_y, self.width, self.height)

    def create_top_wall(self, with_exit):
        if with_exit:
            self.colliders.append((0, 0, 5 * 50, 50))
            self.colliders.append((7 * 50, 0, 5 * 50, 50))
            for i in range(0, 5):
                self.render_points.append(("wall", 0 + (i * 50), 0))
                self.render_points.append(("wall", (7 * 50) + (i * 50), 0))
        else:
            self.colliders.append((0, 0, 12 * 50, 50))
            for i in range(0, 12):
                self.render_points.append(("wall", 0 + (i * 50), 0))

    def create_bot_wall(self, with_exit):
        if with_exit:
            self.colliders.append((0, 11 * 50, 5 * 50, 50))
            self.colliders.append((7 * 50, 11 * 50, 5 * 50, 50))
            for i in range(0, 5):
                self.render_points.append(("wall", 0 + (i * 50), 11 * 50))
                self.render_points.append(("wall", (7 * 50) + (i * 50), 11 * 50))
        else:
            self.colliders.append((0, 11 * 50, 12 * 50, 50))
            for i in range(0, 12):
                self.render_points.append(("wall", 0 + (i * 50), 11 * 50))

    def create_left_wall(self, with_exit):
        if with_exit:
            self.colliders.append((0, 50, 50, 4 * 50))
            self.colliders.append((0, 7 * 50, 50, 4 * 50))
            for i in range(0, 4):
                self.render_points.append(("wall-side", 0, 50 + (i * 50)))
                self.render_points.append(("wall-side", 0, (7 * 50) + (i * 50)))
        else:
            self.colliders.append((0, 50, 50, 10 * 50))
            for i in range(0, 10):
                self.render_points.append(("wall-side", 0, 50 + (i * 50)))

    def create_right_wall(self, with_exit):
        if with_exit:
            self.colliders.append((11 * 50, 50, 50, 4 * 50))
            self.colliders.append((11 * 50, 7 * 50, 50, 4 * 50))
            for i in range(0, 4):
                self.render_points.append(("wall", 11 * 50, 50 + (i * 50)))
                self.render_points.append(("wall", 11 * 50, (7 * 50) + (i * 50)))
        else:
            self.colliders.append((11 * 50, 50, 50, 10 * 50))
            for i in range(0, 10):
                self.render_points.append(("wall", 11 * 50, 50 + (i * 50)))

    def create_walls(self, exits):
        self.create_top_wall(0 in exits)
        self.create_right_wall(1 in exits)
        self.create_bot_wall(2 in exits)
        self.create_left_wall(3 in exits)

    def fill_floors(self):
        for x in range(0, 12):
            for y in range(0, 12):
                tile_x = x * 50
                tile_y = y * 50
                add_tile = True
                for render_point in self.render_points:
                    if tile_x == render_point[1] and tile_y == render_point[2]:
                        add_tile = False
                        break
                if add_tile:
                    self.render_points.append(("floor", tile_x, tile_y))

    def offset_coords(self, base_x, base_y):
        self.base_x = base_x
        self.base_y = base_y
        for i in range(0, len(self.colliders)):
            self.colliders[i] = (self.colliders[i][0] + self.base_x, self.colliders[i][1] + self.base_y, self.colliders[i][2], self.colliders[i][3])
        for i in range(0, len(self.render_points)):
            self.render_points[i] = (self.render_points[i][0], self.render_points[i][1] + self.base_x, self.render_points[i][2] + self.base_y)

    def generate_empty(self, exits):
        self.create_walls(exits)
        self.fill_floors()
