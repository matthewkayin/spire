import pyglet


def center_image(image):
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2


pyglet.resource.path = ["./game/res"]
pyglet.resource.reindex()

player_idle_image = pyglet.resource.image("player-idle.png")
center_image(player_idle_image)
