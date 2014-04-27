
from VisualisationPlugin import VisualisationPlugin

import pygame
import math

from DDRPi import FloorCanvas

class SineWaveVisualisationPlugin(VisualisationPlugin):

	def __init__(self):
		self.clock = pygame.time.Clock()

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

		# Set the background colour
		canvas.set_colour(FloorCanvas.GREEN)

		#self.surface.draw_line(0,0 ,9,5, FloorCanvas.WHITE)
		#self.surface.draw_line(9,5 ,17,0, FloorCanvas.WHITE)
		#exit()

		amplitude = 5.0
		period = 18.0
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
				canvas.draw_line(int(previous_x), int(previous_y), int(x), int(y), FloorCanvas.WHITE)
			#self.surface.set_pixel(int(x),int(y),FloorCanvas.WHITE)
			previous_x = x
			previous_y = y

		return canvas

