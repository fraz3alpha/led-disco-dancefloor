
from VisualisationPlugin import VisualisationPlugin

import pygame
import logging
import colorsys
import math
import random

from DDRPi import FloorCanvas

class FireworksVisualisationPlugin(VisualisationPlugin):

	logger = logging.getLogger(__name__)

	def __init__(self):
		self.clock = pygame.time.Clock()

		self.fireworks = None

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

	def new_firework(self, colour=(0xFF,0,0), x=12, explode_height=8.0):

		firework = dict()
		firework["colour"] = colour
		firework["start_time"] = pygame.time.get_ticks()
		firework["explode_time"] = None
		firework["explode_radius"] = 3.0
		firework["explode_speed"] = 5.0
		firework["decay_speed"] = 4.0
		firework["x"] = x
		firework["target_height"] = explode_height
		firework["speed"] = 4.0
		firework["tail"] = 5.0
		# Options: LAUNCH, EXPLODE
		firework["mode"] = "LAUNCH"

		return firework

	def new_random_firework(self, limit_x, limit_y):

		firework_colours = [(0xFF,0,0),(0,0xFF,0),(0,0,0xFF),(0xFF,0xFF,0),(0,0xFF,0xFF),(0xFF,0,0xFF),(0xFF,0xFF,0xFF)]

		firework = dict()
		firework["colour"] = firework_colours[random.randint(0,len(firework_colours)-1)]
		firework["start_time"] = pygame.time.get_ticks()
		firework["explode_time"] = None
		firework["explode_radius"] = random.randint(20,70)/ 10.0
		firework["explode_speed"] = random.randint(30,50)/ 10.0
		firework["decay_speed"] = 4.0
		firework["x"] = random.randint(0,int(limit_x))
		firework["target_height"] = random.randint(4,int(limit_y))
		firework["speed"] = random.randint(50,80)/ 10.0
		firework["tail"] = random.randint(60,70)/ 10.0
		# Options: LAUNCH, EXPLODE, DEAD
		firework["mode"] = "LAUNCH"
		return firework
		

	def draw_frame(self, canvas):

		if self.fireworks is None:
			self.fireworks = []
			for i in range(10):
				self.fireworks.append(self.new_random_firework(canvas.get_width(), canvas.get_height()*0.8))

		# See if any fireworks have finished, and we need new ones
		for idx, firework in enumerate(self.fireworks):
			if firework["mode"] == "DEAD":
				self.fireworks[idx] = self.new_random_firework(canvas.get_width(), canvas.get_height())

		# Draw whatever this plugin does.
		canvas = self.draw_surface(canvas, self.fireworks, pygame.time.get_ticks())

		# Limit the frame rate.
		# This sleeps so that at least 25ms has passed since tick() 
		#  was last called. It is a no-op if the loop is running slow
		self.clock.tick(25)

		# We need to return our decorated surface
		return canvas

	def draw_splash(self,canvas):

		fireworks = []
		fireworks.append(self.new_firework())

		return self.draw_surface(canvas, fireworks, 0)

	# Normalization method, so the colors are in the range [0, 1]
	def normalize (self, color):
	    return color[0] / 255.0, color[1] / 255.0, color[2] / 255.0

	def reformat (self, colour):
		return int (round (colour[0] * 255))%256, \
			int (round (colour[1] * 255))%256, \
			int (round (colour[2] * 255))%256
 

	# We've split the method that does the drawing out, so that draw_splash()
	#  can call it with a fixed timer
	def draw_surface(self, canvas, fireworks, t):
		canvas.set_colour(FloorCanvas.BLACK)

		for firework in fireworks:

			theoretical_height = (t-firework["start_time"])/1000.0 * firework["speed"]

			if firework["mode"] == "LAUNCH":
				# Work out how high up the firework has got
				if theoretical_height >= firework["target_height"]:
					firework["mode"] = "EXPLODE"
					firework["explode_time"] = t
				current_height = theoretical_height
			else:
				current_height = firework["target_height"]
			# Draw the launching tail, which is an antialiased line, with 
			#  a gradient on it! :S
			# But if they just go straight, then it's less of a problem
			(x_quot, x_rem) = divmod(firework["x"], 1.0)
			(y_quot, y_rem) = divmod(current_height, 1.0)
			#self.logger.info("y quot:%f, mod:%f" % (y_quot, y_rem))
			(h,s,v) = colorsys.rgb_to_hsv(*self.normalize(firework["colour"]))
			# Draw the tail
			for y in range(int(y_quot)):
				# If it is a few blocks away, then tail the value off
				if y < (theoretical_height - 1):
					if y < theoretical_height -1 -firework["tail"]:
						pass
					else:
						tail_prop = (y - (theoretical_height - 1 - firework["tail"])) / float(firework["tail"])
						#self.logger.info("hsv input: %f,%f,%f" % (h,s,v))
						canvas.set_pixel(x_quot, y, (h,s,tail_prop * v), format="HSV")
			# If there is an extra bit left over
			if y_rem > 0.01:
				v_partial = v * y_rem
				#self.logger.info("Remainder: %f, v_partial: %f" % (y_rem, v_partial))
				canvas.set_pixel(x_quot, y_quot, (h,s,v_partial), format="HSV")

			if firework["mode"] == "LAUNCH":
				# Always Draw the brightest firework point
				canvas.set_pixel(x_quot, y_quot, (h,s,v), format="HSV")
			elif firework["mode"] == "EXPLODE":
				# Draw an increasing disc of light

				explode_x = firework["x"]
				explode_y = firework["target_height"]
	
				#
				t_since_explosion = (t - firework["explode_time"]) / 1000.0
				# Initial fast expansion
				if t_since_explosion < firework["explode_radius"] / firework["explode_speed"]:
					explosion_radius = t_since_explosion * firework["explode_speed"]
				# 4 times slower expansion whilst it is dying
				else :
					t_since_max_explosion = t_since_explosion - (firework["explode_radius"] / firework["explode_speed"])
					#self.logger.info("Time since max explosion: %f" % t_since_max_explosion)
					explosion_radius = firework["explode_radius"] + t_since_max_explosion * firework["explode_speed"] / 4.0

				decay_ratio = min(1.0, math.e ** -((t_since_explosion-2.0)/(1.0)))
				if decay_ratio < 0.01:
					firework["mode"] = "DEAD"

				for x in range(canvas.get_width()):
					for y in range(canvas.get_height()):
						# Calculate how far away from the centre of the blob the centre of this pixel is
						x_d = x - explode_x
						y_d = y - explode_y
						distance_away = math.sqrt(x_d * x_d + y_d * y_d)
	
						distance_decay_factor = 1.0	
						if explosion_radius >= 1:
							distance_decay_factor = 1.0 * (distance_away / explosion_radius)
		
						if distance_away < explosion_radius:
							self.merge_pixel(canvas, x, y, (h,s,v), decay_ratio * distance_decay_factor, "HSV")
