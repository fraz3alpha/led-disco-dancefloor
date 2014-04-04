__authors__ = ['Andrew Taylor','Joel Wright']

import serial
import threading
import os

class ComboComms(object):
	def __init__(self, config):
		self.comms = []
		if config["system"]["debug"] == True:
			debug_comms = DebugComms(config["system"]["pipe"])
			self.comms.append(debug_comms)
			
		if config["system"]["floor"] == True:
			floor_comms = FloorComms(config["system"]["tty"])
			self.comms.append(floor_comms)

	def configure(self, tty=None, baud=None, timeout=None):
		for c in self.comms:
			c.configure(tty, baud, timeout)
			
	def send_data(self,data_buffer):
		for c in self.comms:
			c.send_data(data_buffer)

	def clear(self):  
		for c in self.comms:
			c.clear()

class FloorComms(object):
	def __init__(self, tty):
		self.tty = tty
		self.baud = 1000000
		self.timeout = 1
		self.s_port = serial.Serial(self.tty, self.baud, timeout=self.timeout)
		
	def configure(self, tty=None, baud=None, timeout=None):
		changes = False
		if tty is not None:
			self.tty = tty
			changes = True
		if baud is not None:
			self.baud = baud
			changes = True
		if timeout is not None:
			self.timeout = timeout
			changes = True
		if changes:
			self.ser = serial.Serial(self.tty, self.baud, timeout=self.timeout)

	def send_data(self,data_buffer):
		s = ""
		for i in data_buffer:
			s += chr(i%256)
		s += chr(1)
		self.s_port.write(s)

	def clear(self):  
		s = ""
		for i in range(self.pixels*3):
			s += chr(0)
		s += chr(1)
		self.s_port.write(s)

class DebugComms(object):
	def __init__(self, pipe):
		self.pipe = open(pipe,'w')
		
	def configure(self, tty=None, baud=None, timeout=None):
		return None

	def send_data(self,data_buffer):
		s = ""
		for i in data_buffer:
			v = hex(i)[2:]
			if len(v) < 2:
				s += "'\\x0%s'" % v
			else:
				s += "'\\x%s'" % v
		self.pipe.write("%s\n" % s)
		self.pipe.flush()

	def clear(self):
		s = ""
		for i in range(self.pixels*3):
			s += "\\x00"
		self.pipe.write(s)

