__authors__ = ['Andrew Taylor']

import random
import time
import pygame
# Python comes with some color conversion methods.
import colorsys
# For Math things, what else
import math

from VisualisationPlugin import VisualisationPlugin

import logging

# Video available here:
# http://www.youtube.com/watch?v=ySJlUu2926A&feature=youtu.be

class SpeedingBlobsVisualisationPlugin(VisualisationPlugin):
    logger = logging.getLogger(__name__)

    speed_blobs = None

    blob_speeds = [500]

    def configure(self, config):
        self.config = config
        self.logger.info("Config: %s" % config)

    def new_random_blob(self, canvas):
        blob_entry = {}
        # Random Speed, ms/pixel
        blob_entry["speed"] = self.blob_speeds[random.randint(0, len(self.blob_speeds) - 1)]
        w = canvas.get_width()
        h = canvas.get_height()
        # Random X location
        blob_entry["start_x"] = random.randint(0, w)
        # Random Y location
        blob_entry["start_y"] = random.randint(0, h)
        # Random direction
        direction = {}
        direction["x"] = random.randint(0, 5) - 2
        direction["y"] = random.randint(0, 5) - 2
        if (direction["x"] == 0 and direction["y"] == 0):
            direction["x"] = 1
        blob_entry["direction"] = direction
        # Start time
        blob_entry["start_time"] = pygame.time.get_ticks()
        # Random colour
        blob_entry["colour"] = float(random.randint(0, 100)) / 200.0
        blob_entry["decay"] = float(random.randint(3, 6))

        blob_entry["complete"] = False

        return blob_entry

    def initial_blob_config(self, canvas):
        # Put 5 blobs in

        self.speed_blobs = []

        for i in range(4):
            self.speed_blobs.append(self.new_random_blob(canvas))

        return self.speed_blobs

    def configure(self, config):
        self.config = config
        self.logger.info("Config: %s" % config)
        self.clock = pygame.time.Clock()


    # Example, and following two functions taken from http://www.pygame.org/wiki/RGBColorConversion

    # Normalization method, so the colors are in the range [0, 1]
    def normalize(self, color):
        return color[0] / 255.0, color[1] / 255.0, color[2] / 255.0

    # Reformats a color tuple, that uses the range [0, 1] to a 0xFF
    # representation.
    def reformat(self, color):
        return int(round(color[0] * 255)) % 256, \
               int(round(color[1] * 255)) % 256, \
               int(round(color[2] * 255)) % 256

    def draw_frame(self, canvas):

        if self.speed_blobs is None:
            self.initial_blob_config(canvas)

        t = pygame.time.get_ticks()
        self.logger.debug("Ticks: %d" % t)

        canvas = self.draw_blobs(canvas, self.speed_blobs, t)

        # Check to see if we need to replace a blob with a new one
        for idx, blob in enumerate(self.speed_blobs):
            if blob.get("complete") is True:
                self.speed_blobs[idx] = self.new_random_blob(canvas)

        # Limit the frame rate
        self.clock.tick(25)
        return canvas

    def draw_splash(self, canvas):
        """
        Construct a splash screen suitable to display for a plugin selection menu
        """

        test_blobs = []

        blob_entry = {}
        # Random X location
        blob_entry["x"] = 2
        # Random Y location
        blob_entry["y"] = 2
        # Random colour
        blob_entry["colour"] = 0.2
        blob_entry["height"] = 2
        blob_entry["decay"] = 10

        test_blobs.append(blob_entry)

        blob_entry = {}
        # Random X location
        blob_entry["x"] = (canvas.get_width() - 1) / 2.0
        # Random Y location
        blob_entry["y"] = (canvas.get_height() - 1) / 2.0
        # Random colour
        blob_entry["colour"] = 0.5
        blob_entry["height"] = 0.5
        blob_entry["decay"] = 7.0

        test_blobs.append(blob_entry)

        blob_entry = {}
        # Random X location
        blob_entry["x"] = (canvas.get_width() - 1) / 2.0 + 5
        # Random Y location
        blob_entry["y"] = (canvas.get_height() - 1) / 2.0
        # Random colour
        blob_entry["colour"] = 0.5
        blob_entry["height"] = 0.5
        blob_entry["decay"] = 7.0

        test_blobs.append(blob_entry)

        # Draw the blobs
        canvas = self.draw_blobs(canvas, test_blobs, 0)
        return canvas

    def draw_blobs(self, canvas, blobs, t):

        # Period
        t_background_period = 20000
        # Fraction of the way through
        background_hue = (float(t) / float(t_background_period)) % 1

        # Create a blank "sheet"
        sheet = [[0 for y in range(canvas.get_height())] for x in range(canvas.get_width())]

        # Draw all of the blobs
        for blob in blobs:

            blob_height = blob["colour"]

            # If the blobs are defined as static, then
            # draw them where they lie, else calculate
            #  where they should appear
            blob_x = blob.get("x")
            blob_y = blob.get("y")

            if blob_x is None or blob_y is None:
                # try to calculate the blob's position

                t_delta = t - blob["start_time"]
                #			print "%d" % t_delta
                squares_to_travel = float(t_delta) / float(blob["speed"])

                direction = blob["direction"]

                offset = blob["decay"]

                x_offset = 0
                y_offset = 0

                x_delta = 0
                y_delta = 0
                if (direction["x"] == 0):
                    x_offset = 0
                else:
                    x_delta = direction["x"] * squares_to_travel - blob["start_x"]
                if (direction["x"] < 0):
                    x_offset = blob["decay"] + canvas.get_width()
                if (direction["x"] > 0):
                    x_offset = -blob["decay"]

                if (direction["y"] == 0):
                    y_offset = 0
                else:
                    y_delta = direction["y"] * squares_to_travel - blob["start_y"]
                if (direction["y"] < 0):
                    y_offset = blob["decay"] + canvas.get_height()
                if (direction["y"] > 0):
                    y_offset = -blob["decay"]

                # print "x_dir %d x_offset %d , y_dir %d y_offset %d" % (direction["x"], x_offset, direction["y"], y_offset)


                blob_x = blob["start_x"] + x_delta + x_offset
                blob_y = blob["start_y"] + y_delta + y_offset

                if (direction["x"] > 0):
                    if (blob_x > canvas.get_width() + blob["decay"]):
                        blob["complete"] = True
                else:
                    if (blob_x < 0 - blob["decay"]):
                        blob["complete"] = True

                if (direction["y"] > 0):
                    if (blob_y > canvas.get_height() + blob["decay"]):
                        blob["complete"] = True
                else:
                    if (blob_y < 0 - blob["decay"]):
                        blob["complete"] = True


            # The central pixel should remain the correct colour at all times.
            # The problem occurs when the background colour 'overtakes' the blob colour
            # bg hue [0,1] , blob hue say 0.5
            # For blob hue > bg hue, then it is straight forward, the hue gradually
            #  decreases until it meets the bg hue value (according to the appropriate
            #  drop-off formula
            # For bg hue > blob hue, then the decay starts to go in the other direction,
            #  with a negative delta, and the hue should actually be increased up to the
            #  bg hue value
            # But then what happens when the bg hue wraps?
            # The bg hue wraps from 0 to 1, and now what happens to the decay? where previously
            #  it may have gone through the green end of the spectrum, not it has to go through
            #  blue according to the above formula.

            # If we think of the canvas as an sheet, and the blobs pinch the sheet up (like the general
            #  relativity rubber-sheet analogy, but the other way up) then it doesn't matter that numbers
            #  wrap, we just want to apply a height map colour, with the bottom varying

            for x in range(canvas.get_width()):
                for y in range(canvas.get_height()):
                    # Calculate how far away from the centre of the blob the centre of this pixel is
                    x_d = x - blob_x
                    y_d = y - blob_y
                    distance_away = math.sqrt(x_d * x_d + y_d * y_d)
                    decay = blob["decay"]
                    # Only draw pixels in the decay zone
                    if (distance_away < decay):
                        # Calculate the scaling factor
                        decay_amount = (math.cos(math.pi * distance_away / decay) + 1.0) / 2.0
                        # This compounds any blobs on top of each other automatically
                        sheet[x][y] += (blob_height * decay_amount)

        # Now translate the sheet height into colours
        for x in range(canvas.get_width()):
            for y in range(canvas.get_height()):
                hue = background_hue + sheet[x][y]
                rgb_colour = self.reformat(colorsys.hsv_to_rgb(hue, 1.0, 1.0))
                canvas.set_pixel(x, y, rgb_colour)

        return canvas
