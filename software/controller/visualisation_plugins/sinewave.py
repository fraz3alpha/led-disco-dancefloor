
from VisualisationPlugin import VisualisationPlugin

import pygame
import math

import logging

from DDRPi import FloorCanvas

class SineWaveVisualisationPlugin(VisualisationPlugin):

	logger = logging.getLogger(__name__)

	def __init__(self):
		self.clock = pygame.time.Clock()

	def configure(self, config):
		self.config = config
		self.logger.info("Config: %s" % config)

	def draw_frame(self,canvas):

		# Limit the frame rate.
		# This sleeps so that at least 25ms has passed since tick() 
		#  was last called. It is a no-op if the loop is running slow
		self.clock.tick(25)
		# Draw whatever this plugin does
		return self.draw_surface(canvas, pygame.time.get_ticks())

	def draw_splash(self,canvas):
		return self.draw_surface(canvas, 0)

	def draw_surface(self,canvas):
		return self.draw_surface(canvas, 0)

	def draw_surface(self, canvas, ticks):

		# Get the background colour
		background_colour = FloorCanvas.GREEN
		try:
			background_colour = getattr(FloorCanvas, self.config["background_colour"].upper())
		except (AttributeError, KeyError):
			pass

		# Set the background colour
		canvas.set_colour(background_colour)

		# Get the wave colour
		wave_colour = FloorCanvas.WHITE
		try:
			wave_colour = getattr(FloorCanvas, self.config["colour"].upper())
		except (AttributeError, KeyError):
			pass

		# Get the amplitude
		amplitude = 5.0
		try:
			amplitude = float(self.config["amplitude"])
		except (ValueError, KeyError):
			pass

		# Get the period
		period = 18.0
		try:
			period = float(self.config["period"])
		except (ValueError, KeyError):
			pass

		phase_offset = 0.0
		frequency = 1.0

		phase_offset = 2 * math.pi * frequency * ticks / 1000
		#phase_offset = 0

		w = canvas.get_width();
		h = canvas.get_height()
		previous_x = None
		previous_y = None
		for x in range(w):
			phase = math.pi * 2 * x / period
			y = h/2.0 + amplitude * math.sin(phase_offset + phase)
			
			if previous_y != None and previous_x != None:
				# Draw line between previous point at this one
				#self.surface.draw_line(int(round(previous_x)), int(round(previous_y)), int(round(x)), int(round(y)), FloorCanvas.WHITE)
				canvas.draw_line(int(previous_x), int(previous_y), int(x), int(y), wave_colour)
			#self.surface.set_pixel(int(x),int(y),FloorCanvas.WHITE)
			previous_x = x
			previous_y = y

		return canvas

	def get_valid_arguments(self):
		args =	["background_colour",	# The background colour of the wave
			"colour",		# The colour of the wave
			"speed",		# The speed of the wave
			"amplitude", 		# The amplitude of the wave
			]
		return args
