__authors__ = ['Joel Wright','Mark McArdle']

class TestPlugin(object):
    def configure(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

class PluginRegistry(object):
    def __init__(self):
	self.__registry__ = {}

    def register(self, name, item):
        self.__registry__[name] = item

    def values(self):
        return self.__registry__.values()

    def items(self):
        return self.__registry__.items()
