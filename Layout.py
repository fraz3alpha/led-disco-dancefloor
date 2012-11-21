__author__ = 'Joel Wright'

import gtk
from DDRPi import Plugin

class DisplayLayout(gtk.Window, Plugin):
    def __init__(self):
        super(DisplayLayout, self).__init__()

    def config(self, config, image_surface):
        """
        This is an example of an end user module - need to make sure we can get the main image surface and config
        to write to them both...
        """
        self.ddrpi_config = config
        self.ddrpi_surface = image_surface

    def start(self):
        """
        Start writing to the surface
        """

    def stop(self):
        """
        Stop writing to the surface, de-register callbacks
        """

    def on_timer(self):
        # add this
        return False


