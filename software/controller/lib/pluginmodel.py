__authors__ = ['Andrew Taylor']

import logging
import yaml
import os
import pygame

# For counting instances of output classes
from itertools import count

from VisualisationPlugin import VisualisationPlugin
from GamePlugin import GamePlugin

# from DDRPi import FloorCanvas

class PluginModel(object):
    logger = logging.getLogger(__name__)

    def __init__(self, surface_size):
        self.reset_model()
        self.surface_size = surface_size
        pass

    def reset_model(self):
        # Keep track of all the available plugin names and objects
        self.plugins = dict()
        self.playlists = []
        # All the plugins are add to a special PluginPlaylist that
        #  occupies the first slot. This should be displayed differently,
        #  and probably not auto-increment when it is playlist - i.e.
        #  is user controlled
        self.all_plugins_playlist = PluginPlaylist(PluginPlaylist.ALL)
        self.add_playlist(self.all_plugins_playlist)
        self.current_playlist = None

    """
    Set the current plugin in the "all plugins" special playlist
     by name, and therefore leave it running indefinitely
    """

    def set_current_plugin(self, plugin_name):
        self.logger.info("Attempting to set current plugin to: %s" % plugin_name)
        all_plugins = self.get_all_plugins_playlist()
        for idx, plugin in enumerate(all_plugins.get_plugins()):
            if plugin.plugin_name == plugin_name:
                self.logger.info("Starting requested plugin: %s at #%d" % (plugin_name, idx))
                self.current_playlist = all_plugins
                return all_plugins.start_plugin(idx)
        return None

    """
    Set the current playlist
    """

    def set_current_playlist_by_index(self, idx):
        self.current_playlist = self.playlists[idx]
        self.current_playlist._reset_playlist_state()
        return self.current_playlist

    def get_current_playlist(self):
        return self.current_playlist

    #	def get_available_plugins(self, plugin_type=None):
    #		#TODO: Implement get_available_plugins()
    #		if (plugin_type is None):
    #			return self.available_plugins
    #		pass

    """
    Return all the playlists available
    """

    def get_all_playlists(self):
        return self.playlists

    """
    Return only those playlists that the user has added
     (assuming there are any), else return an empty array
    """

    def get_user_playlists(self):
        if len(self.playlists) > 1:
            return self.playlists[1:]
        return []

    """
    Return the playlists containing all the plugins
    This one will usually be manually incremented
    """

    def get_all_plugins_playlist(self):
        return self.playlists[0]

    def get_current_playlist_index(self):
        if self.current_playlist == None:
            return -1
        for idx, playlist in enumerate(self.playlists):
            if self.current_playlist == playlist:
                return idx
        return -1


    def get_current_playlist(self):
        return self.current_playlist

    def add_playlist(self, playlist):
        self.logger.info(playlist)
        self.playlists.append(playlist)
        self.logger.info("Playlist queue is now of size %d" % len(self.playlists))
        return len(self.playlists) -1

    def add_playlist_from_file(self, playlist_file):
        if not os.path.exists(playlist_file):
            self.logger.error("Unable to load playlist, it doesn't exist: %s" % playlist_file)
            return None
        f = open(playlist_file)
        data = yaml.load(f)
        f.close()

        if data is None:
            self.logger.error("Unable to parse playlist: %s" % playlist_file)
            return None

        playlist = PluginPlaylist(PluginPlaylist.USER)

        if "plugins" in data:
            playlist_entries = data["plugins"]
            for details in playlist_entries:
                self.logger.info("Playlist entry: %s" % (details))
                if "name" not in details:
                    # We need the name, else we can't do anything!
                    self.logger.warn("Missing name for entry : %s" % (details))
                    continue
                plugin_name = details["name"]
                # Add the class object to the details, provided we have it
                if plugin_name not in self.plugins:
                    self.logger.warn("Unable to locate %s in available plugins" % plugin_name)
                    continue
                details["obj"] = self.plugins[plugin_name]
                details["size"] = self.surface_size
                self.logger.info("Adding plugin to playlist: %s" % details)
                try:
                    playlist.add_plugin(Plugin(plugin_name, self.plugins[plugin_name], details))
                except Exception as e:
                    self.logger.warn(e)
                    self.logger.warn("Failed to add %s found in playlist %s" % (plugin_name, playlist_file))

        self.logger.info("Created playlist of size %d" % playlist.get_size())
        return self.add_playlist(playlist)

    def add_plugin(self, plugin_name, plugin_object):
        self.logger.info("Adding plugin %s to the menu list" % plugin_name)
        self.plugins[plugin_name] = plugin_object
        config = {"size": self.surface_size}
        # This could throw an exception if the plugin cannot be configured (which
        #  is done in __init__ of Plugin
        try:
            self.all_plugins_playlist.add_plugin(Plugin(plugin_name, plugin_object, config))
        except Exception as e:
            self.logger.warn(e)
            self.logger.warn("Failed to add %s to the plugin model" % plugin_name)
        return None

    def add_plugins(self, plugins):
        self.logger.info("%s" % plugins)
        for plugin_name in sorted(plugins.keys()):
            self.add_plugin(plugin_name, plugins[plugin_name])
        return None

    def __str__(self):
        string = "PluginModel\n"
        if self.current_playlist is not None:
            string += "Current Playlist: #%d @ %d\n" % (
            self.current_playlist.playlist_number, self.current_playlist.current_position)
        else:
            string += "<No current playlist>\n"
        if self.playlists is not None:
            for playlist in self.playlists:
                string += "%s" % playlist
        return string


