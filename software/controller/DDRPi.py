#
# The top level script for the DDRPi floor.
# This is what you run
#

# Configuration options can be given either by:
#  - Including them in a config.yaml file
#  - Including them in a config file as described by the option --config=
#  - Defining/Overriding them on the command line with --<option>=<value>

# Options on the command line override the options on the config file

# Current output options are:
#  - TTY
#  - Named pipe (character stream)
#  - Graphical Simulation Window
# These are configurable by including as many --output=<OutputClass> directives
#  as necessary, and they will take either the global config values, or those
#  specified on the line, e.g.
#  --output=TtyOutput,device=/dev/ttyUSB0,baud=1000000
#  --output=SimulationOutput
#  --output=NamedPipeOutput,pipe=/tmp/floor_pipe

# Plugins are initially divided into two groups, i.e. those which run visualisation
#  patterns for a while, and those which are games and require interaction and will
#  run until they are manually changed.

# The Plugin class is extended by VisualisationPlugin and GamePlugin

# Examples of classes extending VisualisationPlugin are:
#  SpeedingBlobsPlugin
#  BlobsPlugin
#  DiscoFloorPlugin
#  ScrollingTextPlugin

# Examples of classes extending GamePlugin are:
#  PongPlugin
#  TetrisPlugin

# We can run plugins by specifying them on the command line, or by specifying a 
#  file that describes what plugins to run and how to run them.
# For example:
#  --plugin=SpeedingBlobsPlugin,duration=20s
#  --plugin=DiscoFloorPlugin,duration=60s,size=2,speed=2
#  --plugin=ScrollingTextPlugin,text='Congratulations',repeat=1,speed=3,textcolour=red,backgroundcolour=0x00FF00
#   or
#  --pluginfile=cycle1.yaml
#     where cycle1.yaml contains similar configuration information to the plugin
#      options above.
#
# Multiple plugins and plugin lists will be concatented together and run in that order - 
#  the list will repeat when it reaches the end.
# The options are plugin dependent, and will be parsed by the plugin itself,
#  any unknown options will be ignored (possibly silently).

# There are several global options that can be overridden on the commandline, including:
#  How long each plugin runs for by default before going on to the next:
#  --pluginduration=10[s|m] , the default is 60s, the default unit is s[econds]
#  What order the plugins should be run in
#  --pluginorder=[fixed|random] , the default is fixed.

# The App runs a webserver in the background which provides some configuration options,
#  runtime information, and some input capability.
# The intention is that it can be used for:
# a) Configuring the layout of the modules
# b) Choosing the active plugin
# c) Viewing the current plugin order/list
# d) Adding to, or modifying, the plugin list
# e) As an input device, either a controller, or to configure a scrolling text plugin etc..
# f) Viewing debug information, such as controllers available, button presses etc..
# 
# Different levels of access will be granted based on the user profile. If the controlling
#  computer is connected to the internet it might be possible to send messages to it via Twitter,
#  if it is only on a local network, then the gateway webpage will be the only access point.

# For command line argument parsing
import argparse
# For parsing config files 
import yaml
# For file checking
import os
# For all your time related needs
import time
# We need pygame for the controller input logic, and the debug gui
import pygame

# Python comes with some color conversion methods.
import colorsys
# For Math things, what else
import math

# For dynamically loading modules from files
import imp
import inspect

# Dance Floor library classes
from lib.layout import DisplayLayout
from lib.floorcanvas import FloorCanvas
from lib.output import GuiOutput, SerialOutput, PipeOutput
from lib.playlist import PluginPlaylistModel
from lib.controllers import ControllerInput
from lib.menu import Menu
from lib.pluginmodel import PluginModel

import logging

#from VisualisationPlugin import VisualisationPlugin
#from visualisation_plugins.wavyblob import WavyBlobVisualisationPlugin

logger = logging.getLogger(__name__)

class GuiInputAdapter(object):

	logger = logging.getLogger(__name__)

	def __init__(self, gui_output):
		self.gui_output = gui_output

	def handle_event(self, canvas, e):
		self.logger.info("GuiOutput - %s" % (self.gui_output))
		if e.type == pygame.MOUSEMOTION:
			self.logger.info("%s" % e.pos)
			relative_position = self.gui_output.get_fractional_position(canvas, *e.pos)
			#e['floor_relative_pos'] = relative_position
			self.logger.info("%s" % relative_position)
			cell_position = self.gui_output.get_nearest_cell(canvas, *e.pos)
			self.logger.info("%s" % cell_position)
			#e['floor_cell_pos'] = cell_position
		return e

