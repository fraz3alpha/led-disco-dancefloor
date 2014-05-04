
from VisualisationPlugin import VisualisationPlugin

# EQ code originally based on example here:
#  http://www.raspberrypi.org/forums/viewtopic.php?t=35838&p=454041

import pygame

from DDRPi import FloorCanvas
import logging
import math

import numpy
import threading
import pyaudio
import scipy
import scipy.fftpack
import scipy.io.wavfile
import wave


from lib.controllers import ControllerInput

class SoundToLightVisualisationPlugin(VisualisationPlugin):

	logger = logging.getLogger(__name__)

	def __init__(self):
		self.clock = pygame.time.Clock()
		self.logger.info("Initialising SoundToLightVisualisationPlugin")

		# Initialise the data structure
		self.max_retained_samples = 100
		self.fftsize = 512
		self.data=numpy.array(numpy.zeros((self.max_retained_samples,self.fftsize/2)),dtype=int)
	
		self.scrolling = False
		
		self.modes = ["SCROLLING", "LATEST"]
		self.mode = self.modes[1]

		t_rec=threading.Thread(target=self.record) # make thread for record()
		t_rec.daemon=True # daemon mode forces thread to quit with program
		t_rec.start() #launch thread

	def configure(self, config):
		self.config = config
		self.logger.info("Config: %s" % config)

	"""
	Handle the pygame event sent to the plugin from the main loop
	"""
	def handle_event(self, e):

		if (e.type == pygame.JOYBUTTONDOWN):
			if e.button == ControllerInput.BUTTON_A:
				if len(self.modes) > 0:
					self.mode = self.modes[0]
				return None
			if e.button == ControllerInput.BUTTON_B:
				if len(self.modes) > 1:
					self.mode = self.modes[1]
				return None

		return e

	def draw_frame(self, canvas):

		canvas = self.draw_surface(canvas, pygame.time.get_ticks())
		# Limit the frame rate.
		# This sleeps so that at least 25ms has passed since tick() 
		#  was last called. It is a no-op if the loop is running slow
		# Draw whatever this plugin does
		return canvas

	def draw_splash(self, canvas):
		canvas.set_colour((0,0,0))
		w = canvas.get_width()
		h = canvas.get_height()
		# Draw something that looks vaguely like a EQ
		for x in range(w):
			# Two humps
			height = h * 0.75 * math.cos(math.pi * float(x) / w) ** 2
			# Decrease the humps
			height *= math.cos((math.pi/2.0) * float(x) / w)
			canvas.draw_line(x,h, x,(h-1)-int(height), (0xFF,0,0))


		return canvas

	def draw_surface(self,canvas):
		return self.draw_surface(canvas, 0)

	def draw_surface(self, canvas, t):
		canvas.set_colour((0,0,0))

		if self.data is not None:
			if self.mode == "SCROLLING":

				for x in range(canvas.get_width()):
					# Skip a sample if it there isn't enough data available
					if x >= len(self.data):
						continue
					latest = self.data[-x]
					new_data = []
					for i in range(len(latest)):
						new_data.append(latest[i])

					# Average the array into chunks to get n blocks
					blocks = canvas.get_height()
					elements_per_block = len(new_data)//blocks
					for block in range(blocks):
						# Calculate the average for the block
						cumulative = 0
						count = 0
						for element in range(elements_per_block):
							index = block * elements_per_block + element
							cumulative += new_data[index]
							count += 1
						average = cumulative / count
						# Coerce the values into a good range
						max_value = 255
						scale = 1.0
						average *= scale
						if average > max_value: average = max_value
						if average < 0: average = 0

						canvas.set_pixel(canvas.get_width() - x, block, (int(average), 0, 0))

			elif self.mode == "LATEST":
				latest = self.data[-1]
				new_data = []
				for i in range(len(latest)):
					new_data.append(latest[i])

				# Average the array into chunks to get n blocks
				blocks = canvas.get_width()
				elements_per_block = len(new_data)//blocks
				for block in range(blocks):
					# Calculate the average for the block
					cumulative = 0
					count = 0
					for element in range(elements_per_block):
						index = block * elements_per_block + element
						cumulative += new_data[index]
						count += 1
					average = float(cumulative) / float(count)
					# Coerce the values into a good range
					max_value = 255
					scale = 1.0
					average *= scale
					if average > max_value: average = max_value
					if average < 0: average = 0

					height = canvas.get_height() * average / max_value
					height_int = int(height)
					for y in range(height_int):
						canvas.set_pixel(canvas.get_width() - block, canvas.get_height() - y, (0xFF, 0, 0))
			

			print "MIN:\t%s\tMAX:\t%s"%(min(self.data[-1]),max(self.data[-1]))

		self.clock.tick(25)
		return canvas

	def record(self):

		# Based off code from:
		#  http://www.swharden.com/blog/2010-06-19-simple-python-spectrograph-with-pygame/

		rate=12000 #try 5000 for HD data, 48000 for realtime
		overlap=5 #1 for raw, realtime - 8 or 16 for high-definition

		self.logger.info("Opening Audio Stream")
		p = pyaudio.PyAudio() 
		inStream = p.open(format=pyaudio.paInt16,channels=1,rate=rate,input=True)
		linear=[0]*self.fftsize
		while True:
			#self.logger.info("Initiating Audio Stream Read")
			linear=linear[self.fftsize/overlap:]
			pcm=numpy.fromstring(inStream.read(self.fftsize/overlap), dtype=numpy.int16)
			linear=numpy.append(linear,pcm)

			# Convert the PCM wave format to FFT
			ffty=scipy.fftpack.fft(linear)
			ffty=abs(ffty[0:len(ffty)/2])/500 #FFT is mirror-imaged
			#print "MIN:\t%s\tMAX:\t%s"%(min(ffty),max(ffty))

			# First shift all the data to the left
			self.data=numpy.roll(self.data,-1,0)
			# Make the last column equal to the new data
			self.data[-1]=ffty[::-1]

