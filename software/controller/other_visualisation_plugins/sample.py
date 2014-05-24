
from VisualisationPlugin import VisualisationPlugin

import pygame
import logging

from DDRPi import FloorCanvas

class SampleVisualisationPlugin(VisualisationPlugin):

	logger = logging.getLogger(__name__)

	def __init__(self):
		self.clock = pygame.time.Clock()

	# Nothing specific to be done before this starts, although we could 
	#  set self.clock here. Stash any config so we can use it later
	def configure(self, config):
		self.config = config
		self.logger.info("Config: %s" % config)

	# This will just keep running, nothing specific to do for start(), stop(),
	#  pause() or resume()
	def start(self):
		pass

	def stop(self):
		pass

	def pause(self):
		pass

	def resume(self):
		pass

	def draw_frame(self, canvas):

		# Draw whatever this plugin does.
		canvas = self.draw_surface(canvas, pygame.time.get_ticks())

		# Limit the frame rate.
		# This sleeps so that at least 25ms has passed since tick() 
		#  was last called. It is a no-op if the loop is running slow
		self.clock.tick(25)

		# We need to return our decorated surface
		return canvas

	def draw_splash(self,canvas):
		return self.draw_surface(canvas,0)

	# We've split the method that does the drawing out, so that draw_splash()
	#  can call it with a fixed timer
	def draw_surface(self, canvas, ticks):
		canvas.set_colour(FloorCanvas.BLUE)
		# Return the canvas
		return canvas

