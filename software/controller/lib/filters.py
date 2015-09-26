__author__ = 'Andrew Taylor'

class Filter(object):

    def __init__(self, config=None):
        self.config = config

    """
    Method to override to modify the value of the RGB data.
    Default here is no modification
    """
    def modify(self, rgb):
        return rgb

class ClearFilter(Filter):

    """
    The same RGB value is returned
    """
    def modify(self, rgb):
        return rgb

class NegativeFilter(Filter):

    """
    RGB value is returned as the opposite
    """
    def modify(self, rgb):
        return rgb ^ 0xFFFFFF

class NeutralDensityFilter(Filter):

    def __init__(self, config=None):
        self.factor = 1

    """
    Reduce the intensity of the value by the prescribed factor
    """
    def modify(self, rgb):
        red = (rgb >> 16) & 0xFF
        green = (rgb >> 8) & 0xFF
        blue = rgb & 0xFF

        # scale the values
        red = red / self.factor
        green = green / self.factor
        blue = blue / self.factor

        # Reconstruct and return the RGB value
        rgb = ((red & 0xFF) << 16) + ((green & 0xFF) << 8) + (blue & 0xFF)
        return rgb