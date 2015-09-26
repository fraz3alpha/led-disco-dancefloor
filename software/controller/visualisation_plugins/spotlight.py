from VisualisationPlugin import VisualisationPlugin

import pygame
import logging
import math

from DDRPi import FloorCanvas
from lib.controllers import ControllerInput


class SpotlightVisualisationPlugin(VisualisationPlugin):
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.clock = pygame.time.Clock()

        self.spot = dict()
        self.spot["position"] = None
        self.spot["radius"] = 5.0
        self.spot["brightness"] = 10

    # Nothing specific to be done before this starts, although we could
    # set self.clock here. Stash any config so we can use it later
    def configure(self, config):
        self.config = config
        self.logger.info("Config: %s" % config)

        self.spots = dict()


    # This will just keep running, nothing specific to do for start(), stop(),
    #  pause() or resume()
    def start(self):
        pass

    def stop(self):
        pass

    def pause(self):
        pass

    def resume(self):
        pass

    def handle_event(self, event):
        try:

            if (pygame.event.event_name(event.type) == "JoyButtonDown"):
                # Create a new spot if the user doesn't already have one
                if (event.button == ControllerInput.BUTTON_A):
                    if event.joy not in self.spots:
                        self.spots[event.joy] = self.new_spot()
                # Remove the current spot if the user presses B
                if (event.button == ControllerInput.BUTTON_B):
                    if event.joy in self.spots:
                        del self.spots[event.joy]
                # Decrease the radius of this spot if there is one
                if (event.button == ControllerInput.BUMPER_LEFT):
                    if event.joy in self.spots:
                        if self.spots[event.joy]["radius"] > 1:
                            self.spots[event.joy]["radius"] -= 1
                # Increase the radius of this spot if there is one
                if (event.button == ControllerInput.BUMPER_RIGHT):
                    if event.joy in self.spots:
                        if self.spots[event.joy]["radius"] < 20:
                            self.spots[event.joy]["radius"] += 1
                # Decrease the brightness of this spot if there is one
                if (event.button == ControllerInput.BUTTON_Y):
                    if event.joy in self.spots:
                        if self.spots[event.joy]["brightness"] > 0:
                            self.spots[event.joy]["brightness"] -= 1
                # Increase the brightness of this spot if there is one
                if event.button == ControllerInput.BUTTON_X:
                    if event.joy in self.spots:
                        if self.spots[event.joy]["brightness"] < 10:
                            self.spots[event.joy]["brightness"] += 1


            elif (pygame.event.event_name(event.type) == "JoyAxisMotion"):
                if event.joy in self.spots:
                    if event.axis == 1:
                        # The axis is upside down, -1 = up
                        if event.value < -0.5:
                            (x, y) = self.spots[event.joy]["position"]
                            self.spots[event.joy]["position"] = (x, y - 1)
                        elif event.value > 0.5:
                            (x, y) = self.spots[event.joy]["position"]
                            self.spots[event.joy]["position"] = (x, y + 1)
                    if event.axis == 0:
                        # Left and Right, generated new colours
                        if event.value < -0.5:
                            (x, y) = self.spots[event.joy]["position"]
                            self.spots[event.joy]["position"] = (x - 1, y)
                        elif event.value > 0.5:
                            (x, y) = self.spots[event.joy]["position"]
                            self.spots[event.joy]["position"] = (x + 1, y)

        except Exception as e:
            print(e)

        return None

    def new_spot(self):

        spot = dict()
        spot["radius"] = 5.0
        spot["position"] = (0, 0)
        spot["colour"] = FloorCanvas.WHITE
        spot["brightness"] = 10

        return spot

    def draw_frame(self, surface):

        # Limit the frame rate.
        # This sleeps so that at least 25ms has passed since tick()
        #  was last called. It is a no-op if the loop is running slow
        self.clock.tick(25)
        # Draw whatever this plugin does.
        # We need to return our decorated surface
        return self.draw_surface(surface, pygame.time.get_ticks())

    def draw_splash(self, canvas):

        canvas.set_colour(FloorCanvas.BLACK)

        w = canvas.get_width()
        h = canvas.get_height()

        canvas.draw_circle((w - 1) / 2.0, (h - 1) / 2.0, 8.0, FloorCanvas.WHITE, FloorCanvas.WHITE)

        return canvas

    # We've split the method that does the drawing out, so that draw_splash()
    #  can call it with a fixed timer
    def draw_surface(self, canvas, ticks):

        canvas.set_colour(FloorCanvas.BLACK)

        w = canvas.get_width()
        h = canvas.get_height()


        # If we have some spots, then draw them on the canvas, else
        #  draw a pulsating circle
        if len(self.spots) > 0:
            for spot_number in self.spots:
                spot = self.spots[spot_number]
                (x, y) = spot["position"]
                brightness = spot["brightness"]
                radius = spot["radius"]

                (r, g, b) = (0xFF, 0xFF, 0xFF)
                adjusted_brightness = (r * brightness / 10.0, g * brightness / 10.0, b * brightness / 10.0)

                canvas.draw_circle(x, y, radius, adjusted_brightness, adjusted_brightness)

        else:
            x = (w - 1) / 2.0
            y = (h - 1) / 2.0
            radius = 5 + 3.0 * math.sin(ticks * math.pi * 2.0 / 2000)
            brightness = 10

            (r, g, b) = (0xFF, 0xFF, 0xFF)
            adjusted_brightness = (r * brightness / 10.0, g * brightness / 10.0, b * brightness / 10.0)

            canvas.draw_circle(x, y, radius, adjusted_brightness, adjusted_brightness)

        return canvas
