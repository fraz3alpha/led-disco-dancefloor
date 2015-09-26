from VisualisationPlugin import VisualisationPlugin

import pygame
# For colour conversion functions
from colorsys import hls_to_rgb

from DDRPi import FloorCanvas


class HlsTestVisualisationPlugin(VisualisationPlugin):
    def __init__(self):
        self.clock = pygame.time.Clock()

    def draw_frame(self, surface):

        # Limit the frame rate.
        # This sleeps so that at least 25ms has passed since tick()
        # was last called. It is a no-op if the loop is running slow
        self.clock.tick(25)
        # Draw whatever this plugin does.
        # We need to return our decorated surface
        return self.draw_surface(surface, pygame.time.get_ticks())

    def draw_splash(self, canvas):
        return self.draw_surface(canvas, 0)

    def draw_surface(self, canvas):
        return self.draw_surface(0)

    def draw_surface(self, canvas, ticks):
        canvas.set_colour(FloorCanvas.WHITE)

        for x in range(0, canvas.get_width()):
            for y in range(0, canvas.get_height()):
                h = float(x) / canvas.get_width()
                # A saturation of 1.0 gives pure colour
                # 0 = grey
                s = 1.0
                # a lightness of 0.5 gives pure colour,
                #  0 = black, 1 = white
                l = float(y) / canvas.get_height()

                # Convert the hls colourspace to RGB so we
                #  can assign it to a pixel
                rgb = hls_to_rgb(h, l, s)
                canvas.set_float_pixel_tuple(x, y, rgb)


        # Return the canvas
        return canvas



