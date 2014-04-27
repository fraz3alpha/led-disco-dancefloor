__authors__ = ['Andrew Taylor']

import random
import time
import pygame

from VisualisationPlugin import VisualisationPlugin

import logging
from lib.floorcanvas import FloorCanvas

class ScrollingTextVisualisationPlugin(VisualisationPlugin):
	
	logger = logging.getLogger(__name__)

	start_tick = -1
	# ms per pixel of scrolling
	scroll_speed = 100

	def __init__ (self):
		self.clock = pygame.time.Clock()

	def start(self):
		"""
		Start writing to the surface
		"""
		# Setup recurring events
		self.start_tick = pygame.time.get_ticks()

		return None
		
	def draw_frame (self, canvas):

		time_since_start = pygame.time.get_ticks() - self.start_tick
		return self.draw_frame_t(canvas, time_since_start)

	def draw_frame_t (self, canvas, t):
		"""
		Write the updated plugin state to the dance surface and blit
		"""
		w = canvas.get_width()
		h = canvas.get_height()

		text = "TEST"

		text_size = canvas.get_text_size("Test")
		text_width = text_size[0]
		text_height = text_size[1]

		canvas.set_colour(FloorCanvas.BLACK)

		# Total time to traverse the screen = 
		#  (border right + border left + surface width + text width in pixels) * time per pixel
		offscreen_buffer = 5
		time_on_screen = (offscreen_buffer * 2 + text_width + w) * self.scroll_speed

		# Work out what fraction of the duration we are the way through this, based on when we started
		position_delta = t % time_on_screen
		# The text starts at $offscreen_buffer + w (off the right edge), and then scrolls left
		x_position = int(w + offscreen_buffer - position_delta / self.scroll_speed)

		y_position = int((h - text_height) / 2)

		canvas.draw_text("Test", (0xFF,0,0), x_position, y_position)

		# Limit the frame rate
		self.clock.tick(25)
		return canvas
		
	def draw_splash (self, canvas):
		return canvas

