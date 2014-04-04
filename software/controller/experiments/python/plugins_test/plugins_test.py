__authors__ = ['Joel Wright','Mark McArdle']

import os
import sys
import importlib
from plugins_base import TestPlugin
from plugins_base import PluginRegistry

class TestMainPlugins(object):
    def __init__(self):
        self.__registry__ = PluginRegistry()
        self.__register_plugins("plugins")
        print("Registered Plugins %s" % self.__registry__.items())

    def __register_plugins(self, plugin_folder):
        """
        Find the loadable plugins in the given plugin folder.
        
        Returns:
            A list of plugins that can be loaded.
        """
        print("Searching for plugins in %s" % plugin_folder)
        plugins = []
        
        for root, dirs, files in os.walk(plugin_folder):
            for fname in files:
                if fname.endswith(".py") and not fname.startswith("__"):
                    fpath = os.path.join(root, fname)
                    mname = fpath.rsplit('.', 1)[0].replace('/', '.')
                    importlib.import_module(mname)
            
            for plugin in TestPlugin.__subclasses__():
                print("name: %s" % plugin.__name__)
                pinst = plugin()
                self.__registry__.register(pinst.__name__, pinst)


# Start the test
if __name__ == "__main__":
	test = TestMainPlugins()
