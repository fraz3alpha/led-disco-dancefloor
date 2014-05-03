
from VisualisationPlugin import VisualisationPlugin

import pygame
import colorsys
import math, cmath

from DDRPi import FloorCanvas
import logging

class SpinningWheelVisualisationPlugin(VisualisationPlugin):

	logger = logging.getLogger(__name__)

	def __init__(self):
		self.clock = pygame.time.Clock()
		self.logger.info("Initialising SpinningWheelVisualisationPlugin")

	def configure(self, config):
		self.config = config
		self.logger.info("Config: %s" % config)

	def draw_frame(self, canvas):

		canvas = self.draw_surface(canvas, pygame.time.get_ticks())
		# Limit the frame rate.
		# This sleeps so that at least 25ms has passed since tick() 
		#  was last called. It is a no-op if the loop is running slow
		self.clock.tick(25)
		# Draw whatever this plugin does
		return canvas

	def draw_splash(self, canvas):
		return self.draw_surface(canvas, 0)

	def draw_surface(self,canvas):
		return self.draw_surface(canvas, 0)

	def draw_surface(self, canvas, t):
		w = canvas.get_width()
		h = canvas.get_height()

		x_centre_pixel = (w-1)/2.0
		y_centre_pixel = (h-1)/2.0

		# The hue varies by angle, with a constant offset - the speed
		#  that it rotates

		offset = 0.0

		speed = 30.0
		colours = "FULL_COLOUR"

		if self.config != None:
			try:
				speed = float(self.config["speed"])
			except (AttributeError, ValueError, KeyError):
				pass

			try:
				if self.config["colours"] in ["FULL_COLOUR", "BLACK_AND_WHITE"]:
					colours = self.config["colours"]
			except (AttributeError, KeyError):
				pass

		for x in range(w):
			for y in range(h):
				x_diff = x-x_centre_pixel
				y_diff = y-y_centre_pixel

				# Get angle in the range [0,2pi]
				angle = cmath.phase(complex(-x_diff, y_diff)) + math.pi
			
				# Add a bit according to the phase				
				angle += speed * t / (1000.0 * 2.0 * math.pi)

				# Get it back in the range [0,2pi]
				(angle_div, angle_mod) = divmod(angle, 2.0 * math.pi)

				# Default, full colour
				hue = angle_mod / (2.0 * math.pi)
				saturation = 1.0
				lightness = 0.5
				if colours == "BLACK_AND_WHITE":
					hue = 0.0
					saturation = 0.0
					lightness = angle_mod / (1.0 * math.pi)


				rgb_colour = self.reformat(colorsys.hsv_to_rgb(*(hue,saturation,lightness)))
				canvas.set_pixel_tuple(x,y,rgb_colour)
		#exit(1)
		return canvas

	# Example, and following two functions taken from http://www.pygame.org/wiki/RGBColorConversion

	# Normalization method, so the colors are in the range [0, 1]
	def normalize (self, color):
	    return color[0] / 255.0, color[1] / 255.0, color[2] / 255.0
 
	# Reformats a color tuple, that uses the range [0, 1] to a 0xFF
	# representation.
	def reformat (self, color):
	    return int (round (color[0] * 255)), \
	           int (round (color[1] * 255)), \
	           int (round (color[2] * 255))

