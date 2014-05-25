__authors__ = ['Andrew Taylor']

import random
import time
import pygame
import math

from VisualisationPlugin import VisualisationPlugin
from lib.controllers import ControllerInput

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

	square_size = 2
	max_square_size = 6

	colour_selection = 1

	brightness = 1.0
	brightness_step = 0.1

	fps = 2
	max_fps = 10

	def __init__ (self):
		self.clock = pygame.time.Clock()
		self.current_colours = None
		self.last_beat = 0
		self.colour_selection = self.all_floor_colours
		self.brightness = 1.0
		# Set this to true to force a refresh of the colours
		self.force_regenerate_colours = False

	def configure(self, config):
		self.config = config
		self.logger.info("Config: %s" % config)

		# Seed the random function with the current time
		random.seed()

		self.fps = 2
		self.square_size = 2

		if config is not None:
			# Get the fps
			try:
				self.fps = int(self.config["fps"])
			except (ValueError, KeyError):
				pass	

			# Get the square size
			try:
				self.square_size = int(self.config["square_size"])
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
				#button = self.__buttons__[event.button]
				button = event.button
				if (button != None):
					if (button == ControllerInput.BUMPER_LEFT):
						if (self.square_size > 1):
							self.square_size -= 1
					if (button == ControllerInput.BUMPER_RIGHT):
						if (self.square_size < self.max_square_size):
							self.square_size += 1

					if (button == ControllerInput.BUTTON_A):
						if self.colour_selection != self.all_floor_colours:
							self.colour_selection = self.all_floor_colours
							self.force_regenerate_colours = True
					if (button == ControllerInput.BUTTON_B):
						if self.colour_selection != self.primary_floor_colours:
							self.colour_selection = self.primary_floor_colours
							self.force_regenerate_colours = True
					if (button == ControllerInput.BUTTON_Y):
						if (self.fps > 0):
							self.fps -= 1
					if (button == ControllerInput.BUTTON_X):
						if (self.fps < self.max_fps):
							self.fps += 1

			elif (event_name_temp == "JoyAxisMotion"):
				if event.axis == 1:
					# The axis is upside down, -1 = up
					if event.value < -0.5:
						self.increment_brightness()
					elif event.value > 0.5:
						self.decrement_brightness()
				if event.axis == 0:
					# Left and Right, generated new colours
					if event.value < -0.5 or event.value > 0.5:
						self.force_regenerate_colours = True
			
		except Exception as ex:
			print (ex)
			self.logger.error("ColourCycleExtraLargePlugin: %s" % ex)

		return None

	def increment_brightness(self):
		if self.brightness < 1.0:
			self.brightness += self.brightness_step
		if self.brightness > 1.0:
			self.brightness = 1.0
		self.logger.info("Brightness: %f" % self.brightness)
		return None

	def decrement_brightness(self):
		if self.brightness > 0.0:
			self.brightness -= self.brightness_step
		if self.brightness < 0.0:
			self.brightness = 0.0
		self.logger.info("Brightness: %f" % self.brightness)
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

		# If there are no colours yet, regenerate
		if ((self.current_colours is None) or (self.force_regenerate_colours == True)):
			self.current_colours = self.regenerate_colours(self.colour_selection, int(w*h))
			self.force_regenerate_colours = False
		else:
			# If we are on static, don't regenerated
			if self.fps > 0:
				# Regenerate the colours on each beat.
				current_beat = pygame.time.get_ticks() // (1000 / self.fps)
				if current_beat != self.last_beat:
					self.current_colours = self.regenerate_colours(self.colour_selection, int(w*h))
					self.last_beat = current_beat

		self.draw_floor(canvas, self.current_colours, self.square_size)

		self.clock.tick(25)
		return canvas

	def draw_floor(self, canvas, colours, square_size):

		w = canvas.get_width()
		h = canvas.get_height()

		# The maximum number of squares (rounded up) displayable on each side
		x_squares = math.ceil(w // float(square_size))
		y_squares = math.ceil(h // float(square_size))

		for x in range(w):
			for y in range(h):
				row = (x // square_size )
				column = (y // square_size)
				index = int(row * y_squares + column)
				(r,g,b) = colours[index]
				adjusted_brightness = (r*self.brightness, g*self.brightness, b*self.brightness)
				canvas.set_pixel(x,y, adjusted_brightness)

		return canvas

	def draw_splash(self, canvas):
		"""
		Construct a splash screen suitable to display for a plugin selection menu
		"""
		w = canvas.get_width()
		h = canvas.get_height()

		# Use a defined seed
		random.seed(0)

		colours = self.regenerate_colours(self.all_floor_colours, int(w*h))

		self.draw_floor(canvas, colours, 2)

		return canvas

		
