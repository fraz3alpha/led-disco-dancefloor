__authors__ = ['Andrew Taylor']

import random
import time
import pygame
import math

from VisualisationPlugin import VisualisationPlugin

import logging

class DiscoFloorVisualisationPlugin(VisualisationPlugin):

	logger = logging.getLogger(__name__)

	# Colours
	__colours__ = {
		"black"    : (0,0,0),
		"red"      : (255,0,0),
		"green"    : (0,255,0),
		"blue"     : (0,0,255),
		"cyan"     : (0,255,255),
		"magenta"  : (255,0,255),
		"yellow"   : (255,255,0),
		"white"    : (255,255,255)
	}

	all_floor_colours = ("red", "green", "blue", "cyan", "magenta", "yellow", "white");
	primary_floor_colours = ("red", "green", "blue");

	# Buttons
	__buttons__ = {
		0	: "X",
		1	: "A",
		2	: "B",
		3	: "Y",
		4	: "LB",
		5	: "RB",
		8	: "SELECT",
		9	: "START"
	}

	square_size = 1
	max_square_size = 6

	colour_selection = 1

	fps = 2
	max_fps = 10

	def __init__ (self):
		self.clock = pygame.time.Clock()
		self.current_colours = None
		self.last_beat = 0
		self.colour_selection = self.all_floor_colours

	def configure(self, config):
		self.config = config
		self.logger.info("Config: %s" % config)

		# Get the fps
		self.fps = 2.0
		try:
			self.fps = float(self.config["fps"])
		except (ValueError, KeyError):
			pass	

		# Get the square size
		self.square_size = 2
		try:
			self.square_size = int(self.config["size"])
		except (ValueError, KeyError):
			pass	
	

	def handle_event(self, event):
		"""
		Handle the pygame event sent to the plugin from the main loop
		"""

		joypad = action = action_value = event_name = None
		
		try:
			event_name_temp = pygame.event.event_name(event.type)

			if (event_name_temp == "JoyButtonDown"):
				button = self.__buttons__[event.button]
				if (button != None):
					if (button == "LB"):
						if (self.square_size > 1):
							self.square_size -= 1
					if (button == "RB"):
						if (self.square_size < self.max_square_size):
							self.square_size += 1

					if (button == "A"):
						self.colour_selection = self.all_floor_colours
					if (button == "B"):
						self.colour_selection = self.primary_floor_colours
					if (button == "Y"):
						if (self.fps > 1):
							self.fps -= 1
					if (button == "X"):
						if (self.fps < self.max_fps):
							self.fps += 1

		except Exception as ex:
			print (ex)
			self.logger.error("ColourCycleExtraLargePlugin: %s" % ex)

		return None

	def regenerate_colours(self, colour_set, size):

		colours = []
		for i in range(size):
			new_colour = self.__colours__[colour_set[random.randint(0,len(colour_set)-1)]]
			colours.append(new_colour)
		return colours
		
	def draw_frame(self, canvas):
		"""
		Write the updated plugin state to the dance surface and blit
		"""

		w = canvas.get_width()
		h = canvas.get_height()

		# Regenerate the colours on each beat.
		current_beat = pygame.time.get_ticks() // (1000 / self.fps)
		if current_beat != self.last_beat or self.current_colours is None:
			#self.logger.info("Beat: %d" % current_beat)
			self.current_colours = self.regenerate_colours(self.colour_selection, int(w*h))
		self.last_beat = current_beat

		# The maximum number of squares (rounded up) displayable on each side
		x_squares = math.ceil(w // float(self.square_size))
		y_squares = math.ceil(h // float(self.square_size))

		for x in range(w):
			for y in range(h):
				row = (x // self.square_size )
				column = (y // self.square_size)
				index = int(row * y_squares + column)
				canvas.set_pixel_tuple(x,y, self.current_colours[index])

		self.clock.tick(25)
		return canvas

	def draw_splash(self, canvas):
		"""
		Construct a splash screen suitable to display for a plugin selection menu
		"""
		w = canvas.get_width()
		h = canvas.get_height()

		colours = dict(self.__colours__)
		del colours["black"]
		
		for x in range(0,w):
			for y in range(0,h):
				colour = colours.keys()[random.randint(1,len(colours)-1)]
				canvas.set_pixel_tuple(x,y, colours[colour])

		return canvas

		
