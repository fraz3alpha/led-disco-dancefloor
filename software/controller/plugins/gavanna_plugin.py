__authors__ = ['Andrew Taylor']

import logging
import pygame
import random
import time
from datetime import datetime

from DDRPi import DDRPiPlugin

class GavannaPlugin(DDRPiPlugin):

	pulse_rate = 2000
	pulse_increasing = 1
	pulse_last_ratio = 0

	def post_invalidate(self):
		self.changed = 1

	def configure(self, config, image_surface):
		"""
		This is an example of an end user module - need to make sure we can get
		the main image surface and config to write to them both...
		"""
		self.ddrpi_config = config
		self.ddrpi_surface = image_surface
		self.clock = pygame.time.Clock()
	
	def __name__(self):
		return 'Text Plugin'

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

	def pause(self):
		return None

	def resume(self):
		self.post_invalidate()
		return None
		
	def handle(self, event):
		"""
		Handle the pygame event sent to the plugin from the main loop
		"""
		return None

	def draw_heart(self, colour, x_pos, y_pos, fill):
		w = self.ddrpi_surface.width
		h = self.ddrpi_surface.height

		heart = (0x06, 0x09, 0x11, 0x22, 0x11, 0x09, 0x06);
		if (fill > 0):
			heart = (0x06, 0x0F, 0x1F, 0x3E, 0x1F, 0x0F, 0x06);
		heart_height = 6
		heart_width = len(heart)

		for x in range(0, heart_width):
			for y in range(0, heart_height):
				pixel_value = (heart[x] >> y) & 0x01
				if (pixel_value == 1):
					self.ddrpi_surface.draw_tuple_pixel(x+x_pos,y+y_pos, colour)

		return None


	
	def update_surface(self):
		"""
		Write the updated plugin state to the dance surface and blit
		"""

		w = self.ddrpi_surface.width
		h = self.ddrpi_surface.height
			
		for x in range(0,w):
			for y in range(0,h):
				self.ddrpi_surface.draw_tuple_pixel(x,y, (0,0,0))

		self.ddrpi_surface.draw_text("Gav", (0xFF,0xFF,0xFF), 3, 0)
		self.ddrpi_surface.draw_text("Anna", (0xFF,0xFF,0xFF), 0, 11)

		# Calculate the red value for the heart's centre
		ratio = int(255.0 * (float(pygame.time.get_ticks() % self.pulse_rate) / float(self.pulse_rate)))

		# Increase then decrease the value
		self.pulse_increasing = 1
		pulse_mod = pygame.time.get_ticks() % (2*self.pulse_rate)

		# Calculate which
		if (pygame.time.get_ticks() % (2*self.pulse_rate) > self.pulse_rate):
			self.pulse_increasing = -1

		# Work out the red value
		red_value = ratio
		if (self.pulse_increasing == -1):
			red_value = 255 - ratio

		# Draw the fading heart...
		self.draw_heart((red_value, 0x00, 0x00), w/2 -4, h/2 - 2, 1)
		# .. and a solid outline
		self.draw_heart((0xFF, 0x00, 0x00), w/2 -4, h/2 - 2, 0)

		# Limit the frame rate
		self.ddrpi_surface.blit()

		# Rate limit it
		self.clock.tick(25)

	def display_preview(self):
		"""
		Construct a splash screen suitable to display for a plugin selection menu
		"""
		w = self.ddrpi_surface.width
		h = self.ddrpi_surface.height
		
		# Background is black
		for x in range(0,w):
			for y in range(0,h):
				self.ddrpi_surface.draw_tuple_pixel(x,y, (0,0,0))

		# Draw a solid red heart in the middle (ish)
		self.draw_heart((0xFF, 0x00, 0x00), w/2 -4, h/2 - 2, 1)

		self.ddrpi_surface.blit()

		
