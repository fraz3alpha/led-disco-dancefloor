# For getting an unbuffered write
import sys
# For getting the time
import time
# For threading
import threading

class ControllerInputListener():

  def new_controller_input(self, controller_input, channel, value):
    raise NotImplementedError("new_controller_input(channel, value) not implements")

class ControllerInput(threading.Thread):

  listeners = set()

  def __init__(self):
    self.keep_running = 1
    threading.Thread.__init__(self)
    self.start()

  def addControllerInputListener(self, listener):
    self.listeners.add(listener)

  def removeControllerInputListener(self, listener):
    if (listener in self.listeners):
      self.listeners.remove(listener)

  def notifyListeners(self, channel, value):
    for listener in self.listeners:
      listener.new_controller_input(self, channel, value)

  def get_nice_name(self, channel):
    if (channel == 0x0100):
      return "X"
    if (channel == 0x0101):
      return "A"
    if (channel == 0x0102):
      return "B"
    if (channel == 0x0103):
      return "Y"
    if (channel == 0x0104):
      return "LB"
    if (channel == 0x0105):
      return "RB"
    if (channel == 0x0108):
      return "Select"
    if (channel == 0x0109):
      return "Start"
    if (channel == 0x0200):
      return "LeftRight"
    if (channel == 0x0201):
      return "UpDown"

  def run(self):

    pipe = open('/dev/input/js0', 'r')

    data_buffer = []

    while (self.keep_running == 1):
      for char in pipe.read(1):
        data_buffer.append(ord(char))
        if (len(data_buffer) == 8):
          time_system = int(round(time.time() * 1000))
          time_controller = data_buffer[0] + (data_buffer[1] << 8) + (data_buffer[2] << 16) + (data_buffer[3] << 24)
          # print "Controller time    : %d" % (time_controller)

          input_data = (data_buffer[5] << 8) + (data_buffer[4])
          # Get the value (1 = pressed, 0 = released, on an axis it goes -1/+1 to give direction and 0 for released)
          input_value = input_data & 0x7FFF
          # If it is negative, convert it to a signed number
          if (input_value & 0x4000):
            input_value -= 0x8000
  
          input_state = (input_data >> 15) & 0x1
         
          data_type = (data_buffer[6] >> 7) & 0x1
          input_type = data_buffer[6] & 0x7F
          input_channel = data_buffer[7]

          input_id = (input_type << 8) + input_channel

          if (data_type == 1):
            #print "Data packet - type: %d channel: %d" % (input_type, input_channel)
            data_buffer = []
            continue

          #print "InputID: 0x%04X , value %d" % (input_id, input_value)

          self.notifyListeners(input_id, input_value)

          sys.stdout.flush()
          data_buffer = []

    print "Shutting down Controller input"
    pipe.close()

  def stop_running(self):
    print "Requesting shutdown"
    self.keep_running = 0

class DummyProgram(ControllerInputListener):

  plugins = []
  current_plugin = -1

  def __init__(self):
    self.plugins.append("Tetris")
    self.plugins.append("Pong")
    self.plugins.append("Pacman")
    self.current_plugin = 0

  def list_current_plugin(self):
    if (self.current_plugin == -1):
      print "No plugin selected"
    else:
      print "Current plugin is %s" % (self.plugins[self.current_plugin])

  def new_controller_input(self, controller_input, channel, value):
    print "Channel: %s , value %d" % (controller_input.get_nice_name(channel), value)
    # Iterate through the list when the Select button is pressed down
    if (controller_input.get_nice_name(channel) == "Select" and value == 1):
      self.current_plugin += 1
      if (self.current_plugin >= len(self.plugins)):
        if (len(self.plugins) > 0):
          self.current_plugin = 0
        else:
          self.current_plugin = -1
      self.list_current_plugin()

      

d = DummyProgram()
d2 = DummyProgram()
c = ControllerInput()
c.addControllerInputListener(d)
#c.addControllerInputListener(d2)
time.sleep(10)
c.stop_running()
time.sleep(5)