#							canvas.set_pixel(x, y, (h,s,v * decay_ratio * distance_decay_factor), format="HSV")
						elif distance_away < explosion_radius + 1:
							(d_quot, d_rem) = divmod(distance_away - explosion_radius, 1.0)
							self.merge_pixel(canvas, x, y, (h,s,v), (1-d_rem) * decay_ratio * distance_decay_factor, "HSV")
#							canvas.set_pixel(x, y, (h,s,(1-d_rem) * decay_ratio * distance_decay_factor), format="HSV")


		# Return the canvas
		return canvas

	def merge_pixel(self, canvas, x, y, new_colour, alpha, format="RGB"):
		# When we set a pixel we see we have set the alpha channel to, and merge it wil the existing
		#  pixel
		current_pixel_rgb = canvas.get_pixel_tuple(x,y)
	
		# If HSV, make it RGB format
		if format == "HSV":
			new_colour = self.reformat(colorsys.hsv_to_rgb(*new_colour))

		new_r = current_pixel_rgb[0] * (1-alpha) + new_colour[0] * alpha
		new_g = current_pixel_rgb[1] * (1-alpha) + new_colour[1] * alpha
		new_b = current_pixel_rgb[2] * (1-alpha) + new_colour[2] * alpha

		canvas.set_pixel(x,y,(new_r, new_g, new_b))

		return canvas

