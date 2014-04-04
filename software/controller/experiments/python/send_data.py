import serial
import threading
import os

# One module is 4' x 3' = 8 x 6 cells = 48 LEDs
# 3 bytes per LED
# 144 bytes per module
# 10 modules
# 1440 bytes / frame

def send_data(data_buffer):
#  print data_buffer
#  ser.write("0")
  for i in data_buffer:
    ser.write(chr(i%256))
  ser.write(chr(1))
  return

def clear():
  
  ser.write

def get_blank_buffer():
  blank_buffer = []
  for i in range(1440):
    blank_buffer.append(0)
  return blank_buffer

ser = serial.Serial('/dev/ttyUSB0', 1000000, timeout=1)
print ser

data_buffer = get_blank_buffer();

def screen_refresh():
  os.system('clear')
#  threading.Timer(0.038, screen_refresh).start()
  while 1:
    send_data(data_buffer)
  
screen_refresh()

update_number = 0

def screen_update():
  global update_number
  global data_buffer
  update_number = update_number+1
  for i in range(1440):
    data_buffer[i] = update_number
  print "Update "+str(update_number)
  threading.Timer(0.05, screen_update).start()
  
  

#screen_update()