class PluginPlaylist(object):
    _ids = count(0)

    ALL = 0
    USER = 1

    states = ["STOPPED", "RUNNING", "PAUSED"]
    loop_modes = ["LOOP", "ONCE"]

    logger = logging.getLogger(__name__)

    def __init__(self, playlist_type=1):
        self.plugins = []
        self.playlist_type = playlist_type
        self.playlist_number = next(self._ids)
        self.logger.info("Creating playlist #%d", self.playlist_number)
        self._reset_playlist_state()

        if self.playlist_type == self.ALL:
            self.auto_advance = False
        else:
            self.auto_advance = True

        self.total_pause_time = 0
        self.previous_pause_time = None

        self.loop_mode = "LOOP"

        pass

    def _reset_playlist_state(self):
        self.current_position = -1
        self.state = "STOPPED"

    def add_plugin(self, plugin):
        self.plugins.append(plugin)
        return len(self.plugins)-1

    # Two sets of access methods.
    # 1: For when the playlist is running, and handles moving between
    #  the plugins.
    # 2: For looking at what is in the playlist


    # Playlist running methods
    def get_current_plugin(self):

        # Trigger the playlist to start playing
        if self.current_position == -1:
            self.logger.info("Starting the playlist")
            self.state = "RUNNING"
            return self.next()

        current_plugin = self.plugins[self.current_position]

        if self.auto_advance == True:
            # If the plugin has run its duration, then move to the next one,
            #TODO: Add in code to check for the playlist being paused
            if self.state == "RUNNING":
                plugin_duration = current_plugin.get_duration()
                plugin_duration_so_far = pygame.time.get_ticks() - self.current_plugin_start_time

                if self.loop_mode == "LOOP" or self.current_position < len(self.plugins) - 1:
                    if plugin_duration_so_far > plugin_duration:
                        self.logger.info("Plugin has exceeded intended duration")
                        current_plugin = self.next()
                else:
                    pass

        return current_plugin


    def next(self):
        # Reset the pause time
        self.total_pause_time = 0

        self.logger.info("Getting next plugin in the playlist")
        if len(self.plugins) == 0:
            return None
        if not self.is_running():
            self.resume()

        current_plugin = self.plugins[self.current_position]
        # Don't bother iterating through plugins if there
        #  is only one. Leave it running so that it isn't
        #  continually reconfigured and restarted
        if len(self.plugins) > 0:
            self.current_position += 1
            if self.current_position >= len(self.plugins):
                self.current_position = 0

            self.logger.info("We need to start a new plugin")
            current_plugin = self.start_plugin(self.current_position)

        return current_plugin

    def start_plugin(self, index):
        self.logger.info("start_plugin(%d)" % (index))
        new_plugin = self.plugins[index]

        # The plugin may not have been re-created, so
        #  we need to reset it
        new_plugin.reset()
        # Make a note when this plugin started
        self.current_plugin_start_time = pygame.time.get_ticks()

        self.resume()
        new_plugin.start()
        self.current_position = index
        return new_plugin


    def previous(self):
        pass

    def pause(self):
        self.previous_pause_time = pygame.time.get_ticks()
        self.total_pause_time = 0
        self.state = "PAUSED"
        pass

    def resume(self):
        if self.previous_pause_time != None:
            self.total_pause_time += pygame.time.get_ticks() - self.previous_pause_time
        self.previous_pause_time = None
        self.state = "RUNNING"
        if self.current_position == -1:
            if len(self.plugins) > 0:
                self.current_position = 0
        return None

    def is_running(self):
        return (self.state == "RUNNING")

    # Playlist interrogation methods
    def get_plugins(self):
        # Sort the plugins by plugin name
        #return sorted(self.plugins, key=lambda plugin: plugin.plugin_name)
        return self.plugins

    def get_current_plugin_info(self):
        info = dict()
        current_plugin = self.plugins[self.current_position]
        info["obj"] = self.plugins[self.current_position]
        info["name"] = self.plugins[self.current_position].plugin_name
        info["index"] = self.current_position
        info["start_time"] = self.current_plugin_start_time
        return info

    def get_plugin_remaining_time(self):
        current_plugin = self.plugins[self.current_position]

        plugin_duration = current_plugin.get_duration()
        plugin_duration_so_far = pygame.time.get_ticks() - self.current_plugin_start_time

        pause_time = self.total_pause_time
        if self.previous_pause_time != None:
            pause_time += pygame.time.get_ticks() - self.previous_pause_time

        return plugin_duration - plugin_duration_so_far + pause_time

    def get_current_plugin_index(self):
        return self.current_position

    def set_current_plugin_by_index(self, index):
        if index >= len(self.plugins):
            # This is out of range
            return None
        return self.start_plugin(index)

    def get_size(self):
        return len(self.plugins)

    def draw_splash(self, canvas):
        # Dark blue background
        canvas.set_colour((0, 0, 0xFF))
        # Draw white lines every other pixel
        even_colour = (0xFF, 0xFF, 0xFF)
        odd_colour = (0x80, 0x80, 0x80)
        for i in range(len(self)):
            colour = odd_colour
            if i % 2 == 0:
                colour = even_colour
            canvas.draw_line(6, 4 + i, canvas.get_width() - 5, 4 + i, colour)
        # Draw the playlist number at the bottom left
        canvas.draw_text("%d" % self.playlist_number, (0xFF, 0xFF, 0xFF), 0, 10)
        return canvas

    def __str__(self):
        string = "PluginPlaylist #%s : %s\n" % (self.playlist_number, self.state)
        for idx, plugin in enumerate(self.get_plugins()):
            if (idx == self.current_position):
                string += " >%s\n" % plugin
            else:
                string += "  %s\n" % plugin
        return string

    def __len__(self):
        return len(self.plugins)


