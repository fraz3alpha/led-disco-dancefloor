import serial
import Tkinter as tk
import threading
import time
import visual as v
import random

class ControllerInput(threading.Thread):

  conn = None
  last_data = None
  
  def __init__(self, port):
    self.conn = serial.Serial('/dev/ttyUSB0', 57600, timeout=0.1)
    threading.Thread.__init__(self)
    self.start()

  def get_last_data(self):
    return self.ast_data

  def run(self):
    running_buffer = ""
    while (1):
      # This doesn't work for some reason, bytes get read all out of order
      data = self.conn.read(size=1)
      if (data != None and data != "" and data != "\n"):
        print "%s" % data,
        running_buffer = ""

# Abstract class
class FloorOutput:

  def update(self, output_buffer):
    raise NotImplementedError("update() function not defined")


# Output to serial port
class SerialDanceFloorOutput(FloorOutput):
  conn = None

  def __init__(self, port):
    self.conn = serial.Serial(port, 1000000, timeout=1)

  def update(self, canvas):
    print "Writing output (%d bytes) to dance floor via serial port" % (len(canvas.get_buffer()))
    if (self.conn != None):
      # Make the data into a character stream
      output_stream = ""
      for data in canvas.get_buffer():
        output_stream += chr((data >> 16) & 0xFF)
        output_stream += chr((data >> 8 ) & 0xFF)
        output_stream += chr((data      ) & 0xFF)
      # Terminate the stream with a sync byte
      output_stream += chr(1)
      self.conn.write(output_stream) 

class VisualDanceFloorOutput(FloorOutput):

  width = 0
  height = 0

  mid_width = 0
  mid_height = 0

  data_sprites = []

  def __init__(self, floor_width, floor_height):

    scene = v.display(title='9DOF Razor IMU test',x=0, y=0, width=500, height=200,center=(0,0,0), background=(0,0,0))
    self.mid_height = floor_height/2.0
    self.mid_width = floor_width/2.0
    print "Visual width=%d height=%d, mid_width=%f mid_height=%f" % (floor_width, floor_height, self.mid_width, self.mid_height)
    scene.range=(floor_width*2, floor_height*2, 1)
    # All future additions (which are done by creating objects) will go into this scene
    scene.select()

    self.width = floor_width
    self.height = floor_height

    # Create a set of boxes to represent the tiles, and store them in an array so that we can
    #  change their colours later using update()
    for i in range(floor_height):
      for j in range(floor_width):
        # Attempt to center the data
        self.data_sprites.append(v.box(pos=(i-self.mid_height,j-self.mid_width,0), size=(1,1,1), color=(1,1,1)))

  # Parse RGB colours in the range 0.0 to 1.0 from the data to set the coloured blocks
  def update(self, canvas):
    canvas_buffer = canvas.get_buffer()
    for index in range(len(canvas_buffer)):
      data = canvas_buffer[index]
      red   = float(((data >> 16) & 0xFF)) / 255.0
      green = float(((data >> 8 ) & 0xFF)) / 255.0
      blue  = float(((data      ) & 0xFF)) / 255.0
      # print "%06X = %.2f %.2f %.2f" % (data, red, green, blue)
      self.data_sprites[index].color=(red, green, blue)
    

# Output to terminal
class TextDanceFloorOutput(FloorOutput):

  def update(self, canvas):
    output_buffer = canvas.get_buffer()
    print "Writing output (%d bytes) to dance floor terminal" % (len(output_buffer))
    for y in range(canvas.get_height()):
      for x in range(canvas.get_width()):
        position = y * canvas.get_width() + x
#        print "Drawing %d,%d from %d" % (x,y, position)
        print "%06X, " % (output_buffer[position]),
      print

class DanceFloor:

  controller_input = None
  floor_outputs = {}
  canvas = None

  def __init__(self):
    self.controller_input = None
    self.floor_outputs = {}
    self.canvas = Canvas(6, 16)
    print "Dance Floor Ready"

  def set_controller_input(self, controller_port):
    self.controller_input = ControllerInput(controller_port)

  def set_floor_output(self, floor_output):
    self.floor_outputs = {}
    add_floor_output(floor_output)

  def add_floor_output(self, floor_output):
    self.floor_outputs[floor_output] = 1;

  def get_canvas(self):
    return self.canvas

  def update(self):

    for output, enabled in self.floor_outputs.items():
      if (enabled == 1):
        output.update(self.canvas)