class DDRPiMaster():

	DEFAULT_CONFIG_FILE = "config.yaml"
	DEFAULT_PLUGIN_DIRECTORY = "plugins"
	logger = logging.getLogger(__name__)

	# In the absence of a custom playlist, or a specific plugin
	#  being requested, attempt to start the first available plugin
	#  of this array
	DEFAULT_STARTUP_PLUGIN = ["DiscoFloorVisualisationPlugin"]

	"""
	Initial constructor set up
	"""
	def __init__ (self):
		self._initial_setup()

	def _initial_setup(self):
		self.gui = None
		self.clock = pygame.time.Clock()
		pass

	"""
	Entry point for running the code.
	This method does not return until the program exits,
	 or an error is thrown
	"""
	def run(self):
		self.run_ddrpi()

	"""
	Hardened entry point for running the code,
	 if errors are thrown during execution, the code
	 will reset, and hopefully this method will never return.
	Best used for debugging, or when running for an event when 
	 you don't want the floor to break.
	TODO: Not tested
	"""
	def run_indefinitely(self):
		while True:
			try:
				self.run_ddrpi()
			except Exception as e:
				self.logger.error("DDRPi", "%s" % e)		

	"""
	If the framework needs to handle an event it is done here.
	If the event is not consumed, or is to be passed on for someone else to have
	 a crack at then the event should be returned. Return none if no more processing
	 should take place
	"""
	def handle_event(self, e):
		if self.gui is not None:
			# See if the gui wants to do something with it
			return self.gui.handle_event(e)
		return e

	"""
	It is possible that the framework may wish to draw on the floor. It will do so here.
	Return None if the plugins should be doing the drawing
	"""
	def draw_frame(self, canvas):
		return None

	"""
	The actual running of the code
	"""
	def run_ddrpi(self):
		self.logger.info("Starting DDRPi running at %s" % (time.strftime('%H:%M:%S %d/%m/%Y %Z')))
		config = self.parse_commandline_arguments()
		self.logger.info("%s" % config)

		# Initialise pygame, which we use for the GUI, controllers, rate limiting etc...
		pygame.init()
		# Set up a list of output endpoints, and input adapaters
		output_devices = []
		input_adapters = []

		# Parse the floor layout
		layout = DisplayLayout(config["modules"])
		(floor_x, floor_y) = layout.calculate_floor_size()
		converter = layout.get_converter()
		
		# Create a suitably sized canvas for the given config
		canvas = FloorCanvas(floor_x, floor_y)

		# Create a menu object to handle user input
		menu = Menu()

		# Set up the various outputs defined in the config.
		# Known types are the moment are "gui", "serial" and "pipe"
		if ("outputs" in config):
			for output_number, details in config["outputs"].items():
				self.logger.info("%d - %s" % (output_number, details))
				if "enabled" in details:
					if details["enabled"] is False:
						self.logger.info("Skipping disabled output %d" % output_number)
						self.logger.info("%s" % details)
						continue
				self.logger.info("Configuring output %d" % output_number)
				if details["type"] == "serial":
					self.logger.info("Creating a SerialOutput class")
					serial_output = SerialOutput(details)
					serial_output.set_name("SerialOutput-#%d" % output_number)
					serial_output.set_output_converter(converter)
					output_devices.append(serial_output)
				elif details["type"] == "gui":
					# Skip the gui if headless has been specified
					if "headless" in config["system"] and config["system"]["headless"] is True:
						continue
					self.logger.info("Creating a GuiOutput class [There can be only one]")
					gui_output = GuiOutput()
					output_devices.append(gui_output)
					self.gui = gui_output
				elif details["type"] == "pipe":
					self.logger.info("Creating a PipeOutput class")
					pipe_output = PipeOutput(details)
					pipe_output.set_output_converter(converter)
					output_devices.append(pipe_output)
				else:
					self.logger.warn("I don't know how to handle an output of type '%s'" % (details["type"]))

		# Initialise any connected joypads/joysticks
		controllers = self.init_joysticks()

		# There can be many plugin directories, and can either be relative (from the directory in which this
		#  script resides), or absolute. All directories are scanned, and the plugins found are added to the 
		#  master list. If there are duplicate class names, the last one encountered probably wins silently.
		visualisation_plugin_dirs = ["visualisation_plugins", "game_plugins"]

		# We will store a dict of classname > class object in here
		available_plugins = self.load_plugins(visualisation_plugin_dirs)

		# Add all the available plugins to the menu
		#menu.add_available_plugins(available_plugins)

		# Create a data model that we can use here, and pass to the
		#  menu class to change what is active
		# We should also be able to provide this model to a webservice
		#  class if we chose to add in HTTP control of the floor too
		plugin_model = PluginModel()

		# Populate the data model
		plugin_model.add_plugins(available_plugins)

		# Link it up to the menu
		menu.set_plugin_model(plugin_model)

		# If we have defined a specific plugin to run indefinitely on the command line, use that
		specific_plugin = False
		if "plugin" in config["system"]:
			only_plugin = config["system"]["plugin"]
			if plugin_model.set_current_plugin(only_plugin) is not None:
				self.logger.info("Running requested plugin %s" % only_plugin)
				specific_plugin = True
			else:
				self.logger.info("Unable to find requested plugin: %s" % (only_plugin))
				self.logger.info("Available plugins are:")
				for available_plugin in available_plugins:
					self.logger.info("  %s" % (available_plugin))
				# This is intended as a development debug option, or at the very least the 
				#  person using it should know what they are doing, so if it isn't available
				#  for whatever reason, exit.
				exit()
		if "playlist" in config["system"]:
			
			# Retreive the list of playlists specified on the command line
			#  or config file
			playlist_list = config["system"]["playlist"]
			self.logger.info(playlist_list)
			if len(playlist_list) > 0:
				for playlist in playlist_list:
					# Make the playlist an absolute path if it isn't already
					if (not os.path.isabs(playlist)):
						root_directory = os.path.dirname(os.path.realpath(__file__))
						playlist = os.path.join(root_directory, playlist)
					# Load the playlist
					plugin_model.add_playlist_from_file(playlist)
				# Start the first one we added
				self.logger.info("Setting current playlist to the first one we added")
				plugin_model.set_current_playlist_by_index(1)

		# When there is no plugin specified and no user playlists either, make the first
		#  playlist active, and select either the first plugin, or, if it is available,
		#  any of the plugins listed in DEFAULT_STARTUP_PLUGIN

		# .set_current_plugin() is a convenience method to start the all_plugins playlist
		#  with the given plugin name
		self.logger.info("Current playlist: %s" % plugin_model.get_current_playlist())
		have_started_a_plugin = False
		if plugin_model.get_current_playlist() is None:
			for specified_plugin in self.DEFAULT_STARTUP_PLUGIN:
				if plugin_model.set_current_plugin(specified_plugin) is not None:
					have_start_a_plugin = True
					self.logger.info("Started default plugin %s" % specified_plugin)
					break

			# If we still haven't started anything, just start the all_plugins playlist
			if have_started_a_plugin is False:
				plugin_model.set_current_playlist_by_index(0)

		print (plugin_model)
