__authors__ = ['Andrew Taylor']

from lib.text import TextWriter

import logging
import math
import colorsys


class FloorCanvas(object):
    logger = logging.getLogger(__name__)

    # The floor canvas is a large array which we can draw on to
    # It provides a number of  methods that you would expect for
    # a canvas object, including shapes, painting pixels etc..

    # Some colour constants
    # You can get at them using e.g. FloorCanvas.BLACK
    BLACK = 0x000000
    WHITE = 0xFFFFFF
    RED = 0xFF0000
    GREEN = 0x00FF00
    BLUE = 0x0000FF
    YELLOW = 0xFFFF00
    MAGENTA = 0xFF00FF
    CYAN = 0x00FFFF

    # Constructor to set up the size and initial colour
    def __init__(self, width=0, height=0, colour=BLACK):
        self.width = 0
        if (width > 0):
            self.width = width
        self.height = 0
        if (height > 0):
            self.height = height
        self.logger.info("Creating a canvas with width=%d, height=%d" % (width, height))
        # Create the two dimensional array for the canvas object
        self.data = [[self.BLACK for y in range(height)] for x in range(width)]

    # Return an array data[x][y] of the canvas. This may or may not be
    #  the same as the internal representation, so don't get it directly,
    #  call this method instead
    def get_canvas_array(self):
        return self.data

    # See if the given pixel is on the canvas, and not off the side somewhere
    def is_in_range(self, x, y):
        if x < 0 or y < 0:
            return False
        if x >= self.width:
            return False
        if y >= self.height:
            return False
        return True

    # Get the size of the canvas
    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_size(self):
        return (self.width, self.height)

    # Set a pixel with an int value
    def set_pixel(self, x, y, colour, format="RGB", alpha=1.0):
        x = int(round(x, 0))
        y = int(round(y, 0))
        if format == "RGB":
            # If the colour is a tuple and not an int,
            #  unpack it into an int
            if type(colour) is tuple:
                colour = self.pack_colour_tuple(colour)
        elif format == "HSV":
            # It should always be a tuple for HSV, I'm not sure
            #  you can do anything if it isn't
            if type(colour) is tuple:
                colour = self.reformat(colorsys.hsv_to_rgb(*colour))
                colour = self.pack_colour_tuple(colour)
        if self.is_in_range(x, y):

            if alpha < 1.0:
                current_pixel_rgb = self.unpack_colour_tuple(self.get_pixel(x, y))
                new_colour = self.unpack_colour_tuple(colour)

                new_r = current_pixel_rgb[0] * (1 - alpha) + new_colour[0] * alpha
                new_g = current_pixel_rgb[1] * (1 - alpha) + new_colour[1] * alpha
                new_b = current_pixel_rgb[2] * (1 - alpha) + new_colour[2] * alpha

                pixel_colour = self.pack_colour_tuple((new_r, new_g, new_b))

                self.data[x][y] = pixel_colour
            else:
                self.data[x][y] = colour

    def reformat(self, colour):
        return int(round(colour[0] * 255)) % 256, \
               int(round(colour[1] * 255)) % 256, \
               int(round(colour[2] * 255)) % 256

    # Normalization method, so the colors are in the range [0, 1]
    def normalize(self, colour):
        return colour[0] / 255.0, colour[1] / 255.0, colour[2] / 255.0

    # Set a pixel with an tuple value
    # Deprecated, set_pixel now takes either an int or tuple
    def set_pixel_tuple(self, x, y, colour):
        x = int(round(x, 0))
        y = int(round(y, 0))
        if self.is_in_range(x, y):
            self.data[x][y] = self.pack_colour_tuple(colour)

    # Set a pixel with a float tuple value
    def set_float_pixel_tuple(self, x, y, colour):
        """
        Set the value of the pixel at (x,y) to colour((r,g,b)) where r g and b are floats
        """
        (floatR, floatG, floatB) = colour
        intR = int(floatR * 255)
        intG = int(floatG * 255)
        intB = int(floatB * 255)
        self.set_pixel_tuple(x, y, (intR, intG, intB))

    # Return the colour as an int (i.e the value of 0xRRGGBB)
    def get_pixel(self, x, y):
        if self.is_in_range(x, y):
            return self.data[x][y]
        return None

    # Return the colour as (R,G,B) tuple
    def get_pixel_tuple(self, x, y, format="RGB"):
        if format == "RGB":
            return self.unpack_colour_tuple(self.get_pixel(x, y))
        elif format == "HSV":
            return colorsys.rgb_to_hsv(*self.normalize(self.get_pixel(x, y)))

    def unpack_colour_tuple(self, colour):
        if colour < 0:
            return (0, 0, 0)
        red = (colour >> 16) & 0xFF
        green = (colour >> 8) & 0xFF
        blue = colour & 0xFF
        return (red, green, blue)

    def pack_colour_tuple(self, colour):
        (red, green, blue) = colour
        # Ensure the values are ints
        red = int(red)
        green = int(green)
        blue = int(blue)

        value = (red << 16) + (green << 8) + blue
        return value

    def draw_box(self, top_left, bottom_right, colour):
        """
        Fill the box from top left to bottom right with the given colour
        """
        (tlx, tly) = top_left
        (brx, bry) = bottom_right
        if tlx <= brx and tly <= bry:
            y = tly
            while y <= bry:
                x = tlx
                while x <= brx:
                    self.set_pixel(x, y, colour)
                    x += 1
                y += 1

    def draw_line(self, from_x, from_y, to_x, to_y, colour, aliasing=None):
        # Work out which direction has the most pixels
        #  so that there are no gaps in the line
        if (from_x == to_x and from_y == to_y):
            self.set_pixel(int(from_x), int(from_y), colour)
            return None
        #self.logger.verbose("(%d,%d) > (%d,%d)" % (from_x, from_y, to_x, to_y))
        if (abs(from_x - to_x) > abs(from_y - to_y)):
            # Make sure that to_x is >= from_x so that the range()
            #  works properly
            if to_x < from_x:
                temp = to_x
                to_x = from_x
                from_x = temp

                temp = to_y
                to_y = from_y
                from_y = temp
            #self.logger.verbose("Going from x=%d to x=%d" % (from_x, to_x))
            gradient = float(to_y - from_y) / float(to_x - from_x)
            #self.logger.verbose("Gradient=%f, c=%d" % (gradient, from_y))
            for x in range(to_x - from_x + 1):
                y = gradient * float(x) + from_y
                self.set_pixel(int(x + from_x), int(y), colour)
        else:
            # Make sure that to_y is >= from_y so that the range()
            #  works properly
            if to_y < from_y:
                temp = to_x
                to_x = from_x
                from_x = temp

                temp = to_y
                to_y = from_y
                from_y = temp
            #self.logger.verbose("Going from y=%d to y=%d" % (from_y, to_y))
            gradient = float(to_x - from_x) / float(to_y - from_y)
            for y in range(to_y - from_y + 1):
                x = gradient * float(y) + from_x
                self.set_pixel(int(x), int(y + from_y), colour)

    # Set the entire canvas to a single colour
    def set_colour(self, colour):
        if type(colour) is tuple:
            colour = self.pack_colour_tuple(colour)
        for x in range(self.width):
            for y in range(self.height):
                self.data[x][y] = colour

    # Text methods:
    def draw_text(self, text, colour, x_pos, y_pos, custom_text=None):
        # Returns the text size as a (width, height) tuple for reference
        text_size = TextWriter.draw_text(self, text, colour, x_pos, y_pos, custom_text)
        return text_size

    def get_text_size(self, text):
        # Returns the text size as a (width, height) tuple for reference,
        #  but doesn't actually draw anything because it doesn't pass a surface through
        return TextWriter.draw_text(None, text, (0, 0, 0), 0, 0)

    def draw_circle(self, x_centre, y_centre, radius, colour, fill, antialias=None):

        #radius = int(round(radius, 0))

        x = 0
        y = int(math.sqrt(radius ** 2 - 1) + 0.5)

        all_set_pixels = set()
        while (x <= y):
            # The outline
            pixels_to_set = []
            pixels_to_set.append((x_centre - x, y_centre + y))
            pixels_to_set.append((x_centre + x, y_centre + y))
            pixels_to_set.append((x_centre - x, y_centre - y))
            pixels_to_set.append((x_centre + x, y_centre - y))

            pixels_to_set.append((x_centre - y, y_centre + x))
            pixels_to_set.append((x_centre + y, y_centre + x))
            pixels_to_set.append((x_centre - y, y_centre - x))
            pixels_to_set.append((x_centre + y, y_centre - x))

            all_set_pixels.update(pixels_to_set)

            for pixel in pixels_to_set:
                (pixel_x, pixel_y) = pixel
                self.set_pixel(pixel_x, pixel_y, colour)

            # The fill
            if fill is not None:
                if y >= 1:
                    y -= 1
                    self.draw_line(int(round(x_centre - x, 0)), int(round(y_centre + y, 0)),
                                   int(round(x_centre - x, 0)), int(round(y_centre + x, 0)), fill)
                    self.draw_line(int(round(x_centre + x, 0)), int(round(y_centre + y, 0)),
                                   int(round(x_centre + x, 0)), int(round(y_centre + x, 0)), fill)
                    self.draw_line(int(round(x_centre - x, 0)), int(round(y_centre - y, 0)),
                                   int(round(x_centre - x, 0)), int(round(y_centre - x, 0)), fill)
                    self.draw_line(int(round(x_centre + x, 0)), int(round(y_centre - y, 0)),
                                   int(round(x_centre + x, 0)), int(round(y_centre - x, 0)), fill)

                    self.draw_line(int(round(x_centre - y, 0)), int(round(y_centre + x, 0)),
                                   int(round(x_centre - x, 0)), int(round(y_centre + x, 0)), fill)
                    self.draw_line(int(round(x_centre + y, 0)), int(round(y_centre + x, 0)),
                                   int(round(x_centre + x, 0)), int(round(y_centre + x, 0)), fill)
                    self.draw_line(int(round(x_centre - y, 0)), int(round(y_centre - x, 0)),
                                   int(round(x_centre - x, 0)), int(round(y_centre - x, 0)), fill)
                    self.draw_line(int(round(x_centre + y, 0)), int(round(y_centre - x, 0)),
                                   int(round(x_centre + x, 0)), int(round(y_centre - x, 0)), fill)

            x += 1
            if x > radius: break
            y = int(math.sqrt(radius ** 2 - x ** 2) + 0.5)

        # This doesn't work that well.
        # Basically, it attempts to see if there are any pixels that should be fractionally illuminated
        #  by looking to see if any pixels are < 1.0 pixel away, and turn them on a bit
        if antialias is not None:
            self.logger.info("Total number of set pixels: %d" % (len(all_set_pixels)))

            surround_pixels = set()
            for pixel in all_set_pixels:
                (pixel_x, pixel_y) = pixel
                surround_pixels.add((pixel_x - 1, pixel_y))
                surround_pixels.add((pixel_x + 1, pixel_y))

                surround_pixels.add((pixel_x - 1, pixel_y + 1))
                surround_pixels.add((pixel_x, pixel_y + 1))
                surround_pixels.add((pixel_x + 1, pixel_y + 1))

                surround_pixels.add((pixel_x - 1, pixel_y - 1))
                surround_pixels.add((pixel_x, pixel_y - 1))
                surround_pixels.add((pixel_x + 1, pixel_y - 1))

            self.logger.info("Total number of surrounding pixels: %d" % (len(surround_pixels)))
            # The pixels that we haven't already set
            pixels_not_already_set = surround_pixels.difference(all_set_pixels)

            for pixel in pixels_not_already_set:
                (pixel_x, pixel_y) = pixel
                distance_away = math.sqrt((pixel_x - x_centre) ** 2 + (pixel_y - y_centre) ** 2)
                delta = abs(distance_away - radius)
                #self.logger.info("%d,%d is %f off" % (pixel_x, pixel_y, delta))
                if delta < 1.0:
                    delta /= 1.0
                    self.set_pixel(pixel_x, pixel_y, colour, "RGB", delta)

        return None