class Plugin(object):
    logger = logging.getLogger(__name__)

    types = ["VisualisationPlugin", "GamePlugin"]

    DEFAULT_DURATION = 5000

    def __init__(self, plugin_name, plugin_object, config=None):
        self.plugin_name = plugin_name
        self.plugin_object = plugin_object
        self.instance = plugin_object()
        self.configure(config)
        pass

    def configure(self, config):
        self.config = config
        self.instance.configure(self.config)
        return None

    def reset(self):
        if self.config is not None:
            self.instance.configure(self.config)
        return None

    def start(self):
        self.instance.start()
        return None

    def get_duration(self):
        if self.config is None:
            return self.DEFAULT_DURATION

        # Get the duration from the config
        duration = self.DEFAULT_DURATION
        try:
            duration = 1000 * int(self.config["duration"])
        except (AttributeError, ValueError, KeyError):
            pass
        return duration

    def get_type(self):
        if isinstance(self.instance, VisualisationPlugin):
            return "VisualisationPlugin"
        elif isinstance(self.instance, GamePlugin):
            return "GamePlugin"
        else:
            return "UnknownPlugin"

    def get_plugin_type(self):
        return "VisualisationPlugin"

    def get_plugin_object(self):
        return self.instance

    def get_plugin_type(self):
        pass

    def draw_splash(self, canvas):
        if self.instance is not None:
            return self.instance.draw_splash(canvas)
        return None

    def __str__(self):
        return "%s - %s" % (self.get_type(), self.plugin_name)

