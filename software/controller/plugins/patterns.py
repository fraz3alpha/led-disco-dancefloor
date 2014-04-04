__authors__ = ['Stew Francis']

import csv
import time
import math
import colorsys

from DDRPi import DDRPiPlugin
from lib.utils import ColourUtils

class Filter(object):
	
	def process(self, frame):
		raise NotImplementedError

class Pattern(object):
	def __init__(self, patternFile):
		with open(patternFile) as csvFile:
			reader = csv.reader(csvFile)
			patternMeta = reader.next()
			height = int(patternMeta[1])
			framesPerBeat = int(patternMeta[2])
			
			rows = list()
			
			for row in reader:
				#convert to float representation
				rows.append([hexToFloatTuple(colour) for colour in row])
				
		self.frames = [rows[i * height : (i+1) * height] for i in range(0, len(rows) / height)]
		self.beatsPerFrame = 1 / float(framesPerBeat)
	
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
			self.__currentFrame = Patterns.apply(self.__filters, self.__pattern.frames[self.__frameIndex])

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

def hexToFloatTuple(hexString):
	(r, g, b) = ColourUtils.hexToTuple(hexString)
	rf = r/float(255)
	gf = g/float(255)
	bf = b/float(255);
	return (rf, gf, bf)

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
		

class Patterns(DDRPiPlugin):

	def configure(self, config, image_surface):
		self.__surface = image_surface
		self.__beatService = BeatService()
		self.__patternIndex = -1
		self.__nextPatternTime = 0
		self.__patternDisplaySecs = 30
		
		self.__patterns = [
			[
				PatternFilter("plugins/nyan.csv", self.__beatService)
			],
			[
				PatternFilter("plugins/knightRider.csv", self.__beatService,
					[
						MotionBlurFilter(0.9)
					]),
				ColourFilter((1.0, 0.0, 1.0)),
				BeatHueAdjustmentFilter(self.__beatService, 0.2)
			],
			[
				PatternFilter("plugins/knightRider.csv", self.__beatService,
					[
						MotionBlurFilter(0.9)
					]),
				ColourFilter((1.0, 0.0, 0.0)),
				HueScroller()
			],
			[
				PatternFilter("plugins/knightRider.csv", self.__beatService,
					[
						MotionBlurFilter(0.9)
					]),
				ColourFilter((1.0, 0.0, 0.0)),
				BeatLightnessAdjustment(self.__beatService), #would like to apply this to the raw pattern before motion blur, but not pattern-specific
				HueScroller(),
			],
			[
				PatternFilter("plugins/matrix.csv", self.__beatService,
				[
					MotionBlurFilter(0.95)
				]),
				ColourFilter((0.0, 1.0, 0.0)),
				HueScroller()
			],
			[
				PatternFilter("plugins/explode.csv", self.__beatService,
				[
					MotionBlurFilter(0.9)
				]),
				ColourFilter((1.0, 0.0, 1.0)),
				BeatHueAdjustmentFilter(self.__beatService, 0.2)
			],
			[
				PatternFilter("plugins/explode2.csv", self.__beatService,
				[
					MotionBlurFilter(0.9)
				]),
				ColourFilter((0.0, 0.0, 1.0)),
				HueScroller()
			],
			[
				PatternFilter("plugins/explodeA.csv", self.__beatService,
				[
					MotionBlurFilter(0.9)
				]),
				ColourFilter((0.0, 0.0, 1.0)),
				HueScroller()
			],
			[
				PatternFilter("plugins/waveyWave.csv", self.__beatService),
				ColourFilter((0.0, 0.0, 1.0)),
				BeatHueAdjustmentFilter(self.__beatService, 0.2)
			],
			[
				PatternFilter("plugins/diamond.csv", self.__beatService, 
					[
						MotionBlurFilter(0.7)
					]),
				ColourFilter((1.0, 0.5, 0.5)),
				HueScroller()
			]
		]
	
	def display_preview(self):
		self.__blitFrame(Pattern("plugins/triForce.csv").frames[0])

	def start(self):
		pass

	def stop(self):
		pass

	def handle(self, event):
		pass
		
	def pause(self):
		pass
		
	def resume(self):
		pass

	def update_surface(self):
		frame = Patterns.apply(self.__getActivePattern(), list())
		self.__blitFrame(frame)
	
	def __blitFrame(self, frame):
		for y in range(0, self.__surface.height):
			row = frame[y]
			for x in range(0, self.__surface.width):
				self.__surface.draw_float_tuple_pixel(x, y, row[x])
		
		self.__surface.blit()
	
	@staticmethod
	def apply(filters, zero):
		return reduce(lambda x, y: y.process(x), filters, zero)
	
	def __getActivePattern(self):
		tim = time.time()
		if self.__nextPatternTime < tim:
			self.__patternIndex = (self.__patternIndex + 1) % len(self.__patterns)
			self.__nextPatternTime = tim + self.__patternDisplaySecs
		
		return self.__patterns[self.__patternIndex]
		
