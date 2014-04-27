__authors__ = ['Andrew Taylor']

from logging import Logger

class FloorCanvas(object):
	# The floor canvas is a large array which we can draw on to
	# It provides a number of  methods that you would expect for 
	#  a canvas object, including shapes, painting pixels etc..

	# Some colour constants
	# You can get at them using e.g. FloorCanvas.BLACK
	BLACK = 0x000000
	WHITE = 0xFFFFFF
	RED   = 0xFF0000
	GREEN = 0x00FF00
	BLUE  = 0x0000FF

	# Constructor to set up the size and initial colour
	def __init__(self, width=0, height=0, colour=BLACK):
		self.width = 0
		if (width > 0):
			self.width = width
		self.height = 0
		if (height > 0):
			self.height = height
		Logger.info("FloorCanvas", "Creating a canvas with width=%d, height=%d" % (width, height))
		# Create the two dimensional array for the canvas object
		self.data = [[self.BLACK for y in range(height)] for x in range(width)]

	# Return an array data[x][y] of the canvas. This may or may not be
	#  the same as the internal representation, so don't get it directly,
	#  call this method instead
	def get_canvas_array(self):
		return self.data

	# See if the given pixel is on the canvas, and not off the side somewhere
	def is_in_range(self, x, y):
		if x >= self.width:
			return False
		if y >= self.height:
			return False
		return True

	# Get the size of the canvas
	def get_width(self):
		return self.width

	def get_height(self):
		return self.height

	def get_size(self):
		return (self.width, self.height)

	# Set a pixel with an int value
	def set_pixel(self, x, y, colour):
		if self.is_in_range(x,y):
			self.data[x][y] = colour

	# Set a pixel with an tuple value
	def set_pixel_tuple(self, x, y, colour):
		if self.is_in_range(x,y):
			self.data[x][y] = self.pack_colour_tuple(colour)

	# Set a pixel with a float tuple value
	def set_float_pixel_tuple(self, x, y, colour):
		"""
		Set the value of the pixel at (x,y) to colour((r,g,b)) where r g and b are floats
		"""
		(floatR, floatG, floatB) = colour
		intR = int(floatR*255)
		intG = int(floatG*255)
		intB = int(floatB*255)
		self.set_pixel_tuple(x, y, (intR, intG, intB))

	# Return the colour as an int (i.e the value of 0xRRGGBB)
	def get_pixel(self, x, y):
		if self.is_in_range(x,y):
			return self.data[x][y]
		return None

	# Return the colour as (R,G,B) tuple
	def get_pixel_tuple(self, x, y):
		return self.unpack_colour_tuple(self.get_pixel(x,y))

	def unpack_colour_tuple(self, colour):
		if colour < 0:
			return (0,0,0)
		red   = (colour >> 16) & 0xFF
		green = (colour >> 8) & 0xFF
		blue  =  colour        & 0xFF
		return (red,green,blue)

	def pack_colour_tuple(self, colour):
		(red, green, blue) = colour
		value = (red << 16) + (green << 8) + blue
		return value

	def draw_line(self, from_x, from_y, to_x, to_y, colour, aliasing=None):
		# Work out which direction has the most pixels
		#  so that there are no gaps in the line
		if (from_x == to_x and from_y == to_y):
			self.set_pixel(int(from_x), int(from_y))
			return None
		#Logger.verbose("FloorCanvas", "(%d,%d) > (%d,%d)" % (from_x, from_y, to_x, to_y))
		if (abs(from_x - to_x) > abs(from_y - to_y)):
			# Make sure that to_x is >= from_x so that the range()
			#  works properly
			if to_x < from_x:
				temp = to_x
				to_x = from_x
				from_x = temp

				temp = to_y
				to_y = from_y
				from_y = temp
			#Logger.verbose("FloorCanvas", "Going from x=%d to x=%d" % (from_x, to_x))
			gradient = float(to_y - from_y) / float(to_x - from_x)
			#Logger.verbose("FloorCanvas", "Gradient=%f, c=%d" % (gradient, from_y))
			for x in range(to_x - from_x + 1):
				y = gradient * float(x) + from_y
				self.set_pixel(int(x + from_x), int(y), colour)
		else:
			# Make sure that to_y is >= from_y so that the range()
			#  works properly
			if to_y < from_y:
				temp = to_x
				to_x = from_x
				from_x = temp

				temp = to_y
				to_y = from_y
				from_y = temp
			#Logger.verbose("FloorCanvas", "Going from y=%d to y=%d" % (from_y, to_y))
			gradient = float(to_x - from_x) / float(to_y - from_y)
			for y in range(to_y - from_y + 1):
				x = gradient * float(y) + from_x
				self.set_pixel(int(x), int(y+from_y), colour)

	# Set the entire canvas to a single colour
	def set_colour(self, colour):
		for x in range(self.width):
			for y in range(self.height):
				self.data[x][y] = colour


