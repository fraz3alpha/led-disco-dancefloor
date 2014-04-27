
class VisualisationPlugin(object):

	"""
	Called just before starting a plugin
	"""
	def configure(self):
		print ("This plugin doesn't have a configure() method")

	"""
	Called in a loop to update the display, draw_frame is where most of the 
	 time goes, and should also include a call to limit the frame rate to an
	 appropriate value. 25 fps is ample.
	"""
	def draw_frame(self, canvas):
		print ("This plugin has failed to implement update_surface(canvas)")
		return None

	"""
	In some cases the plugin may be asked to display a splash screen, for example
	 when a user is flicking through the available catalogue of plugins. As 
	 pixel real estate is at a premium, it isn't possible to write out the name
	 of the plugin, so this is available to draw something representitive of the 
	 plugin
	"""
	def draw_splash(self, canvas):
		print ("This plugin doesn't have a splash screen")

	"""
	If a plugin wants to consume a keyboard or controller input event,
	 then it should override this method and return None to indicate that
	 no further processing should be done
	"""
	def handle_event(self, e):
		return e

	"""
	Some plugins might have specific things they need to do when they start,
	 for example, start a thread, or load other resources
	Called after a plugin is about to be switched to. This means that previously 
	 another plugin was showing, or nothing was. It is possible that a plugin object
	 is re-used, in which case this will allow a plugin to reset, or it might be never
	 started, maybe if the splash screen is displayed but the plugin is not chosen
	"""
	def start(self):
		pass

	"""
	If a plugin starts a thread, it should stop that when requested, but most
	 plugins probably don't have anything specific to do when they finish.
	Called after this plugin has been running, but will no longer be asked to
	 display any more frames
	"""
	def stop(self):
		pass

	"""
	If a plugin cares that it isn't being displayed for a while, it can implement
	 pause and choose to stop its internal timer. Resume will be called when it is 
	 being displayed again
	"""
	def pause(self):
		pass

	"""
	Called after a previous call to pause, resume indicates that the plugin will be
	 asked to draw something soon, and it might want to consider getting things in order.
	Alternatively, the next call to draw_frame could automatically bring a plugin out of
	 pause state
	"""
	def resume(self):
		pass
