
from VisualisationPlugin import VisualisationPlugin

import pygame
import logging 

from DDRPi import FloorCanvas

class LoveHeartVisualisationPlugin(VisualisationPlugin):

	logger = logging.getLogger(__name__)

	def __init__(self):
		self.clock = pygame.time.Clock()

	# Nothing specific to be done before this starts, although we could 
	#  set self.clock here. Stash any config so we can use it later
	def configure(self, config):
		self.config = config

		self.pulse_rate = 2000
		self.pulse_increasing = 1
		self.pulse_last_ratio = 0

		self.upper_name = ""
		self.lower_name = ""

		if config is not None:

			try:
				self.upper_name = "%s" % self.config["upper_name"]
			except (ValueError, KeyError):
				pass

			try:
				self.lower_name = "%s" % self.config["lower_name"]
			except (ValueError, KeyError):
				pass

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

		w = canvas.get_width()
		h = canvas.get_height()

		canvas.set_colour(FloorCanvas.BLACK)

		has_text = False
		if (self.upper_name is not None and self.upper_name != ""):
			self.draw_text(canvas, self.upper_name, 0, 0)	
			has_text = True
		if (self.lower_name is not None and self.lower_name != ""):
			self.draw_text(canvas, self.lower_name, 0, 11)	
			has_text = True

		# Drawing entirely black doesn't work very well, so draw a border
		#  if there are no names drawn
		if has_text is False:
			#Draw a border
			canvas.draw_line(0,0,0,h-1, FloorCanvas.WHITE)
			canvas.draw_line(0,h-1,w-1,h-1, FloorCanvas.WHITE)
			canvas.draw_line(w-1,h-1,w-1,0, FloorCanvas.WHITE)
			canvas.draw_line(w-1,0,0,0, FloorCanvas.WHITE)


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
		self.draw_heart(canvas, (red_value, 0x00, 0x00), w/2 -4, h/2 - 2, 1)
		# .. and a solid outline
		self.draw_heart(canvas, (0xFF, 0x00, 0x00), w/2 -4, h/2 - 2, 0)


		# Limit the frame rate.
		# This sleeps so that at least 25ms has passed since tick() 
		#  was last called. It is a no-op if the loop is running slow
		self.clock.tick(25)
		# Draw whatever this plugin does.
		# We need to return our decorated surface
		return canvas

	def draw_splash(self,canvas):

		canvas.set_colour(FloorCanvas.BLACK)

		# Draw a solid red heart in the middle (ish)
		canvas = self.draw_heart(canvas, (0xFF, 0x00, 0x00), canvas.get_width()//2 -4, canvas.get_height()//2 - 2, 1)
		return canvas

	def draw_heart(self, canvas, colour, x_pos, y_pos, fill):

		heart = (0x06, 0x09, 0x11, 0x22, 0x11, 0x09, 0x06);
		if (fill > 0):
			heart = (0x06, 0x0F, 0x1F, 0x3E, 0x1F, 0x0F, 0x06);
		heart_height = 6
		heart_width = len(heart)

		for x in range(0, heart_width):
			for y in range(0, heart_height):
				pixel_value = (heart[x] >> y) & 0x01
				if (pixel_value == 1):
					canvas.set_pixel(x+x_pos,y+y_pos, colour)

	def draw_text(self, canvas, text, x, y):

		if text == "Phil":
			self.draw_phil(canvas, x, y)
		elif text == "Naomi":
			self.draw_naomi(canvas, x, y)
		else:
			canvas.draw_text(self.upper_name, (0xFF,0xFF,0xFF), x, y)

		return canvas
		

	def draw_phil(self, canvas, x, y) :

		# To make it central
		offset = 4

		canvas.draw_text("P", (0xFF,0xFF,0xFF), x+offset, y)

		# Use the narrow i that we have to use for Naomi, and a h
		custom_text = {"h": (0x7F, 0x08, 0x04, 0x78, 0), "i": (0x7D, 0, 0, 0 ,0), "l": (0x7F, 0,0,0,0),}
		canvas.draw_text("h", (0xFF,0xFF,0xFF), x+offset+6, y, custom_text)
		canvas.draw_text("i", (0xFF,0xFF,0xFF), x+offset+11, y, custom_text)
		canvas.draw_text("l", (0xFF,0xFF,0xFF), x+offset+13, y, custom_text)

		return canvas
	
	def draw_naomi(self, canvas, x, y) :

		offset = 0
		canvas.draw_text("N", (0xFF,0xFF,0xFF), x+offset, y)

		# Hand craft a narrower a & o
		custom_text = {"o": (0x38, 0x44, 0x44, 0x38, 0x00), "a": (0x20, 0x54, 0x54, 0x78, 0x00), "i": (0x7D, 0, 0, 0 ,0)}
		canvas.draw_text("a", (0xFF,0xFF,0xFF), x+offset+6, y, custom_text)
		canvas.draw_text("o", (0xFF,0xFF,0xFF), x+offset+11, y, custom_text)
		canvas.draw_text("m", (0xFF,0xFF,0xFF), x+offset+16, y)
		canvas.draw_text("i", (0xFF,0xFF,0xFF), x+offset+22, y, custom_text)

		return canvas

