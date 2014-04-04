from Tkinter import *
import config

# Create a suitably sized empty canvas
def get_blank_canvas(x,y):
  # Shorthand for creating a 2d array, x by y.
  blank_canvas = [[0]*y for i in xrange(x)]
  print_canvas(blank_canvas)
  return blank_canvas

def print_canvas(canvas_map):
  width = len(canvas_map)
  height = len(canvas_map[0])
  for y in range(height):
    for x in range(width):
      print "%03d" % canvas_map[x][y],
    print
#  for y in range(len(canvas_map)):
#    for x in range(len(canvas_map[y])):
#      print "%03d" % canvas_map[y][x],
#    print

config_data = config.load()

max_x = 0;
max_y = 0;

# Find out the maximum constraints of this setup
for module, module_data in config_data["modules"].items():
  this_max_x = module_data["x_position"] + module_data["width"]
  this_max_y = module_data["y_position"] + module_data["height"]
  if (this_max_x > max_x):
    max_x = this_max_x
  if (this_max_y > max_y):
    max_y = this_max_y

print "Extents: %d, %d" % (max_x, max_y)
# The number of elements is one greater than the max extent index
canvas_map = get_blank_canvas(max_x, max_y)

master = Tk()
master.title("LED Disco Dance Floor Controller")

# The height and width of each cell
display_cell_size = 20

canvas_width = display_cell_size * max_x
canvas_height = display_cell_size * max_y

w = Canvas(master, width=canvas_width, height=canvas_height)
w.pack()

# Create a rectangle to form the solid colour of the background
background = w.create_rectangle(0, 0, 500, 500, fill="black")

# The cell count
count = 0

# Draw each module from the config file
for module, module_data in sorted(config_data["modules"].items()):
  # Calculate the limits of the module
  border_x  = module_data["x_position"] * display_cell_size
  border_y  = module_data["y_position"] * display_cell_size
  border_x1 = (module_data["x_position"]+module_data["width"]) * display_cell_size
  border_y1 = (module_data["y_position"]+module_data["height"]) * display_cell_size

  # Draw each cell of the module
  for x in range(module_data["x_position"], module_data["x_position"]+module_data["width"]):
    for y in range(module_data["y_position"], module_data["y_position"]+module_data["height"]):
      w.create_rectangle(x*display_cell_size, 
                         y*display_cell_size, 
                         x*display_cell_size+display_cell_size,
                         y*display_cell_size+display_cell_size, 
                         fill="red", outline="white")

  # Start at the origin
  if (module_data["direction"] == "x"):
    print "Module %d increases along %s" % (module, module_data["direction"])
    # Work out if we need to go forwards or backwards along each axis
    # Left to right?
    x_direction = 1
    if (module_data["x_origin"] == module_data["x_position"]):
      x_direction = 1
    else:
      x_direction = -1

    # Top to bottom?
    y_direction = 1
    if (module_data["y_origin"] == module_data["y_position"]):
      y_direction = 1
    else:
      y_direction = -1
    


    print "  x increment: %d, y increment: %d" % (x_direction, y_direction)
    x_from = module_data["x_origin"]
    x_to = module_data["x_origin"] + module_data["width"]
    if (x_direction == -1):
      x_from = module_data["x_origin"]
      x_to = module_data["x_origin"] - module_data["width"]
    
    y_from = module_data["y_origin"]
    y_to = module_data["y_origin"] + module_data["height"]
    if (y_direction == -1):
      y_from = module_data["y_origin"]
      y_to = module_data["y_origin"] - module_data["height"]
    
    for y in range(y_from, y_to, y_direction):
      for x in range(x_from, x_to, x_direction):
        w.create_text(x*display_cell_size+ display_cell_size/2, y*display_cell_size + display_cell_size/2, text=count, fill="white", font=("Helvectica",6))
        # Make a note of which cell is in which position
        canvas_map[x][y] = count
        count = count+1

  else:
    print "Module %d increases along %s" % (module, module_data["direction"])
    # Work out if we need to go forwards or backwards along each axis
    # Left to right?
    x_direction = 1
    if (module_data["x_origin"] != module_data["x_position"]):
      x_direction = -1

    # Top to bottom?
    y_direction = 1
    if (module_data["y_origin"] != module_data["y_position"]):
      y_direction = -1
    
    print "  x increment: %d, y increment: %d" % (x_direction, y_direction)
    x_from = module_data["x_origin"]
    x_to = module_data["x_origin"] + module_data["width"]
    if (x_direction == -1):
      x_from = module_data["x_origin"]
      x_to = module_data["x_origin"] - module_data["width"]
    
    y_from = module_data["y_origin"]
    y_to = module_data["y_origin"] + module_data["height"]
    if (y_direction == -1):
      y_from = module_data["y_origin"]
      y_to = module_data["y_origin"] - module_data["height"]

    for x in range(x_from, x_to, x_direction):
      for y in range(y_from, y_to, y_direction):
        w.create_text(x*display_cell_size+ display_cell_size/2, y*display_cell_size + display_cell_size/2, text=count, fill="white", font=("Helvectica",6))
        canvas_map[x][y] = count
        count = count+1

  # Draw the outline and the name of the module in the origin cell
  w.create_rectangle(border_x,border_y,border_x1,border_y1,outline="yellow")

  origin_x  = module_data["x_origin"] * display_cell_size
  origin_y  = module_data["y_origin"] * display_cell_size
  origin_x1 = (module_data["x_origin"]+1) * display_cell_size
  origin_y1 = (module_data["y_origin"]+1) * display_cell_size

  w.create_oval(origin_x+2, origin_y+2, origin_x1-2, origin_y1-2, fill="purple", outline="purple")

  w.create_text(origin_x + display_cell_size/2, origin_y + display_cell_size/2, text=module, fill="white")

print ""
print "The pixels are arranged as follows:"
print_canvas(canvas_map)

mainloop()