#
		if self.gui is not None:
			#playlistModel.add_model_changed_listener(self.gui)
#			self.gui.set_playlist_model(playlistModel)
			self.gui.set_plugin_model(plugin_model)
			
	
		# Create an object that can map key events to joystick events
		self.controller_mapper = ControllerInput()

		# The main loop is an event loop, with each part 
		#  non-blocking and yields after doing a short bit.
		# Each 'bit' is a frame

		# Check for pygame events, primarily coming from
		#  gamepads and the keyboard
		
		running = True
		while running:
		
			current_playlist = plugin_model.get_current_playlist()
			current_plugin = None
			if current_playlist is not None:
				current_plugin = current_playlist.get_current_plugin()

			for e in pygame.event.get():

				if e.type == pygame.QUIT:
					running = False

				e = self.controller_mapper.map_event(e)

				# Each consumer should return None if the
				#  event has been consumed, or return
				#  the event if something else should
				#  act upon it

				# Check first if the framework is going to 
				#  consume this event. This includes heading
				#  into menus, possibly modifying the plugin
				#  model (previous/next plugin)
				#e = self.handle_event(e)
				#if e is None:
				#	continue

				# See if the menu wants to consume this event
				e = menu.handle_event(e)
				if e is None:
					 continue

				self.print_input_event(e)

				# Next pass it on to the current plugin, if
				#  there is one
				if current_plugin is not None:
#					e = current_plugin['instance'].handle_event(e)
					e = current_plugin.instance.handle_event(e)
					if e is None:
						continue

			# Ask the framework if it thinks it is displaying something
			# display_frame = self.draw_frame(canvas)
			# Ask the menu if it wants to draw something
			display_frame = menu.draw_frame(canvas)
			if display_frame is None:
				# If there is nothing to draw from the framework, ask
				#  the current plugin to do something is there is one
				if current_plugin is not None:
