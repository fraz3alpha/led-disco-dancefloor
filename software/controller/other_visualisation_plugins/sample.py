
from VisualisationPlugin import VisualisationPlugin

import pygame

from DDRPi import FloorCanvas

class SampleVisualisationPlugin(VisualisationPlugin):

	logger = logging.getLogger(__name__)

	def __init__(self):
		self.clock = pygame.time.Clock()

	# Nothing specific to be done before this starts, although we could 
	#  set self.clock here.
	def configure(self):
		pass

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

	def draw_frame(self, surface):

		# Limit the frame rate.
		# This sleeps so that at least 25ms has passed since tick() 
		#  was last called. It is a no-op if the loop is running slow
		self.clock.tick(25)
		# Draw whatever this plugin does.
		# We need to return our decorated surface
		return self.draw_surface(surface, pygame.time.get_ticks())

	def draw_splash(self,canvas):
		return self.draw_surface(canvas,0)

	# We've split the method that does the drawing out, so that draw_splash()
	#  can call it with a fixed timer
	def draw_surface(self, canvas, ticks):
		canvas.set_colour(FloorCanvas.BLUE)
		# Return the canvas
		return canvas

