__authors__ = ['Joel Wright']

from plugins_base import TestPlugin

class TestPlugin1(TestPlugin):
    __name__ = "TestPlugin1"
    __version__ = 0.01
    
    def __init__(self):
        self.initialised = True
    
    def config(self):
        self.configured = True

    def start(self):
        print("Started TestPlugin1")

    def stop(self):
        print("Stopped TestPlugin1")

