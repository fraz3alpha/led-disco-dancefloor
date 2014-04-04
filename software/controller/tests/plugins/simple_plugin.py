__authors__ = ['Joel Wright']

import random
import time
import pygame

from DDRPi import DDRPiPlugin

class SimplePlugin(DDRPiPlugin):
	
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
		
	def update_surface(self):
		"""
		Write the updated plugin state to the dance surface and blit
		"""
		w = self.ddrpi_surface.width
		h = self.ddrpi_surface.height
		
		for x in range(0,w):
			for y in range(0,h):
				r = random.randint(0,255)
				g = random.randint(0,255)
				b = random.randint(0,255)
				self.ddrpi_surface.draw_tuple_pixel(x,y,(r,g,b))

		# Limit the frame rate
		self.clock.tick(40)
		self.ddrpi_surface.blit()
		
	def display_preview(self):
		"""
		Construct a splash screen suitable to display for a plugin selection menu
		"""
		self.update_surface()