#					display_frame = current_plugin['instance'].draw_frame(canvas)
					# There is every chance that the plugin might throw an 
					#  exception as we have no control over the quality of
					#  external code (or some in-house code!), so catch any
					#  exception	
					try:
						display_frame = current_plugin.instance.draw_frame(canvas)
					except:
						self.logger.warn("Current plugin threw an error whilst running draw_frame()")
						display_frame = self.draw_error(canvas)
						
						
				else:
					# If there is no plugin, then the framework should
					#  do something
					pass

			# Send the data to all configured outputs if there is any to send
			# TODO: If the plugin doesn't return a canvas for some reason,
			#        then the gui should be updated with a canvas, but the output
			#        plugins need not be informed. The problem is that if the plugin
			#        happens to never return anything, then the gui is never updated
			if display_frame is None:
				canvas.set_colour((0,0,0))
				display_frame = canvas

			for output_device in output_devices:
				output_device.send_data(display_frame)

			# Limit the framerate, we need not do it in the plugins - they really shouldn't
			#  mind that we are running at a max of 25fps
			self.clock.tick(25)

		pygame.quit()
		exit()

	def print_input_event(self, e):
		self.logger.info("%s" %e)

		X = 0
		A = 1
		B = 2
		Y = 3
		LB = 4
		RB = 5	
		SELECT = 8
		START = 9


		if pygame.event.event_name(e.type) == "JoyButtonDown":
			self.logger.info("JoyButtonDown")
		if pygame.event.event_name(e.type) == "JoyButtonUp":
			self.logger.info("JoyButtonUp")

		return None

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

	"""
	Initialise all the connected joysticks/pads.

	This is probably going to be one or two SNES controllers.

	If there aren't any connected controllers, equivalent operation can be provided
	 by the keyboard shortcuts
	"""
	def init_joysticks(self):
		num_c = pygame.joystick.get_count()
		self.__controllers__ = {}
		
		for c in range(0,num_c):
			self.__controllers__[c] = pygame.joystick.Joystick(c)
			self.__controllers__[c].init()
			
		self.logger.info("Initialised %s controllers" % num_c)

		return self.__controllers__
		
	"""
	Iterate over the directories passed in, and find as many plugins as we can
	A plugin is currently defined as something that has a classname that ends
	 with "VisualisationPlugin". This might not be ideal, as if we have an abstract
        super class then we will have to have some way of saying that this is not a real
	 plugin.
	Return a dict of class objects, keyed on the class name. This allows us to 
	 create instances of these classes whenever we want
	"""
	def load_plugins(self, directory_list):
		available_plugins = dict()

		for plugin_dir in directory_list:

			# If the directory is not fully qualified, make it relative
			#  to the DDRPi directory
			if (not os.path.isabs(plugin_dir)):
				root_directory = os.path.dirname(os.path.realpath(__file__))
				plugin_dir = os.path.join(root_directory, plugin_dir)

			if not os.path.isdir(plugin_dir):
				self.logger.warn("'%s' is not a directory" % (plugin_dir))

			# Recursively search the given directory for .py files which 
			#  aren't commented out (start with __)
			these_plugins = dict()
			for root, dirs, files in os.walk(plugin_dir):
				for fname in files:
					if fname.endswith(".py") and not fname.startswith("__"):
						# Remove the .py from the end
						module_name = fname.split('.',1)[0]
						# Create the full path to the file
						fpath = os.path.join(root, fname)
						# Attempt to load the module dynamically
						try:
							foo = imp.load_source(module_name, fpath)
							# Search through the members of this module
							#  to find the classes used, and find the
							#  ones that end in "VisualisationPlugin" which
							#  are defined in this module
							for name, obj in inspect.getmembers(foo):
								if inspect.isclass(obj):
									if name.endswith("Plugin") and obj.__module__ == module_name:
										these_plugins[obj.__name__] = obj
						except Exception as e:
							self.logger.info("An error occurred loading plugin %s from %s" % (module_name, fpath))
							self.logger.info(e)

			# Print out a list of what plugins were loaded from each directory
			self.logger.info("Visualisation plugins loaded from '%s':" % (plugin_dir))
			if len(these_plugins) == 0:
				self.logger.info("  None")
			else:
				for plugin_name in these_plugins:
					self.logger.info("  %s" % (plugin_name))

			# Add these_plugins to our master list
			available_plugins.update(these_plugins)

		return available_plugins
	
	"""
	The commandline arguments are parsed, and a config file is created and returned to the 
	 rest of the programme.

	Most commandline arguments are available in the resultant config file, and are added to
	 the ["system"] entry, based on a whitelist

	TODO: 
	Additional commandline options could be added based on what plugins are available, or 
	 handled more generically. It would be nice to print out what options are available for
	 each plugin, which would necessitate parsing the available plugins, and also finding
	 out the plugins directory, which can be modified in the config file - so that would 
	 need to be parsed first

	TODO:
	Possibly other parts of the program may wish to add to the help, so it would be useful
	 if there was some way of them contributing
	"""
	def parse_commandline_arguments(self):

		parser = argparse.ArgumentParser(description='The main dance floor control program')


		# First pass, get the --config option, if present
		parser.add_argument('--config', required=False, dest='config', default=None, help='The location of the configuration file')
		# --testmode makes the script use a predefined set of config, so that --config is not required
		parser.add_argument('--testmode', required=False, dest='testmode', default=False, help='Use a pre-configured set of options, useful for testing - only a GUI output, and a 24x18 cell floor', action="store_true")
		# --headless overrides any enabled guis
		parser.add_argument('--headless', required=False, dest='headless', default=None, help='Don\'t bring up a GUI', action="store_true")
		# --plugin defines a single plugin to be used, helpful in development and testing
		parser.add_argument('--plugin', required=False, dest='plugin', default=None, help='The classname of the one plugin to use')
		parser.add_argument('--playlist', required=False, action='append', dest='playlist', default=None, help='A playlist to use')
		args, unknown = parser.parse_known_args()
		self.logger.info("Just the --config argument:")
		self.logger.info("%s"% args)
	
		# The contents of the config file, either parsed from a file, or a test one created
		#  in memory
		config_file_data = None

		if (args.testmode is True):
			# If test mode, this will override the config with something created by
			#  this script
			config_file_data = self.get_testmode_config()
		else:
			# Else we are parsing one passed in via the command line, try to parse
			#  it if it exists
			if (args.config is None):
				args.config = self.DEFAULT_CONFIG_FILE
				if (not os.path.isfile(args.config)):
					self.logger.warn("default config file (%s), does not exist" % (args.config))
					exit()
			else:
				if (not os.path.isfile(args.config)):
					self.logger.warn("config file passed (%s), does not exist" % (args.config))
					exit()

			# By this point args.config will be a file that does exist
			config_file_data = self.parse_config_file(args.config)

		# Something could have gone wrong parsing either one though
		if (config_file_data is not None):
			self.logger.info("%s" % config_file_data)
		else:
			self.logger.error("The config file was unable to be parsed, nothing will work, exiting")
			exit()

		# Add in select other commandline arguments into the system section of the config file
		config_file_data['arg'] = dict()
		for key, value in vars(args).items():
			if (value is not None):
				if (key in self.list_known_system_args()):
					config_file_data['system'][key] = value

		return config_file_data

		# I'll come back to this
		#parser.add_argument('--plugin_directory', required=False, nargs='*', dest='plugin_directory', default=self.DEFAULT_PLUGIN_DIRECTORY, help='The location(s) of available plugins')

		#parser.add_argument('--plugins', required=False, nargs='*')
		#parser.add_argument('--plugin_order', required=False)
		#args = parser.parse_args()
		#print ("All the arguments")
		#print args;

		#return None

	"""
	The testmode config brings up a stock sized dancefloor, with a gui, but no other outputs
	"""
	def get_testmode_config(self):
		config = dict()

		# Add a single output, a GUI
		config["outputs"] = dict()
		config["outputs"][1] = {"name": "testmode gui", "type": "gui", "enabled": "true"}
	
		# Enable debug, and set the default plugins directory
		config["system"] = dict()
		config["system"]["debug"] = True
		config["system"]["plugin_dir"] = "plugins"

		# Add a single dancefloor module of the correct size
		config["modules"] = dict()
		config["modules"][1] = {"width": 24, "height": 18, "x_position": 0, "y_position": 0, "orientation": "N"}

		return config

	"""
	Parse the config file, which should be in YAML form
	"""
	def parse_config_file(self, config_file):
		self.logger.info("Parsing config file: '%s'" % (config_file))
		if (not os.path.isfile(config_file)):
			self.logger.error("Error, provided config file: '%s', does not exist, exiting" % (config_file))
			exit()
		f = open(config_file)
		data = yaml.load(f)
		f.close()
		return data

	"""
	Whitelist of commandline arguments to add into the system section of the config
	"""
	def list_known_system_args(self):
		args = list()
		args.append("headless")
		args.append("plugin")
		args.append("playlist")
		return args;

# GO GO GO!
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger.info("Loading DDRPi")
ddrpi = DDRPiMaster()
ddrpi.run()
#ddrpi.run_indefinitely()

