__authors__ = ['Andrew Taylor']

import random
import time
import pygame

from DDRPi import DDRPiPlugin

class ScrollingTextPlugin(DDRPiPlugin):
	
	start_tick = -1
	# ms per pixel of scrolling
	scroll_speed = 100

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
		self.start_tick = pygame.time.get_ticks()

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

		text = "TEST"

		time_since_start = pygame.time.get_ticks() - self.start_tick

		text_size = self.ddrpi_surface.get_text_size("Test")
		text_width = text_size[0]
		text_height = text_size[1]

		# Draw the background (black)
		for x in range(0,w):
			for y in range(0,h):
				r = 0
				g = 0
				b = 0
				# random.randint(0,255)
				self.ddrpi_surface.draw_tuple_pixel(x,y,(r,g,b))


		# Total time to traverse the screen = 
		#  (border right + border left + surface width + text width in pixels) * time per pixel
		offscreen_buffer = 5
		time_on_screen = (offscreen_buffer * 2 + text_width + w) * self.scroll_speed

		# Work out what fraction of the duration we are the way through this, based on when we started
		position_delta = time_since_start % time_on_screen
		# The text starts at $offscreen_buffer + w (off the right edge), and then scrolls left
		x_position = int(w + offscreen_buffer - position_delta / self.scroll_speed)

		y_position = int((h - text_height) / 2)

		self.ddrpi_surface.draw_text("Test", (0xFF,0,0), x_position, y_position)

		# Limit the frame rate
		self.clock.tick(25)
		self.ddrpi_surface.blit()
		
	def display_preview(self):
		"""
		Construct a splash screen suitable to display for a plugin selection menu
		"""
		self.update_surface()
