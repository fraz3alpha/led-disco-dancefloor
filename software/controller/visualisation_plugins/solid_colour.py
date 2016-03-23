from VisualisationPlugin import VisualisationPlugin

import pygame
import colorsys
import math, cmath
import random

from DDRPi import FloorCanvas
from lib.controllers import ControllerInput
import logging
import urllib2
import json
import six # For string compatability between python 2.x and 3.x

class ColourPlugin(VisualisationPlugin):
    logger = logging.getLogger(__name__)

    __colours__ = {
        "RED": (0xFF, 0, 0),
        "GREEN": (0, 0xFF, 0),
        "BLUE": (0, 0, 0xFF),
        "BLACK": (0, 0, 0),
        "WHITE": (0xFF, 0xFF, 0xFF),
    }

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.logger.info("Initialising DDRPlugin")

        # Defaults
        self.colour = ColourPlugin.__colours__["RED"]

        self.config = None

    def configure(self, config):
        if config is not None:
            self.config = config

    """
    Called periodically to draw the dance floor surface
    """
    def draw_frame(self, canvas):

        canvas = self.draw_surface(canvas)
        # Limit the frame rate.
        # This sleeps so that at least 25ms has passed since tick()
        # was last called. It is a no-op if the loop is running slow
        self.clock.tick(25)
        # Draw whatever this plugin does
        return canvas

    def handle_event(self, event):
        pass

    def draw_splash(self, canvas):
        return self.draw_surface(canvas)

    def draw_surface(self, canvas):

        w = canvas.get_width()
        h = canvas.get_height()

        # Set the whole canvas to a the debug colour if we are debug mode
        for x in range(w):
            for y in range(h):
                canvas.set_pixel(x,y, self.colour)

        # Draw the starting positions
        return canvas