class Canvas:

  height = 0
  width = 0
  data = []
  random_colours = []
  
  COLOUR_BLACK = 0x00

  def __init__(self, width, height):
    self.height = height
    self.width = width
    self.data = []
    for i in range(height * width):
      self.data.append(self.COLOUR_BLACK)
    print "Canvas %s x %s" % (height, width)
    
    self.random_colours.append(0xFF0000) # Red
    self.random_colours.append(0x00FF00) # Green
    self.random_colours.append(0x0000FF) # Blue
    self.random_colours.append(0xFFFF00) # Yellow
    self.random_colours.append(0xFFFFFF) # White

  def get_buffer(self):
    return self.data

  def get_height(self):
    return self.height
 
  def get_width(self):
    return self.width

  def draw_random_pixel(self, x, y):
    self.draw_pixel(x,y, self.random_colours[random.randrange(len(self.random_colours))])

  def draw_pixel(self, x, y, colour):

    # print "Drawing pixel @ (%d, %d)" % (x, y)

    # Don't draw the pixel if it is off the edges
    if (x >= self.width or x < 0):
      return

    if (y >= self.height or y < 0):
      return

    position = (y*self.width) + x
 
    # print "Position = %d" % position
    self.data[position] = colour

  # This is probably not very efficient, but it works
  def draw_line(self, x_start, y_start, x_end, y_end, colour):

    # print "Drawing line from (%d, %d) to (%d, %d)" % (x_start, y_start, x_end, y_end)

    x_diff = x_end - x_start
    y_diff = y_end - y_start

    if (x_diff == 0 and y_diff == 0):
      self.draw_pixel(x_start, y_start, colour)
      return

    if (abs(x_diff) > abs(y_diff)):

      # Make the line be drawn in the direction of increasing x
      if (x_end < x_start):
        # print "Switching around the input"
        temp_x = x_end
        x_end = x_start
        x_start = temp_x
      
        temp_y = y_end
        y_end = y_start
        y_start = temp_y

      x_diff = x_end - x_start
      y_diff = y_end - y_start

      # print "Drawing line from (%d, %d) to (%d, %d)" % (x_start, y_start, x_end, y_end)

      grad = float(y_diff) / float(x_diff)
      # print "x Gradient is %f" % (grad)

      for x in range(x_start, x_end + 1):
        y = int(round((x - x_start) * grad + y_start))
        # print "x = %d , y = %d" % (x,y)
        self.draw_pixel(x,y,colour)
    else:

      # Make the line be drawn in the direction of increasing y
      if (y_end < y_start):
        # print "Switching around the input"
        temp_x = x_end
        x_end = x_start
        x_start = temp_x
      
        temp_y = y_end
        y_end = y_start
        y_start = temp_y

      x_diff = x_end - x_start
      y_diff = y_end - y_start

      grad = float(x_diff) / float(y_diff)
      # print "y Gradient is %f" % (grad)
      for y in range(y_start, y_end + 1):
        x = int(round((y - y_start) * grad + x_start))
        # print "x = %d , y = %d" % (x,y)
        self.draw_pixel(x,y,colour)      
 
  # Draw a rectangle. Fill = None for no fill
  def draw_rect(self, x_start, y_start, x_end, y_end, colour, fill):
    raise NotImplementedError("Function draw_rect() not implemented")

  def draw_text(self, text, font_size):
    raise NotImplementedError("Function draw_text() not implemented")

  def fill(self, colour):
    for i in range(len(self.data)):
      self.data[i] = colour


  def draw_union_jack(self):
    # Blue background
    self.fill(0x0000FF)
    # White cross
    self.draw_line(0,0, self.width - 1, self.height - 1, 0xFFFFFF)
    self.draw_line(self.width - 1, 0, 0, self.height - 1, 0xFFFFFF)

    self.draw_line(0,7, self.width-1, 7, 0xFF0000)
    self.draw_line(0,8, self.width-1, 8, 0xFF0000)

    self.draw_line(2,0, 2,self.height-1, 0xFF0000)
    self.draw_line(3,0, 3,self.height-1, 0xFF0000)

df = DanceFloor()

df.add_floor_output(TextDanceFloorOutput())
df.add_floor_output(VisualDanceFloorOutput(6, 16))
#df.add_floor_output(SerialDanceFloorOutput('/dev/ttyUSB0'))
#df.set_controller_input(ControllerInput('/dev/ttyUSB0'))


df.get_canvas().draw_union_jack()

df.update()
#df.get_canvas().draw_pixel(0,0, 0xFF)
#df.get_canvas().draw_line(5,1,5,1, 0xAA00)
#df.get_canvas().draw_line(0,0,15,5, 0xAA00)
#print
#df.update()

# Do a little random pixel colouring
while (1): 
  for i in range(6):
    for j in range(16):
      time.sleep(.1)
      df.get_canvas().draw_random_pixel(i,j)
      df.update()
    
