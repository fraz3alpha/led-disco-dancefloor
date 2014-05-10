__authors__ = ['Joel Wright']

import logging
import pygame

"""
We need a way to abstract the controllers so that we can use lots of different
 inputs. For example, a physical controller is just as good as keyboard input
"""

class ControllerInput(object):

	logger = logging.getLogger(__name__)

	BUTTON_NONE = 0

	DPAD_UP = 10
	DPAD_DOWN = 11
	DPAD_LEFT = 12
	DPAD_RIGHT = 13

	BUTTON_X = 0
	BUTTON_A = 1
	BUTTON_B = 2
	BUTTON_Y = 3

	BUMPER_LEFT = 4
	BUMPER_RIGHT = 5

	BUTTON_SELECT = 8
	BUTTON_START = 9

	CONTROLLER_NONE = 0
	CONTROLLER_1 = 0
	CONTROLLER_2 = 1

	

	def __init__ (self):
		self.mapping = dict()
		# Two controllers

		self.mapping[pygame.K_w] = {"joy": ControllerInput.CONTROLLER_1, "axis": 1, "value": -1}
		self.mapping[pygame.K_s] = {"joy": ControllerInput.CONTROLLER_1, "axis": 1, "value": 1}
		self.mapping[pygame.K_a] = {"joy": ControllerInput.CONTROLLER_1, "axis": 0, "value": -1}
		self.mapping[pygame.K_d] = {"joy": ControllerInput.CONTROLLER_1, "axis": 0, "value": 1}

		self.mapping[pygame.K_q] = {"joy": ControllerInput.CONTROLLER_1, "button": ControllerInput.BUMPER_LEFT}
		self.mapping[pygame.K_e] = {"joy": ControllerInput.CONTROLLER_1, "button": ControllerInput.BUMPER_RIGHT}

		self.mapping[pygame.K_z] = {"joy": ControllerInput.CONTROLLER_1, "button": ControllerInput.BUTTON_SELECT}
		self.mapping[pygame.K_x] = {"joy": ControllerInput.CONTROLLER_1, "button": ControllerInput.BUTTON_START}

		self.mapping[pygame.K_g] = {"joy": ControllerInput.CONTROLLER_1, "button": ControllerInput.BUTTON_A}
		self.mapping[pygame.K_f] = {"joy": ControllerInput.CONTROLLER_1, "button": ControllerInput.BUTTON_B}
		self.mapping[pygame.K_t] = {"joy": ControllerInput.CONTROLLER_1, "button": ControllerInput.BUTTON_X}
		self.mapping[pygame.K_r] = {"joy": ControllerInput.CONTROLLER_1, "button": ControllerInput.BUTTON_Y}
		

		self.mapping[pygame.K_o] = {"joy": ControllerInput.CONTROLLER_2, "axis": 1, "value": -1}
		self.mapping[pygame.K_l] = {"joy": ControllerInput.CONTROLLER_2, "axis": 1, "value": 1}
		self.mapping[pygame.K_k] = {"joy": ControllerInput.CONTROLLER_2, "axis": 0, "value": -1}
		self.mapping[pygame.K_SEMICOLON] = {"joy": ControllerInput.CONTROLLER_2, "axis": 0, "value": 1}

		self.mapping[pygame.K_i] = {"joy": ControllerInput.CONTROLLER_2, "button": ControllerInput.BUMPER_LEFT}
		self.mapping[pygame.K_p] = {"joy": ControllerInput.CONTROLLER_2, "button": ControllerInput.BUMPER_RIGHT}

		self.mapping[pygame.K_COMMA] = {"joy": ControllerInput.CONTROLLER_2, "button": ControllerInput.BUTTON_SELECT}
		self.mapping[pygame.K_PERIOD] = {"joy": ControllerInput.CONTROLLER_2, "button": ControllerInput.BUTTON_START}

		self.mapping[pygame.K_HASH] = {"joy": ControllerInput.CONTROLLER_2, "button": ControllerInput.BUTTON_A}
		self.mapping[pygame.K_QUOTE] = {"joy": ControllerInput.CONTROLLER_2, "button": ControllerInput.BUTTON_B}
		self.mapping[pygame.K_RIGHTBRACKET] = {"joy": ControllerInput.CONTROLLER_2, "button": ControllerInput.BUTTON_X}
		self.mapping[pygame.K_LEFTBRACKET] = {"joy": ControllerInput.CONTROLLER_2, "button": ControllerInput.BUTTON_Y}

		
	"""
	Map or reshape events. 
	They may go out as they came in, or they might be changed
	"""
	def map_event(self, e):
		self.logger.info("Mapping event - %s" % e)
		if e.type in [pygame.KEYDOWN, pygame.KEYUP]:
			return self.map_key_to_joystick_event(e)
		#if e.type in [pygame.JOYAXISMOTION]:
		#	return self.map_pad_to_joystick_event(e)
		return e

	def map_pad_to_joystick_event(self, pad_event):
		event_attr = dict()

		event_attr["joy"] = pad_event.joy

		if pad_event.axis == 0:
			if pad_event.value > 0.5:
				event_attr["button"] = self.DPAD_UP
			elif pad_event.value < 0.5:
				event_attr["button"] = self.DPAD_DOWN
			else:
				pass

	"""
	Map key events to joystick events.
	If it doesn't map to something we know about, then return the original event
	"""
	def map_key_to_joystick_event(self, key_event):
		self.logger.info("Mapping key event to joystick event")

		event_attr = dict()
		
		event_type = None

		if key_event.key in self.mapping:
			self.logger.info("%s" % self.mapping[key_event.key])
			event_attr["joy"] = self.mapping[key_event.key]["joy"]
			if "button" in self.mapping[key_event.key]:
				event_attr["button"] = self.mapping[key_event.key]["button"]
				if key_event.type == pygame.KEYDOWN:
					event_type = pygame.JOYBUTTONDOWN
				if key_event.type == pygame.KEYUP:
					event_type = pygame.JOYBUTTONUP
			if "axis" in self.mapping[key_event.key]:
				event_attr["axis"] = self.mapping[key_event.key]["axis"]
				event_type = pygame.JOYAXISMOTION
				if key_event.type == pygame.KEYUP:
					event_attr["value"] = 0.0
				else:
					event_attr["value"] = self.mapping[key_event.key]["value"]
				
		else:
			return key_event

		if event_type is not None:
			return pygame.event.Event(event_type, event_attr)
		else:
			return key_event

		
