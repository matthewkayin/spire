from . import enemies, util


class Map():
    def __init__(self):
        self.current_rooms = []
        self.rooms = []
        self.rooms.append(Room(0, 0, "empty-one"))
        self.rooms.append(Room(0, -600, "empty-two"))
        self.rooms[1].enemies.append(enemies.Enemy(500, 10))
        self.rooms[0].chests.append([(200, 200, 40, 25), False, (("spellbook-fire", 3), ("spellbook-golem", 3), ("potion", 2))])
        self.current_room = 0
        self.current_room = 0
        self.previous_room = -1

    def update(self, player):
        self.current_rooms = []
        for i in range(0, len(self.rooms)):
            if player.collides(self.rooms[i].get_rect()):
                self.current_rooms.append(self.rooms[i])

    def rect_in_map(self, rect):
        in_map = False
        for room in self.rooms:
            in_map = in_map or room.rect_in_room(rect)
            if in_map:
                break

        return in_map

    def rect_in_current_rooms(self, rect):
        in_map = False
        for room in self.current_rooms:
            in_map = in_map or room.rect_in_room(rect)
            if in_map:
                break

        return in_map


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
        self.items = []
        self.chests = []

        if generator == "empty-one":
            self.create_empty_one()
        elif generator == "empty-two":
            self.create_empty_two()

        self.offset_coords(base_x, base_y)

    def get_rect(self):
        return (self.base_x, self.base_y, self.width, self.height)

    def rect_in_room(self, rect):
        room_rect = self.get_rect()
        if rect[0] >= room_rect[0] and rect[0] + rect[2] < room_rect[0] + room_rect[2] and rect[1] >= room_rect[1] and rect[1] + rect[3] < room_rect[1] + room_rect[3]:
            for collider in self.colliders:
                if util.rects_collide(rect, collider):
                    return False
            return True
        else:
            return False

    def create_empty_one(self):
        render_map = [[3,13,13,13,14,-1,-1,12,13,13,13, 5],
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

        self.colliders.append((0, 0, 250, 25))
        self.colliders.append((350, 0, 250, 25))
        self.colliders.append((0, 565, 600, 35))
        self.colliders.append((0, 50, 50, 500))
        self.colliders.append((550, 50, 50, 500))

        for y in range(0, len(render_map)):
            for x in range(0, len(render_map[0])):
                if render_map[y][x] != -1:
                    self.render_points.append((("tileset", render_map[y][x]), x * 50, y * 50))
                else:
                    self.render_points.append(("floor", x * 50, y * 50))

    def create_empty_two(self):
        render_map = [[3,13,13,13,13,13,13,13,13,13,13, 5],
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

        self.colliders.append((0, 0, 600, 25))
        self.colliders.append((0, 565, 250, 35))
        self.colliders.append((350, 565, 250, 35))
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
