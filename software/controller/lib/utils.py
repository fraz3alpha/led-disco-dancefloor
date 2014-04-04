__authors__ = ['Joel Wright']

class ColourUtils(object):
	@staticmethod
	def tupleToHex(rgb_tuple):
		"""
		Convert an (R, G, B) tuple to hex #RRGGBB
		"""
		hex_colour = '#%02x%02x%02x' % rgb_tuple
		return hex_colour

	@staticmethod
	def hexToTuple(hex_colour):
		"""
		Convert hex #RRGGBB to an (R, G, B) tuple
		"""
		hex_colour = hex_colour.strip()
		if hex_colour[0] == '#':
			hex_colour = hex_colour[1:]
		if len(hex_colour) != 6:
			raise ValueError, "input #%s is not in #RRGGBB format" % hex_colour
		(rs,gs,bs) = hex_colour[:2], hex_colour[2:4], hex_colour[4:]
		r = int(rs, 16)
		g = int(gs, 16)
		b = int(bs, 16)
		return (r,g,b)
