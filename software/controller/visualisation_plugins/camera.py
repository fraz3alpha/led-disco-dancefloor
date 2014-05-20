
from VisualisationPlugin import VisualisationPlugin

import pygame
import pygame.camera
import logging

from DDRPi import FloorCanvas

class CameraVisualisationPlugin(VisualisationPlugin):

	logger = logging.getLogger(__name__)

	def __init__(self):
		self.clock = pygame.time.Clock()
		self.webcam = None

	# Nothing specific to be done before this starts, although we could 
	#  set self.clock here. Stash any config so we can use it later
	def configure(self, config):
		self.config = config
		self.logger.info("Config: %s" % config)

	# This will just keep running, nothing specific to do for start(), stop(),
	#  pause() or resume()
	def start(self):
		pygame.camera.init()
		camera_list = pygame.camera.list_cameras() # list available cameras
		self.logger.info("Cameras found: %d" % len(camera_list))
		if len(camera_list) > 0:
			for camera in camera_list:
				self.logger.info("CAMERA: %s" % camera)
#			# Choose the first webcam
			self.webcam = pygame.camera.Camera(camera_list[0],(800,600))
#
			self.webcam.start() # start camera
		pass

	def stop(self):
		pass

	def pause(self):
		pass

	def resume(self):
		pass

	def draw_frame(self, surface):

		if self.webcam is not None:
			self.logger.info("Getting image from webcam %s" % self.webcam)
			image = self.webcam.get_image()
			resized_image = pygame.transform.scale(image, (surface.get_width(), surface.get_height()))

			pixel_array = pygame.surfarray.pixels3d(resized_image)
			#self.logger.info(pixel_array)
			for row,row_data in enumerate(pixel_array):
				for column,pixel_data in enumerate(row_data):
					surface.set_pixel(row, column, (pixel_data[0], pixel_data[1], pixel_data[2]))


		# Limit the frame rate.
		# This sleeps so that at least 25ms has passed since tick() 
		#  was last called. It is a no-op if the loop is running slow
		self.clock.tick(25)
		# Draw whatever this plugin does.
		# We need to return our decorated surface
		return surface

	def draw_splash(self,canvas):
		return self.draw_surface(canvas,0)

	# We've split the method that does the drawing out, so that draw_splash()
	#  can call it with a fixed timer
	def draw_surface(self, canvas, ticks):
		canvas.set_colour(FloorCanvas.BLUE)
		# Return the canvas
		return canvas

