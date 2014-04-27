__authors__ = ['Andrew Taylor']

from datetime import datetime


class Logger(object):

	# Default logging levels
	active_logging_levels = ['silent', 'warn', 'error', 'info']

	@staticmethod
	def set_logging_level(level):
		if (level not in Logger.get_logging_order()):
			print ("Invalid logging level: '%s'" % (level))
			return

		Logger.active_logging_levels = []

		# Add all the valid logging levels, up to and including
		#  the level we asked for 
		for ordered_level in Logger.get_logging_order():
			Logger.active_logging_levels.append(ordered_level)
			if ordered_level == level:
				break

	@staticmethod
	def get_active_logging_levels():
		return Logger.active_logging_levels

	@staticmethod
	def get_logging_order():
		return ['silent', 'warn', 'error', 'info', 'verbose']

	@staticmethod
	def warn(category, message):
		if "warn" in Logger.active_logging_levels:
			Logger._print("Warn", category, message)

	@staticmethod
	def error(category, message):
		if "error" in Logger.active_logging_levels:
			Logger._print("Error", category, message)

	@staticmethod
	def info(category, message):
		if "info" in Logger.active_logging_levels:
			Logger._print("Info", category, message)

	@staticmethod
	def verbose(category, message):
		if "verbose" in Logger.active_logging_levels:
			Logger._print("Verbose", category, message)

	@staticmethod
	def _print(level, category, message):
		print ("%s %s %s :  %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), level.ljust(7), category, message))
