import sys

import pyglet

# game constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
TARGET_FPS = 60

# handle any cli flags
debug_mode = "--debug" in sys.argv
INDEV_BUILD = True


# init pyglet
window = pyglet.window.Window(SCREEN_WIDTH, SCREEN_HEIGHT, fullscreen=False)
main_batch = pyglet.graphics.Batch()

# create the upper-left corner fps counter
fps_counter = pyglet.window.FPSDisplay(window=window)
fps_counter.label.font_name = "Serif"
fps_counter.label.font_size = 12
fps_counter.label.color = (255, 255, 0, 255)
fps_counter.label.x = 0
fps_counter.label.y = SCREEN_HEIGHT - 12


def init_graphics():
    # give user a resolution that matches their monitor's aspect ratio
    screen = pyglet.canvas.get_display().get_default_screen()
    aspect_ratio = screen.width / screen.height
    print("Screen width and height: " + str(screen.width) + "x" + str(screen.height))
    if aspect_ratio == 16.0 / 10.0:
        print("Detected 16:10 aspect ratio. Setting resolution to 640x400.")
        SCREEN_WIDTH = 640
        SCREEN_HEIGHT = 400
    elif aspect_ratio == 16.0 / 9.0:
        print("Detected 16:9 aspect ratio. Setting resolution to 640x360.")
        SCREEN_WIDTH = 640
        SCREEN_HEIGHT = 360
    elif aspect_ratio == 4.0 / 3.0:
        print("Detected 4:3 aspect ratio. Setting resolution to 640x480.")
        SCREEN_WIDTH = 640
        SCREEN_HEIGHT = 480

    if debug_mode:
        window.set_size(SCREEN_WIDTH, SCREEN_HEIGHT)
    else:
        window.set_fullscreen(fullscreen=True, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)


@window.event
def on_draw():
    window.clear()
    main_batch.draw()
    if debug_mode:
        fps_counter.draw()


if __name__ == "__main__":
    init_graphics()
    # pyglet.clock.schedule_
    pyglet.app.run()
