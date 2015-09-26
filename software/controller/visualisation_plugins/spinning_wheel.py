from VisualisationPlugin import VisualisationPlugin

import pygame
import colorsys
import math, cmath

from DDRPi import FloorCanvas
from lib.controllers import ControllerInput
import logging


class SpinningWheelVisualisationPlugin(VisualisationPlugin):
    logger = logging.getLogger(__name__)
    VALID_MODES = ["CENTER", "EDGE_ROTATE"]
    VALID_COLOURS = ["FULL_COLOUR", "BLACK_AND_WHITE"]

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.logger.info("Initialising SpinningWheelVisualisationPlugin")

        # Defaults
        self.speed = 30.0
        self.edge_rotate_speed = 1.0
        self.colours = "FULL_COLOUR"
        self.mode = "CENTER"


    def configure(self, config):
        self.config = config
        self.logger.info("Config: %s" % config)

        if self.config != None:
            try:
                self.speed = float(self.config["speed"])
            except (AttributeError, ValueError, KeyError):
                pass

            try:
                self.edge_rotate_speed = float(self.config["edge_rotate_speed"])
            except (AttributeError, ValueError, KeyError):
                pass

            try:
                if self.config["colours"].upper() in SpinningWheelVisualisationPlugin.VALID_COLOURS:
                    self.colours = self.config["colours"].upper()
            except (AttributeError, KeyError):
                pass

            try:
                if self.config["mode"].upper() in SpinningWheelVisualisationPlugin.VALID_MODES:
                    self.mode = self.config["mode"].upper()
            except (AttributeError, KeyError):
                pass

    def draw_frame(self, canvas):

        canvas = self.draw_surface(canvas, pygame.time.get_ticks())
        # Limit the frame rate.
        # This sleeps so that at least 25ms has passed since tick()
        # was last called. It is a no-op if the loop is running slow
        self.clock.tick(25)
        # Draw whatever this plugin does
        return canvas

    def handle_event(self, event):

        try:
            event_name_temp = pygame.event.event_name(event.type)

            if event_name_temp == "JoyButtonDown":
                # button = self.__buttons__[event.button]
                button = event.button
                if button is not None:
                    if button == ControllerInput.BUTTON_A:
                        self.mode = "CENTER"
                    elif button == ControllerInput.BUTTON_B:
                        self.mode = "EDGE_ROTATE"
                    if button == ControllerInput.BUTTON_X:
                        self.colours = "BLACK_AND_WHITE"
                    elif button == ControllerInput.BUTTON_Y:
                        self.colours = "FULL_COLOUR"
                    else:
                        print ("Unhandled button event: %s" % button)

        except Exception as ex:
            print (ex)
            self.logger.error("SpinningWheelVisualisationPlugin: %s" % ex)


    def draw_splash(self, canvas):
        return self.draw_surface(canvas, 0)

    def draw_surface(self, canvas):
        return self.draw_surface(canvas, 0)

    def draw_surface(self, canvas, t):
        w = canvas.get_width()
        h = canvas.get_height()

        x_centre_pixel = (w - 1) / 2.0
        y_centre_pixel = (h - 1) / 2.0

        # The hue varies by angle, with a constant offset - the speed
        # that it rotates

        offset = 0.0

        if self.mode == "EDGE_ROTATE":
            radius = math.sqrt((w / 2) ** 2 + (h / 2) ** 2)

            edge_rotate_angle = self.edge_rotate_speed * t / (1000.0 * 2.0 * math.pi)

            x_centre_pixel = (w - 1) / 2.0 + radius * math.cos(edge_rotate_angle)
            y_centre_pixel = (h - 1) / 2.0 + radius * math.sin(edge_rotate_angle)

        for x in range(w):
            for y in range(h):

                x_diff = x - x_centre_pixel
                y_diff = y - y_centre_pixel

                # Get angle in the range [0,2pi]
                angle = cmath.phase(complex(-x_diff, y_diff)) + math.pi

                # Add a bit according to the phase
                angle += self.speed * t / (1000.0 * 2.0 * math.pi)

                # Get it back in the range [0,2pi]
                (angle_div, angle_mod) = divmod(angle, 2.0 * math.pi)

                # Default, full colour
                hue = angle_mod / (2.0 * math.pi)
                saturation = 1.0
                value = 1.0
                if self.colours == "BLACK_AND_WHITE":
                    hue = 0.0
                    saturation = 0.0
                    value = angle_mod / (1.0 * math.pi)

                rgb_colour = self.reformat(colorsys.hsv_to_rgb(*(hue, saturation, value)))
                canvas.set_pixel_tuple(x, y, rgb_colour)
        #exit(1)
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

