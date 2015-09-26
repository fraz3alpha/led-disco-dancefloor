from VisualisationPlugin import VisualisationPlugin

import pygame

from DDRPi import FloorCanvas
import logging
import math
import colorsys

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
        self.data = numpy.array(numpy.zeros((self.max_retained_samples, self.fftsize / 2)), dtype=int)

        self.scrolling = False

        self.modes = ["scrolling", "latest"]
        self.mode = self.modes[1]

        self.chunk_policies = ["linear", "exp"]
        self.chunk_policy = self.chunk_policies[1]

        self.rolling_max = [0 for i in range(100)]
        self.rolling_max_position = 0;

    def start(self):

        t_rec = threading.Thread(target=self.record)  # make thread for record()
        t_rec.daemon = True  # daemon mode forces thread to quit with program
        t_rec.start()  # launch thread


    def configure(self, config):
        self.config = config

        # Set the mode to the requested value, if present
        try:
            mode = self.config["mode"]
            if mode.lower() in self.modes:
                self.mode = mode.lower()
        except (AttributeError, ValueError, KeyError):
            pass

        # Set the binning algorithm to the requested one, if present
        try:
            policy = self.config["policy"]
            if policy.lower() in self.chunk_policies:
                self.chunk_policy = policy.lower()
        except (AttributeError, ValueError, KeyError):
            pass

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

            if e.button == ControllerInput.BUTTON_X:
                if len(self.chunk_policies) > 0:
                    self.chunk_policy = self.chunk_policies[0]
                return None
            if e.button == ControllerInput.BUTTON_Y:
                if len(self.chunk_policies) > 1:
                    self.chunk_policy = self.chunk_policies[1]
                return None

        return e

    def draw_frame(self, canvas):

        canvas = self.draw_surface(canvas, pygame.time.get_ticks())
        # Limit the frame rate.
        # This sleeps so that at least 25ms has passed since tick()
        # was last called. It is a no-op if the loop is running slow
        # Draw whatever this plugin does
        return canvas

    def draw_splash(self, canvas):
        canvas.set_colour((0, 0, 0))
        w = canvas.get_width()
        h = canvas.get_height()
        # Draw something that looks vaguely like a EQ
        for x in range(w):
            # Two humps
            height = h * 0.75 * math.cos(math.pi * float(x) / w) ** 2
            # Decrease the humps
            height *= math.cos((math.pi / 2.0) * float(x) / w)
            canvas.draw_line(x, h, x, (h - 1) - int(height), (0xFF, 0, 0))

        return canvas

    def draw_surface(self, canvas):
        return self.draw_surface(canvas, 0)

    def draw_surface(self, canvas, t):
        canvas.set_colour((0, 0, 0))

        if self.data is not None:

            max_average = max(255, int(sum(self.rolling_max) / len(self.rolling_max)))
            block_values = []

            if self.mode == "scrolling":

                for x in range(canvas.get_width()):
                    # Skip a sample if it there isn't enough data available
                    if x >= len(self.data):
                        continue
                    latest = self.data[-x]

                    number_of_chunks = canvas.get_height()
                    # Make a copy of the array and reverse it -
                    # thus making the lowest frequency bin at [0] (traditionally left)
                    new_data = latest[::-1]
                    #self.logger.info("Input data %s" % new_data)
                    # Split it down into chunks, which is how wide the floor is.
                    # Using an exponential function helps approximate notes a bit better
                    #  where all the lower ones are closely spaced, but the higher ones
                    #  are further apart
                    new_data = self.chunk_data(new_data, canvas.get_height(), self.chunk_policy)
                    #self.logger.info("Chunked data: %s" % new_data)
                    peak_value = max(max(new_data), 50)
                    #self.logger.info("Peak value: %s" % peak_value)

                    # Store the rolling max
                    self.rolling_max[self.rolling_max_position] = peak_value
                    self.rolling_max_position += 1
                    if self.rolling_max_position >= len(self.rolling_max): self.rolling_max_position = 0

                    # Two options, either max, or mean
                    #standard_peak_value = max(max(self.rolling_max), 50) / 2
                    standard_peak_value = max(int(numpy.mean(self.rolling_max)), 255)

                    # Scale everything to the peak value to be in the range [0,1]
                    scaled_data = []
                    for i in range(number_of_chunks):
                        scaled_data.append(new_data[i] / float(standard_peak_value))

                    for y in range(number_of_chunks):
                        scaled_value = min(255, int(255 * scaled_data[y]))
                        canvas.set_pixel(x, y, (scaled_value, scaled_value, scaled_value))

            elif self.mode == "latest":
                latest = self.data[-1]

                number_of_chunks = canvas.get_width()
                # Make a copy of the array and reverse it -
                # thus making the lowest frequency bin at [0] (traditionally left)
                new_data = self.data[-1][::-1]
                #self.logger.info("Input data %s" % new_data)
                # Split it down into chunks, which is how wide the floor is.
                # Using an exponential function helps approximate notes a bit better
                #  where all the lower ones are closely spaced, but the higher ones
                #  are further apart
                new_data = self.chunk_data(new_data, canvas.get_width(), self.chunk_policy)
                #self.logger.info("Chunked data: %s" % new_data)
                peak_value = max(max(new_data), 50)
                #self.logger.info("Peak value: %s" % peak_value)

                # Store the rolling max
                self.rolling_max[self.rolling_max_position] = peak_value
                self.rolling_max_position += 1
                if self.rolling_max_position >= len(self.rolling_max): self.rolling_max_position = 0

                # Two options, either max, or mean
                #standard_peak_value = max(max(self.rolling_max), 50) / 2
                standard_peak_value = max(int(numpy.mean(self.rolling_max)), 50)

                # Scale everything to the peak value
                scaled_data = []
                for i in range(number_of_chunks):
                    scaled_data.append(new_data[i] / float(standard_peak_value))

                for column in range(canvas.get_width()):
                    height_int = int(canvas.get_height() * scaled_data[column])
                    for y in range(height_int):
                        canvas.set_pixel(column, canvas.get_height() - y,
                                         (0xFF, max(0xFF - int(1.5 * y * (256. / (max(height_int, 1)))), 0), 0))
                    #self.draw_flame_to(canvas, column, 0, height_int)

        self.clock.tick(25)
        return canvas

    def chunk_data(self, data, number_of_chunks, scaling="linear"):

        chunks = []

        if scaling == "linear":

            elements_per_block = len(data) // number_of_chunks

            for i in range(number_of_chunks):
                count = 0;
                total = 0
                for x in range(elements_per_block):
                    count += 1
                    total += data[x + i * elements_per_block]
                if count > 0:
                    chunks.append(total // count)

        elif scaling == "exp":

            # The lower frequencies are more closely packed, so don't
            # evenly split the chunks, instead spread the lower frequencies
            #  out more following a rough exponential type curve

            #self.logger.info("length of input - %d" % len(data))

            # Calculate the distribution along the exponential
            elements_per_block = [0 for i in range(number_of_chunks)]
            e = 1.5
            m = 0.5
            for x in range(number_of_chunks):
                elements_per_block[x] = e ** (x * m)

            #self.logger.info("Exponential chunks: %s" % elements_per_block)
            #self.logger.info("Exponential chunk total: %d" % sum(elements_per_block))

            # Scale up so the total number of buckets is about the total
            #  we have to spread out
            multiplier = len(data) / sum(elements_per_block)
            for x in range(number_of_chunks):
                elements_per_block[x] = max(1, int(multiplier * elements_per_block[x]))

            #self.logger.info("Exponential chunks normalised: %s" % elements_per_block)
            #self.logger.info("Exponential chunk total: %d" % sum(elements_per_block))

            # Don't include the DC term
            #elements_per_block[0] = 0

            # Add the required number to each bucket and calculate the average
            count = 0
            for i in range(number_of_chunks):
                elements = 0
                total = 0
                #self.logger.info("Putting %d elements in block %d" % (elements_per_block[i], i))
                for j in range(elements_per_block[i]):
                    elements += 1
                    if count < len(data):
                        total += data[count]
                    #self.logger.info("  %s" % data[count])

                    count += 1

                if elements > 0:
                    chunks.append(total // elements)
                else:
                    chunks.append(0)


                #self.logger.info("Exp chunk data: %s" % chunks)

        return chunks;

    def draw_flame_to(self, canvas, column, from_row, to_row):
        delta = int(abs(to_row - from_row))
        # self.logger.info("Flame height %d, %d" % (column, delta))
        for row in range(delta):
            canvas.set_pixel(column, from_row + row,
                             (0xFF, max(0xFF - int(1.5 * row * (256. / (max(delta, 1)))), 0), 0))
        #canvas.set_pixel(column, from_row + row, (0xFF,0,0))

        return None

    # Reformats a color tuple, that uses the range [0, 1] to a 0xFF
    # representation.
    def reformat(self, color):
        return int(round(color[0] * 255)), \
               int(round(color[1] * 255)), \
               int(round(color[2] * 255))

    def record(self):

        # Based off code from:
        # http://www.swharden.com/blog/2010-06-19-simple-python-spectrograph-with-pygame/

        rate = 12000  #try 5000 for HD data, 48000 for realtime
        overlap = 5  #1 for raw, realtime - 8 or 16 for high-definition

        self.logger.info("Opening Audio Stream")
        p = pyaudio.PyAudio()
        inStream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True)
        linear = [0] * self.fftsize
        while True:
            #self.logger.info("Initiating Audio Stream Read")
            linear = linear[self.fftsize / overlap:]
            pcm = numpy.fromstring(inStream.read(self.fftsize / overlap), dtype=numpy.int16)
            linear = numpy.append(linear, pcm)

            # Convert the PCM wave format to FFT
            ffty = scipy.fftpack.fft(linear)
            ffty = abs(ffty[0:len(ffty) / 2]) / 500  #FFT is mirror-imaged
            #print "MIN:\t%s\tMAX:\t%s"%(min(ffty),max(ffty))

            # First shift all the data to the left
            self.data = numpy.roll(self.data, -1, 0)
            # Make the last column equal to the new data
            self.data[-1] = ffty[::-1]

