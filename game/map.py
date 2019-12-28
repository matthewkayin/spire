class Map():
    def __init__(self):
        self.room = Room(0, 0, "empty", [])


class Room():
    def __init__(self, base_x, base_y, generator, exits):
        self.colliders = []
        self.render_points = []
        self.base_x = base_x
        self.base_y = base_y

        if generator == "empty":
            self.generate_empty(exits)
        elif generator == "two-pillars":
            self.generate_two_pillars(exits)

        self.offset_coords(base_x, base_y)

    def create_top_wall(self, with_exit):
        if with_exit:
            self.colliders.append((0, 0, 5 * 50, 50))
            self.colliders.append((7 * 50, 0, 5 * 50, 0))
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
            self.colliders.append((7 * 50, 11 * 50, 5 * 50, 0))
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
        for collider in self.colliders:
            collider = (collider[0] + self.base_x, collider[1] + self.base_y, collider[2], collider[3])
        for render_point in self.render_points:
            render_point = (render_point[0], render_point[1] + self.base_x, render_point[2] + self.base_y)

    def generate_empty(self, exits):
        self.create_walls(exits)
        self.fill_floors()
