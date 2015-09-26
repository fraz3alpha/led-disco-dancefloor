from VisualisationPlugin import VisualisationPlugin

import pygame
import colorsys
import math

from DDRPi import FloorCanvas
import logging


class WavyBlobVisualisationPlugin(VisualisationPlugin):
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.logger.info("Initialising WavyBlobVisualisationPlugin")

    def configure(self, config):
        self.config = config
        self.logger.info("Config: %s" % config)

    def draw_frame(self, canvas):
        # Limit the frame rate.
        # This sleeps so that at least 25ms has passed since tick()
        # was last called. It is a no-op if the loop is running slow
        self.clock.tick(25)
        # Draw whatever this plugin does
        return self.draw_surface(canvas, pygame.time.get_ticks())

    def draw_splash(self, canvas):
        return self.draw_surface(canvas, 0)

    def draw_surface(self, canvas):
        return self.draw_surface(canvas, 0)

    def draw_surface(self, canvas, t):
        w = canvas.get_width()
        h = canvas.get_height()

        x_centre_pixel = w / 2.0
        y_centre_pixel = h / 2.0
        drop_off_distance = 5.0

        starting_colour_rgb = (255, 0, 0)
        # '*' unpacks a tuple, so that you can use all the values as consecutive arguments
        starting_colour_hsv = colorsys.rgb_to_hsv(*self.normalize(starting_colour_rgb))

        t_movement_period = 20000.0
        t_movement_adjustment = t * 2.0 * math.pi / t_movement_period
        movement_scale_x = w / 4.0
        movement_scale_y = h / 4.0

        # the centre moves in a figure of eight (infinity sign)
        x_this_centre_pixel = x_centre_pixel + movement_scale_x * math.sin(t_movement_adjustment)
        y_this_centre_pixel = y_centre_pixel + movement_scale_y * math.sin(2.0 * t_movement_adjustment)

        max_distance_away = math.sqrt(w * w + h * h) / 4.0

        for x in range(0, w):
            for y in range(0, h):

                hsv_colour = []
                for i in range(0, 3):
                    hsv_colour.append(0x00)
                hsv_colour[1] = starting_colour_hsv[1]
                hsv_colour[2] = starting_colour_hsv[2]

                x_delta = math.fabs(x - x_this_centre_pixel)
                y_delta = math.fabs(y - y_this_centre_pixel)

                distance_away = math.sqrt(x_delta * x_delta + y_delta * y_delta)

                t_period = 4000.0
                t_adjustment = t * 2.0 * math.pi / t_period
                multiplier = (math.sin(t_adjustment) + 1.0) / 2.0

                # We vary only the hue between 0.0 (red) and 1/3 (green)
                hsv_colour[0] = 0.33 * ((math.sin(distance_away / 3.0 - t_adjustment) + 1.0) / 2.0)

                rgb_colour = self.reformat(colorsys.hsv_to_rgb(*hsv_colour))
                canvas.set_pixel_tuple(x, y, rgb_colour)

        return canvas

    # Example, and following two functions taken from http://www.pygame.org/wiki/RGBColorConversion

    # Normalization method, so the colors are in the range [0, 1]
    def normalize(self, color):
        return color[0] / 255.0, color[1] / 255.0, color[2] / 255.0

    # Reformats a color tuple, that uses the range [0, 1] to a 0xFF
    # representation.
    def reformat(self, color):
        return int(round(color[0] * 255)), \
               int(round(color[1] * 255)), \
               int(round(color[2] * 255))

