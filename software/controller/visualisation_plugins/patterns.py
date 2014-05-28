__authors__ = ['Stew Francis']

import csv
import time
import math
import colorsys
import pygame
import os

from DDRPi import FloorCanvas

from VisualisationPlugin import VisualisationPlugin

#from DDRPi import DDRPiPlugin
#from lib.utils import ColourUtils

import logging

class Filter(object):
	
	def process(self, frame):
		raise NotImplementedError

class Pattern(object):

	logger = logging.getLogger(__name__)

	def __init__(self, patternFile):
		#self.logger.info("Loading %s" % patternFile)
		with open(patternFile) as csvFile:
			reader = csv.reader(csvFile)
			patternMeta = next(reader)
			height = int(patternMeta[1])
			framesPerBeat = int(patternMeta[2])
			
			rows = list()
			
			for row in reader:
				#convert to float representation
				rows.append([hexToFloatTuple(colour) for colour in row])
				
		self.frames = [rows[i * height : (i+1) * height] for i in range(0, len(rows) // height)]
		self.beatsPerFrame = 1 / float(framesPerBeat)
	
# This is just the way that the frames are combined.
class PatternFilter(Filter):
	
	def __init__(self, patternFile, beatService, filters = []):
		self.__frameIndex = 0
		self.frameTime = 0
		self.__beatService = beatService
		self.__pattern = Pattern(patternFile)
		self.__filters = filters
		self.__currentFrame = None
	
	def process(self, frame):
		if self.__requiresNewFrame():
			self.__frameIndex = (self.__frameIndex + 1) % len(self.__pattern.frames)
			self.__currentFrame = PatternsVisualisationPlugin.apply(self.__filters, self.__pattern.frames[self.__frameIndex])

		return self.__currentFrame
	
	def __requiresNewFrame(self):
		#calculate whether or not we need to advance the frame index
		tim = time.time()
		if tim > self.frameTime:
			# calculate the time of the next frame
			self.frameTime = self.__beatService.getTimeOfNextBeatInterval(self.__pattern.beatsPerFrame)
			return True
		else:
			return False

def hexToTuple(hex_colour):
	"""
	Convert hex #RRGGBB to an (R, G, B) tuple
	"""
	hex_colour = hex_colour.strip()
	if hex_colour[0] == '#':
		hex_colour = hex_colour[1:]
	if len(hex_colour) != 6:
		raise ValueError("input #%s is not in #RRGGBB format" % hex_colour)
	(rs,gs,bs) = hex_colour[:2], hex_colour[2:4], hex_colour[4:]
	r = int(rs, 16)
	g = int(gs, 16)
	b = int(bs, 16)
	return (r,g,b)

def hexToFloatTuple(hexString):
	(r, g, b) = hexToTuple(hexString)
	rf = r/float(255)
	gf = g/float(255)
	bf = b/float(255);
	return (rf, gf, bf)

# Motion blur is applied to multiple frames (how many)

class MotionBlurFilter(Filter):
	
	def __init__(self, decayFactor):
		self.__decayFactor = decayFactor;
		self.__currentFrame = None
		
	def process(self, frame):
		self.__currentFrame = self.__decay(self.__currentFrame)
		self.__currentFrame = self.__overlay(frame, self.__currentFrame)
		return self.__currentFrame
	
	def __decay(self, frame):
		if self.__currentFrame == None: return None
		return [[MotionBlurFilter.__applyDecay(self.__decayFactor, rgb) for rgb in row] for row in frame]
	
	def __overlay(self, topFrame, bottomFrame):
		if bottomFrame == None: return topFrame
		frameOfPairedRows = zip(topFrame, bottomFrame)
		return [[self.__blend(pair[0], pair[1]) for pair in zip(rowPairs[0], rowPairs[1])] for rowPairs in frameOfPairedRows]

	@staticmethod
	def __blend(rgb1, rgb2):
		return (max(rgb1[0], rgb2[0]), max(rgb1[1], rgb2[1]), max(rgb1[2], rgb2[2]))
	
	@staticmethod
	def __applyDecay(decayFactor, rgb):
		(r, g, b) = rgb
		(h, l, s) = colorsys.rgb_to_hls(r, g, b);
		l *= decayFactor
		return colorsys.hls_to_rgb(h, l, s)
	
class HueScroller(Filter):
	
	def __init__(self):
		self.__lastAdjustment = 0.0
		
			
	def process(self, frame):
		self.__lastAdjustment = (self.__lastAdjustment + 0.01) % 1 + 1 % 1
		return [[BeatHueAdjustmentFilter.adjustHue(self.__lastAdjustment, rgb) for rgb in row] for row in frame]
		

class ColourFilter(Filter):
	
	def __init__(self, rgb):
		self.rgb = rgb
		
	def process(self, frame):
		#for each cell, apply the rgb filter
		return [[(self.rgb[0] * rgb[0], self.rgb[1] * rgb[1], self.rgb[2] * rgb[2]) for rgb in row] for row in frame]
	
class BeatLightnessAdjustment(Filter):
	
	def __init__(self, beatService):
		self.__beatService = beatService
		self.__lightnessAdjustment = 0.1
		
	def process(self, frame):
		x = self.__beatService.getBeatPosition()
		if x < 0.5:
			x *= 2
		else:
			x = 2 * (x - 1)
		
		#calculate how much we need to add to the hue, based on beat position
		frameAdjustment = self.__lightnessAdjustment / (math.e ** ((5*x) ** 2))
		#for each cell, apply the hue adjustment
		return [[BeatLightnessAdjustment.adjustLightness(frameAdjustment, rgb) for rgb in row] for row in frame]
	
	@staticmethod
	def adjustLightness(adjustment, rgb):
		(r, g, b) = rgb
		(h, l, s) = colorsys.rgb_to_hls(r, g, b);
		# inc and wrap h
		l = ((l + adjustment) % 1 + 1 % 1)
		return colorsys.hls_to_rgb(h, l, s)
		
class BeatHueAdjustmentFilter(Filter):
	
	def __init__(self, beatService, hueAdjustment):
		self.__beatService = beatService
		self.hueAdjustment = hueAdjustment
	
	def process(self, frame):		
		# beat position 0 -> 1, adjust to vary from function varies from -1 ->
		# 0-0.5 -> 0-1
		# 0.5-1 -> -1-0
		x = self.__beatService.getBeatPosition()
		if x < 0.5:
			x *= 2
		else:
			x = 2 * (x - 1)
		
		#calculate how much we need to add to the hue, based on beat position
		frameHueAdjustment = self.hueAdjustment / (math.e ** ((5*x) ** 2))
		
		#for each cell, apply the hue adjustment
		return [[BeatHueAdjustmentFilter.adjustHue(frameHueAdjustment, rgb) for rgb in row] for row in frame]
	
	@staticmethod
	def adjustHue(adjustment, rgb):
		(r, g, b) = rgb
		(h, l, s) = colorsys.rgb_to_hls(r, g, b);
		# inc and wrap h
		h = ((h + adjustment) % 1 + 1 % 1)
		return colorsys.hls_to_rgb(h, l, s)
		
	
# This just seems to be a way to keep track of time	
class BeatService(object):
	
	def __init__(self):
		self.beatLength = 0.75
		self.lastBeatTime = time.time()
	
	def getTimeOfNextBeatInterval(self, beatInterval):
		intervalLength = self.beatLength * beatInterval
		tim = time.time()
		
		# calculate the next beat interval of beatInterval
		intervalTime = self.__getLastBeatTime(tim)
		while intervalTime < tim:
			intervalTime += intervalLength
		return intervalTime
	
	def getBeatPosition(self):
		tim = time.time()
		return (tim - self.__getLastBeatTime(tim)) / self.beatLength
		
	def __getLastBeatTime(self, tim):
		while self.lastBeatTime + self.beatLength < tim:
			self.lastBeatTime += self.beatLength
		return self.lastBeatTime
		

class PatternsVisualisationPlugin(VisualisationPlugin):

	def __init__(self):
		self.clock = pygame.time.Clock()

		# All the patterns live in a directory, so set the default
		#  here and store it so that we can fetch things from it
		DEFAULT_PLUGIN_RESOURCE_DIRECTORY = "patterns"
		script_directory = os.path.dirname(os.path.realpath(__file__))
		self.plugin_resource_directory = os.path.join(script_directory, DEFAULT_PLUGIN_RESOURCE_DIRECTORY)

	def add_to_pattern_repo(self, name, pattern_file, beat_service, filters=None, other_args=[]):

		# Check that the file exists
		if not os.path.isfile(pattern_file):
			self.logger.warn("Unable to create %s pattern, no such file: %s" % (name, pattern_file))
			return

		if filters == None:
			pattern_filter = PatternFilter(pattern_file, beat_service)
		else:
			pattern_filter = PatternFilter(pattern_file, beat_service, filters)

		pattern_def = [pattern_filter]
		for arg in other_args:
			pattern_def.append(arg)

		self.__pattern_repo[name] = pattern_def
	
		self.logger.info("Added pattern %s" % name)

		return pattern_def
			

	def add_pattern(self, name):
		self.logger.info("Searching for requested pattern: %s" % name)
		if name in self.__pattern_repo:
			self.logger.info("Adding pattern: %s" % name)
			self.__patterns.append(self.__pattern_repo[name])
		else:
			self.logger.warn("Unable to find pattern: %s" % name)

	def configure(self, config):
		self.config = config
		self.__beatService = BeatService()
		self.__patternIndex = -1
		self.__nextPatternTime = 0
		self.__patternDisplaySecs = 10

		self.__pattern_repo = {}

		# Nyan cat: A loop of the cat scrolling through space
		self.add_to_pattern_repo("Nyan Cat", os.path.join(self.plugin_resource_directory, "nyan.csv"), self.__beatService)

		# Knight Rider: A scanning bar going from left to right and back again, 
		#  with a blur, and a changing colour
		self.add_to_pattern_repo("Knight Rider", os.path.join(self.plugin_resource_directory, "knightRider.csv"), self.__beatService, 
				[
					MotionBlurFilter(0.9)
				], 
				[ColourFilter((1.0, 0.0, 1.0)),	BeatHueAdjustmentFilter(self.__beatService, 0.2)])

		self.add_to_pattern_repo("Explode A.1", os.path.join(self.plugin_resource_directory, "explodeA.csv"), self.__beatService,
				[
					MotionBlurFilter(0.9)
				],
				[ColourFilter((0.0, 0.0, 1.0)),	HueScroller()])

		self.add_to_pattern_repo("Matrix", os.path.join(self.plugin_resource_directory, "matrix.csv"), self.__beatService,
				[
					MotionBlurFilter(0.95)
				],
				[ColourFilter((0.0, 1.0, 0.0)),	HueScroller()])


		self.add_to_pattern_repo("Knight Rider 2", os.path.join(self.plugin_resource_directory, "knightRider.csv"), self.__beatService,
				[
					MotionBlurFilter(0.9)
				],
				[ColourFilter((1.0, 0.0, 0.0)),	HueScroller()])
			
		self.add_to_pattern_repo("Matrix 2", os.path.join(self.plugin_resource_directory, "matrix.csv"), self.__beatService,
				[
					MotionBlurFilter(0.95)
				],
				[ColourFilter((0.0, 1.0, 0.0)),	HueScroller()])

		self.add_to_pattern_repo("Explode 0.1", os.path.join(self.plugin_resource_directory, "explode.csv"), self.__beatService,
				[
					MotionBlurFilter(0.9)
				],
				[ColourFilter((1.0, 0.0, 1.0)),	BeatHueAdjustmentFilter(self.__beatService, 0.2)])

		self.add_to_pattern_repo("Explode 2.1", os.path.join(self.plugin_resource_directory, "explode2.csv"), self.__beatService,
				[
					MotionBlurFilter(0.9)
				],
				[ColourFilter((0.0, 0.0, 1.0)),	HueScroller()])


		self.add_to_pattern_repo("Wavey Wave", os.path.join(self.plugin_resource_directory, "waveyWave.csv"), self.__beatService,
				None,
				[ColourFilter((0.0, 0.0, 1.0)),	BeatHueAdjustmentFilter(self.__beatService, 0.2)])

		self.add_to_pattern_repo("Diamond", os.path.join(self.plugin_resource_directory, "diamond.csv"), self.__beatService,
				[
					MotionBlurFilter(0.7)
				],
				[ColourFilter((1.0, 0.5, 0.5)),	HueScroller()])
		
		self.__patterns = []

		if self.config is not None:
			self.logger.info("Config is not none")
			patterns = None
			
			if "patterns" in self.config:
				for pattern in self.config["patterns"]:
					self.add_pattern(pattern)

		else:
			self.logger.info("Config was none, what should I do?")
		
		if len(self.__patterns) == 0:
			self.logger.info("Adding default patterns")

			self.add_pattern("Nyan Cat")
			self.add_pattern("Knight Rider")
			self.add_pattern("Knight Rider 2")
			self.add_pattern("Diamond")
			self.add_pattern("waveyWave")
			self.add_pattern("Explode A.1")
			self.add_pattern("Explode A.2")
			self.add_pattern("Explode 0.1")
			self.add_pattern("Explode 2.1")

		
		return

	# Interface Methods

	def draw_frame(self, canvas):
		self.clock.tick(50)
		frame = PatternsVisualisationPlugin.apply(self.__getActivePattern(), list())

		for y in range(0, canvas.get_height()):
			row = frame[y]
			for x in range(0, canvas.get_width()):
				canvas.set_float_pixel_tuple(x, y, row[x])
		return canvas
	
	# End of Interface Methods

#	def display_preview(self):
#		self.__blitFrame(Pattern("plugins/triForce.csv").frames[0])
#
#	def start(self):
#		pass
#
#	def stop(self):
#		pass
#
#	def handle(self, event):
#		pass
#		
#	def pause(self):
#		pass
#		
#	def resume(self):
#		pass

	def update_surface(self):
		frame = Patterns.apply(self.__getActivePattern(), list())
		self.__blitFrame(frame)

#	def __blitFrame(self, frame):
#		for y in range(0, self.__surface.height):
#			row = frame[y]
#			for x in range(0, self.__surface.width):
#				self.__surface.draw_float_tuple_pixel(x, y, row[x])
#		
#		self.__surface.blit()
	
	@staticmethod
	def apply(filters, zero):
	
		result = zero
		for new_filter in filters:
			result = new_filter.process(result)
		return result
		#return reduce(lambda x, y: y.process(x), filters, zero)
	
	def __getActivePattern(self):
		tim = time.time()
		if len(self.__patterns) == 0:
			self.logger.warn("No patterns!")
			return None

		if len(self.__patterns) == 1:
			self.__patternIndex = 0
			return self.__patterns[0]

		if self.__nextPatternTime < tim:
			self.__patternIndex = (self.__patternIndex + 1) % len(self.__patterns)
			self.logger.info("Switching to pattern #%d" % self.__patternIndex)
			self.__nextPatternTime = tim + self.__patternDisplaySecs
		
		return self.__patterns[self.__patternIndex]
		
