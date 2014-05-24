__authors__ = ['Andrew Taylor']

from lib.floorcanvas import FloorCanvas
from lib.controllers import ControllerInput

import pygame
import math
import logging

class Menu(object):

	logger = logging.getLogger(__name__)

	def __init__(self):
		self.init_menu()
		pass

	def init_menu(self):
		self.in_menu = False

		self.current_menu_playlist = None
		self.current_menu_playlist_index = 0
		self.current_menu_playlist_entry_index = 0

		self.plugin_model = None

	def is_in_menu(self):
		return self.in_menu

	def set_plugin_model(self, plugin_model):
		self.plugin_model = plugin_model

	"""
	The menu is used to select the currently running plugin, and there are 
	 two types, visualisation and games, which it might be useful to keep
	 separately. 
	The games and visualisation plugins are stored under different sub-menu
	 options. The current menu system is this (if it works in text):

	root - visualisation_splash
	     |          |
	     |          - playlist(s)
	     |          - plugin(s)
	     |
	     - games_splash
                        |
                        - game(s)

	Plugins have a splash screen
	Games have a splash screen
	Playlists are a little harder. It might be useful to draw a splash screen
	 with some indication of which playlist it is. Failing anything else, maybe
	 the index number of the playlist on top of a playlist splash background

	If we are already playing a plugin (very likely), then we should start up
	 the menu at that point. i.e. if we are enjoying a DiscoFloor plugin, the 
	 menu will already be in the visualisation branch of the menu, and located
	 at the DiscoFloor plugin - the user can then go left or right from there
	 and select a new plugin, or head back up and out of the menu if nothing
	 takes their fancy
	"""

	"""
	The menu system is the one real place that the framework wants to intercept
	 events that would otherwise go to the plugins.
	The menu is entered by pressing the SELECT button, and can be exited
	 either when SELECT or B is pressed (cancel) or START or A (confirm)
	"""
	def handle_event(self, e):

		#self.logger.info("Checking if the menu wants to handle the event")

		if (self.in_menu is False):
			# See if we should enter the menu
			if (e.type == pygame.JOYBUTTONDOWN):
				if e.button == ControllerInput.BUTTON_SELECT:
					self.logger.info("Entering Menu")

					# Only got into the menu if we have access to a model
					if self.plugin_model is not None:
						self.in_menu = True
						# Work out where we are, for where we should enter
						#  the menu
						if self.plugin_model.get_current_playlist() is not None:
							self.current_menu_playlist = self.plugin_model.get_current_playlist()
							self.current_menu_playlist_index = self.plugin_model.get_current_playlist_index()
							self.current_menu_playlist_entry_index = self.plugin_model.get_current_playlist().get_current_plugin_index()
							self.plugin_model.get_current_playlist().pause()

					# Consume the event, so no-one else processes it
					return None

			# We aren't in the menu, and we didn't go in, so it isn't for us
			return e
		else:
			self.logger.info("In Menu")
			if (e.type == pygame.JOYBUTTONDOWN):
				self.logger.info("Button Pressed")
				# See if we should leave the menu
				if e.button in [ControllerInput.BUTTON_SELECT]:
					self.logger.info("SELECT Button Pressed")
					self.logger.info("Leaving Menu")
					self.leave_menu()
					return None

				if e.button in [ControllerInput.BUTTON_B]:
					self.logger.info("B Button Pressed")
					# If we are at the root, leave the menu
					if self.current_menu_playlist == None:
						self.logger.info("Leaving Menu")
						self.leave_menu()
						return None
					# If we are in a playlist, go back up to the root
					self.current_menu_playlist = None
					return None

				# Else we are in the menu, and we apparently going to do 
				#  something

				if e.button in [ControllerInput.BUMPER_LEFT]:
					self.logger.info("BUMPER LEFT Button Pressed")
					# If we are in the root, then scroll the current playlist
					#  header splash to the left (assuming we aren't at the start)
					if self.current_menu_playlist == None:
						if self.current_menu_playlist_index > 0:
							self.current_menu_playlist_index -= 1
						self.logger.info("Root menu position = %d" % self.current_menu_playlist_index)
					else:
					# Else decrement the index in the current playlist
						if self.current_menu_playlist_entry_index > 0:
							self.current_menu_playlist_entry_index -= 1
						self.logger.info("Playlist entry position = %d" % self.current_menu_playlist_entry_index)
					# Consume the event and return
					return None

				if e.button in [ControllerInput.BUMPER_RIGHT]:
					self.logger.info("BUMPER RIGHT Button Pressed")
					# If we are in the root, then scroll the current playlist
					#  header splash to the right (assuming we aren't at the end)
					if self.current_menu_playlist == None:
						if self.current_menu_playlist_index < len(self.plugin_model.get_all_playlists()) - 1:
							self.current_menu_playlist_index += 1
						self.logger.info("Root menu position = %d" % self.current_menu_playlist_index)
					else:
					# Else increment the index in the current playlist
						if self.current_menu_playlist_entry_index < len(self.current_menu_playlist) - 1:
							self.current_menu_playlist_entry_index += 1
						self.logger.info("Playlist entry position = %d" % self.current_menu_playlist_entry_index)
					# Consume the event and return
					return None

				if e.button in [ControllerInput.BUTTON_A]:
					self.logger.info("A Button Pressed")
					# If we are in the root, enter a playlist, starting at zero
					if self.current_menu_playlist == None:
						playlists = self.plugin_model.get_all_playlists()
						self.current_menu_playlist = playlists[self.current_menu_playlist_index]
						self.current_menu_playlist_entry_index = 0
						self.logger.info("Entering playlist: %s" % self.current_menu_playlist )
					else:
						# Choose the plugin in the playlist.
						playlist = self.plugin_model.set_current_playlist_by_index(self.current_menu_playlist_index)
						playlist.set_current_plugin_by_index(self.current_menu_playlist_entry_index)
						self.logger.info("Choosing plugin #%d in playlist #%d" % (self.current_menu_playlist_entry_index, self.current_menu_playlist_index))
						# Get out of the menu
						self.leave_menu()
					# Consume the event and return
					return None
					
			# We are in the menu, and will always consume the button presses,	
			#  this catches the event if it wasn't actually something we cared about
			return None

	def leave_menu(self):
		self.in_menu = False
		if self.plugin_model.get_current_playlist() is not None:
			self.plugin_model.get_current_playlist().resume()

	def get_current_plugin(self):
		return "WavyBlobVisualisationPlugin"

	def draw_error(self, canvas):
		canvas.set_colour((0xFF,0,0))
		text = "X"
		colour = (0xFF,0xFF,0xFF)
		(text_width, text_height) = canvas.get_text_size(text)

		w = canvas.get_width()
		h = canvas.get_height()

		x_position = int(w/2.0 - text_width/2.0)
		y_position = int(h/2.0 - text_height/2.0)
		canvas.draw_text(text, colour, x_position, y_position)

		return canvas

	def draw_splash_unknown(self, canvas):
		canvas.set_colour((0,0,0))
		text = "?"
		colour = (0xFF,0,0)
		(text_width, text_height) = canvas.get_text_size(text)

		w = canvas.get_width()
		h = canvas.get_height()

		x_position = int(w/2.0 - text_width/2.0)
		y_position = int(h/2.0 - text_height/2.0)
		canvas.draw_text(text, colour, x_position, y_position)

		return canvas

	"""
	In menu mode the framework will draw some things on the floor to guide the 
	 user to find what they want. 
	This method will return None if nothing is to be done
	"""
	def draw_frame(self, canvas):
		if self.in_menu:
			if self.current_menu_playlist == None:
				# Draw the playlist's splash
				self.logger.info("Drawing splash screen for playlist %d" % self.current_menu_playlist_index)
				playlists = self.plugin_model.get_all_playlists()
				current_menu_playlist = playlists[self.current_menu_playlist_index]
				current_menu_playlist.draw_splash(canvas)

				self.draw_scrollbar(canvas, self.current_menu_playlist_index, len(playlists))

				return canvas
			else:
				# We are in a playlist, so draw the splash of the plugin we 
				#  are currently at
				self.logger.info("Drawing splash screen for playlist %d, plugin %d" % (self.current_menu_playlist_index, self.current_menu_playlist_entry_index))
				# Fish the plugin we want to draw out of the right playlist
				playlists = self.plugin_model.get_all_playlists()
				current_menu_playlist = playlists[self.current_menu_playlist_index]
				current_menu_playlist_plugins = current_menu_playlist.get_plugins()
				plugin = current_menu_playlist_plugins[self.current_menu_playlist_entry_index]
			
				# The plugin can't be trusted, so guard against badness
				try:
					splash_canvas = plugin.draw_splash(canvas)
				except Exception as e:
					self.logger.warn(e)
					splash_canvas = self.draw_error(canvas)

				self.draw_scrollbar(canvas, self.current_menu_playlist_entry_index, len(current_menu_playlist_plugins))

				return canvas
	
		return None

	def draw_scrollbar(self, canvas, position, total):
		# Blank the bottom row for a scroller
		for x in range(canvas.get_width()):
				canvas.set_pixel(x,canvas.get_height()-1, (0,0,0))

		pixels_per_entry = canvas.get_width() / float(total)
				
		bar_start_x = int(math.floor(pixels_per_entry * position))
		bar_end_x = int(math.ceil((pixels_per_entry *position) + pixels_per_entry))
		bar_colour = (0xFF,0xFF,0)
		canvas.draw_line(bar_start_x, canvas.get_height()-1, bar_end_x, canvas.get_height()-1, bar_colour)
		return canvas

