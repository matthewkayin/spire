from . import enemies, util, resources


class Map():
    def __init__(self):
        self.current_rooms = []
        self.rooms = []
        self.rooms.append(Room(0, 0, 14, 14, []))
        self.rooms[0].enemies.append(enemies.Boss_Scorpion(70, 70))
        self.rooms[0].enemies.append(enemies.Enemy_Zombie(200, 200))
        # self.rooms[0].chests.append([(200, 200, 40, 25), False, (("spellbook-fire", 3), ("spellbook-golem", 3), ("potion", 2))])
        self.current_room = 0
        self.current_room = 0
        self.previous_room = -1

        self.player_spawn = (self.rooms[0].width // 2, self.rooms[0].height * 0.75)

        resources.load_tileset("tileset")

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
    DOOR_TOP = 0
    DOOR_RIGHT = 1
    DOOR_BOT = 2
    DOOR_LEFT = 3

    def __init__(self, base_x, base_y, width, height, doors=[]):
        self.colliders = []
        self.render_points = []
        self.entrances = []
        self.base_x = base_x
        self.base_y = base_y
        self.width = 0
        self.height = 0
        self.enemies = []
        self.items = []
        self.chests = []

        self.generate_room(width, height, doors)

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

    def generate_room(self, width, height, doors):
        self.width = width * 50
        self.height = height * 50

        render_map = []
        for row in range(0, height):
            new_row = []
            for column in range(0, width):
                if row == 0:
                    if column == 0:
                        new_row.append(3)
                    elif column == width - 1:
                        new_row.append(5)
                    else:
                        new_row.append(13)
                elif row == height - 1:
                    if column == 0:
                        new_row.append(15)
                    elif column == width - 1:
                        new_row.append(17)
                    else:
                        new_row.append(16)
                else:
                    if column == 0:
                        new_row.append(9)
                    elif column == width - 1:
                        new_row.append(11)
                    else:
                        new_row.append(-1)
            render_map.append(new_row)

        if Room.DOOR_TOP in doors:
            door_index = (width // 2) - 1
            render_map[0][door_index - 1] = 14
            render_map[0][door_index] = -1
            render_map[0][door_index + 1] = -1
            render_map[0][door_index + 2] = 12

            self.colliders.append((0, 0, door_index * 50, 25))
            self.colliders.append(((door_index * 50) + 100, 0, self.width - ((door_index * 50) + 100), 25))
        else:
            self.colliders.append((0, 0, self.width, 25))

        if Room.DOOR_BOT in doors:
            door_index = (width // 2) - 1
            render_map[height - 1][door_index - 1] = 2
            render_map[height - 1][door_index] = -1
            render_map[height - 1][door_index + 1] = -1
            render_map[height - 1][door_index + 2] = 0

            self.colliders.append((0, self.height - 50, door_index * 50, 35))
            self.colliders.append(((door_index * 50) + 100, self.height - 50, self.width - ((door_index * 50) + 100), 35))
        else:
            self.colliders.append((0, self.height - 50, self.width, 35))

        if Room.DOOR_LEFT in doors:
            door_index = (height // 2) - 1
            render_map[door_index - 1][0] = 18
            render_map[door_index][0] = -1
            render_map[door_index + 1][0] = -1
            render_map[door_index + 2][0] = 2

            self.colliders.append((0, 50, 50, (door_index - 1) * 50))
            self.colliders.append((0, (door_index + 2) * 50, 50, self.height - 200 - ((door_index - 1) * 50)))
        else:
            self.colliders.append((0, 50, 50, (height - 2) * 50))

        if Room.DOOR_RIGHT in doors:
            door_index = (height // 2) - 1
            render_map[door_index - 1][width - 1] = 20
            render_map[door_index][width - 1] = -1
            render_map[door_index + 1][width - 1] = -1
            render_map[door_index + 2][width - 1] = 0

            self.colliders.append((self.width - 50, 50, 50, (door_index - 1) * 50))
            self.colliders.append((self.width - 50, (door_index + 2) * 50, 50, self.height - 200 - ((door_index - 1) * 50)))
        else:
            self.colliders.append((self.width - 50, 50, 50, (height - 2) * 50))

        for row in range(0, len(render_map)):
            for column in range(0, len(render_map[0])):
                if render_map[row][column] != -1:
                    self.render_points.append((("tileset", render_map[row][column]), column * 50, row * 50))
                else:
                    self.render_points.append(("floor", column * 50, row * 50))

    def offset_coords(self, base_x, base_y):
        self.base_x = base_x
        self.base_y = base_y
        for i in range(0, len(self.colliders)):
            self.colliders[i] = (self.colliders[i][0] + self.base_x, self.colliders[i][1] + self.base_y, self.colliders[i][2], self.colliders[i][3])
        for i in range(0, len(self.render_points)):
            self.render_points[i] = (self.render_points[i][0], self.render_points[i][1] + self.base_x, self.render_points[i][2] + self.base_y)
