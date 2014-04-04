__authors__ = ['Andrew Taylor']

import random
import time
import pygame
# Python comes with some color conversion methods.
import colorsys
# For Math things, what else
import math

from DDRPi import DDRPiPlugin

# Video available here:
# http://www.youtube.com/watch?v=ySJlUu2926A&feature=youtu.be

class BlobsPlugin(DDRPiPlugin):
	
	def configure(self, config, image_surface):
		"""
		This is an example of an end user module - need to make sure we can get
		the main image surface and config to write to them both...
		"""
		self.ddrpi_config = config
		self.ddrpi_surface = image_surface
		self.clock = pygame.time.Clock()

	def start(self):
		"""
		Start writing to the surface
		"""
		# Setup recurring events
		return None

	def stop(self):
		"""
		Stop writing to the surface and clean up
		"""
		# Stop recurring events
		return None
		
	def handle(self, event):
		"""
		Handle the pygame event sent to the plugin from the main loop
		"""
		return None
		
	def pause(self):
		"""
		Pauses the plugin - e.g. saves a game state when we enter menu mode.
		"""
		return None

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

	def update_surface(self):
		self.wavy_blob()		

		# Limit the frame rate
		self.clock.tick(25)
		self.ddrpi_surface.blit()

	def wavy_blob(self):
		self.wavy_blob_t(pygame.time.get_ticks())

	def wavy_blob_t(self, t):
		# Pass in the time to create the image for, usually the value of pygame.time.get_ticks(),
		#  but for a splash screen, you probably want to pick a number - 0 is good

		w = self.ddrpi_surface.width
		h = self.ddrpi_surface.height

		x_centre_pixel = w/2.0
		y_centre_pixel = h/2.0
		drop_off_distance = 5.0

		starting_colour_rgb = (255, 0, 0)
		starting_colour_hsv = colorsys.rgb_to_hsv (*self.normalize (starting_colour_rgb))

		t_movement_period = 20000.0
		t_movement_adjustment = t*2.0*math.pi/t_movement_period
		movement_scale_x = w/4.0
		movement_scale_y = h/4.0

		# the centre moves in a figure of eight (infinity sign)
		x_this_centre_pixel = x_centre_pixel + movement_scale_x * math.sin(t_movement_adjustment)
		y_this_centre_pixel = y_centre_pixel + movement_scale_y * math.sin(2.0 * t_movement_adjustment)

		max_distance_away = math.sqrt(w*w + h*h)/4.0

		for x in range(0,w):
			for y in range(0,h):

				hsv_colour = []
				for i in range(0,3):
					hsv_colour.append(0x00)
				hsv_colour[1] = starting_colour_hsv[1]
				hsv_colour[2] = starting_colour_hsv[2]

				x_delta = math.fabs(x-x_this_centre_pixel)
				y_delta = math.fabs(y-y_this_centre_pixel)

				distance_away = math.sqrt(x_delta*x_delta + y_delta*y_delta)
				# print "Distance away for %d,%d : %f" % (x,y, distance_away)

				t_period = 4000.0
				t_adjustment = t*2.0*math.pi/t_period
				multiplier = (math.sin(t_adjustment) + 1.0)/2.0

				# We vary only the hue between 0.0 (red) and 1/3 (green)
				hsv_colour[0] = 0.33 * ((math.sin(distance_away/3.0 - t_adjustment) + 1.0) / 2.0)

				rgb_colour = self.reformat(colorsys.hsv_to_rgb(*hsv_colour))
				self.ddrpi_surface.draw_tuple_pixel(x,y,rgb_colour)


	def display_preview(self):
		"""
		Construct a splash screen suitable to display for a plugin selection menu
		"""
		self.wavy_blob_t(0)
		self.ddrpi_surface.blit()
