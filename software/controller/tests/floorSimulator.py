__authors__ = ['Joel Wright']

import io
import os
import pygame
import sys
import time
import yaml
import signal

lib_path = os.path.abspath('../lib')
sys.path.append(lib_path)

from layout import DisplayLayout

config_file = "config.yaml"

class FloorSimulator(object):
	def __init__(self, config_file):
		f = open(config_file)
		config = yaml.load(f)
		f.close()
		self.layout = DisplayLayout(config["modules"])
		self.dimensions = (height, width) = self.layout.calculate_floor_size()
		self.size = (height*20, width*20)
		self.pipe = open(config["system"]["pipe"])
		lm = self.layout.layout_mapping
		self.reverse_lm = self.__reverse_mapping__(lm)
		
	def start(self):
		pygame.init()
		clock = pygame.time.Clock()
		self.screen = pygame.display.set_mode(self.size)
		background = pygame.Surface(self.screen.get_size())
		self.background = background.convert()
		self.background.fill(pygame.Color(0,0,0))
		self.screen.blit(self.background, (0,0))
		pygame.display.flip()
		
		while True:
			line_read = False
			
			while not line_read:
				line = self.pipe.readline()

				if len(line) == 0:
										# Need to grab the pygame event list and clear it to avoid
					# lockups (we'll also update the display to handle desktop
					# changes)
					events = pygame.event.get()
					self.screen.blit(self.background, (0,0))
					pygame.display.update()
				else:
					line_read = True
			
			# Clear Surface
			self.background.fill(pygame.Color(0,0,0))
			
			# Process the input and draw the output
			pixels = self.__build_pixel_list__(line)
			
			# Draw the pixels
			self.__draw_pixels__(pixels)
			
			# Reset and start looking for input again
			line_read = False
			
			# Limit the frame rate
			clock.tick(100)
			
	def __build_pixel_list__(self, line):
		pixels = []
		
		(h,w) = self.dimensions
			
		index = 0
		p = 0
		while p < (h*w):
			r = line[index:index+6]
			g = line[index+6:index+12]
			b = line[index+12:index+18]
			index += 18
			p += 1
			pixels.append((ord(eval(r)),ord(eval(g)),ord(eval(b))))
			
		return pixels
		
	def __draw_pixels__(self, pixels):
		(h,w) = self.dimensions
		for i in range(0,len(self.reverse_lm)):
			(r,g,b) = pixels[i]
			c = pygame.Color(r,g,b)
			(x,y) = self.reverse_lm[i]
			r = pygame.Rect(x*20, y*20, 20, 20)
			pygame.draw.rect(self.background, c, r, 0)
		self.screen.blit(self.background, (0,0))
		pygame.display.update()
			
	def __reverse_mapping__(self, lm):
		pixel_coords = {}
		(w,h) = self.dimensions
		for x in range(0,w):
			for y in range(0,h):
				p = lm[x][y]
				if p is not None:
					pixel_coords[p] = (x,y)
		return pixel_coords

def interrupt_handler(signum, frame):
	print "Received SIGINT"
	sys.exit(1)
    
signal.signal(signal.SIGINT, interrupt_handler)

# Start the floor simulator
if __name__ == "__main__":
	simfloor = FloorSimulator(config_file)
	simfloor.start()
