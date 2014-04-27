__authors__ = ['Andrew Taylor']

# For the timing features
import pygame

import logging

class PluginPlaylistModel(object):

	logger = logging.getLogger(__name__)

	# Contains a list of plugins that are active
	# This could be a playlist for the evening, which
	#  repeats in a loop - with each plugin getting a
	#  go for a while, before bowing out gracefully
	#  for the next one to take over.
	# Or, it could just be a list of all the plugins,
	#  and allows a user to specify which one is on
	#  at any given time

	def __init__(self):
		# Start out with an empty list
		self.new_playlist()
		self.model_changed_listeners = set()
		return None

	def new_playlist(self):
		self.playlist = []
		self.set_cycle_mode("LOOP")
		self.set_order_mode("FIXED")
		self.current_position = -1
		self.current_plugin = None

	def log_message(self, msg, log_level=None):
		#print ("%s - %s" % ("PluginPlaylistModel", msg))
		return None

	def add_model_changed_listener(self, listener):
		self.model_changed_listeners.add(listener)
		return None

	def remove_model_changed_listener(self, listener):
		self.model_changed_listeners.remove(listener)
		return None

	def notify_model_changed_listeners(self):
		for listener in self.model_changed_listeners:
			listener.playlist_model_changed_event()
		return None

	def get_current_plugin(self):

		# If there aren't any [more] plugins available, return None
		if (len(self.playlist) == 0):
			return None

		# If we are already at the last one, we could either keep going,
		#  or stop. Lets keep going
#		if (self.current_position == len(self.playlist) - 1):
#			if self.current_plugin is not None:
#				return self.current_plugin

		# If we have a current plugin, see if it should 
		#  still be running
		if self.current_plugin is not None:
			still_valid = True
			current_time = pygame.time.get_ticks()
			start_time = self.current_plugin['start_time']
			duration = self.current_plugin['duration']
			# If there is only one plugin, just leave it running
			if len(self.playlist) == 1:
				still_valid = True
			elif (duration is not None and duration > 0):
				if start_time is not None:
					self.log_message(self.current_plugin)
					self.log_message(current_time)
					if (current_time > start_time + duration):
						self.log_message("No longer valid, we need a new one")
						still_valid = False
			
			if still_valid:
				return self.current_plugin
		
		# So, we need to get the next plugin. This might be because 
		#  there wasn't one, or because the old one has expired.
		self.log_message ("New plugin required")
		self.log_message ("Playlist count: %d, current position: %d" % (len(self.playlist), self.current_position))

		# Only increment if it is likely to do any good
		self.logger.info("Current index = %d" % (self.current_position))
		if self.current_position < len(self.playlist):
			self.current_position += 1
		# See if we have reached the end
		if (self.current_position == len(self.playlist)) :
			if  self.get_cycle_mode() == 'ONCE':
				self.current_position = len(self.playlist) -1
				return self.current_plugin
			else:
				# Assume 'LOOP'
				self.current_position = 0
			
		self.log_message("The next potential plugin is %s" % (self.playlist[self.current_position]))

		current_plugin = dict()
		for entry in self.playlist[self.current_position]:
			current_plugin[entry] = self.playlist[self.current_position][entry]
		new_plugin_object = current_plugin['obj']
		# Create the plugin object
		current_plugin['instance'] = new_plugin_object()
		current_plugin['instance'].configure()

		# Set the start time
		current_plugin['start_time'] = pygame.time.get_ticks()	

		# Stop the current plugin if there is one
		if self.current_plugin is not None:
			self.current_plugin['instance'].stop()

		# Assign the current plugin to the current slot, and start it
		self.current_plugin = current_plugin
		self.current_plugin['instance'].start()

		self.logger.info("returning new plugin - %s" % (self.current_plugin))
		self.notify_model_changed_listeners()
		return self.current_plugin		
	
	def get_current_plugin_remaining_time(self):
		current_time = pygame.time.get_ticks()
		start_time = self.current_plugin['start_time']
		duration = self.current_plugin['duration']
	
		remaining_time = duration - (current_time - start_time)

		return remaining_time

	def get_current_plugin_index(self):
		return self.current_position

	def get_cycle_mode(self):
		return self.cycle_mode

	def set_cycle_mode(self, mode):
		if mode in self.get_cycle_modes():
			self.cycle_mode = mode
			return mode
		return None

	def get_cycle_modes(self):
		return ["LOOP", "ONCE"]

	def get_order_mode(self):
		return self.order_mode

	def set_order_mode(self, mode):
		if mode in self.get_order_modes():
			self.order_mode = mode
			return mode
		return None

	def get_order_modes(self):
		return ["FIXED", "RANDOM"]

	def get_next_plugin(self):
		if len(self.playlist) == 0:
			return None
		self.current_position = self.current_position + 1
		if self.current_position > len(self.playlist)-1:
			if self.cycle_mode == "LOOP":
				self.current_position = 0
			else:
				return None
		current_entry = self.playlist[self.current_position]
		return current_entry

	def add_plugin(self, plugin_details):
		# The plugin_details include general properties such
		#  as duration, but also potentially plugin specific
		#  properties such as period, amplitude, speed etc..
		self.playlist.append(plugin_details)

	def get_playlist(self):
		return self.playlist

	def get_playlist_length(self):
		return len(self.playlist)

	def get_remaining_playlist_time(self):
		pass

	def print_playlist(self):
		self.logger.info("Plugin playlist:")
		self.logger.info("  Ordering=%s, Cycling=%s" % (self.get_order_mode(), self.get_cycle_mode()))
		for entry in self.playlist:
			self.logger.info("  %s, duration=%d" % (entry['name'], entry['duration']))

