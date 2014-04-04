import pygame
import pygame.joystick
from pygame.locals import *

def main():
   pygame.init()
   count = pygame.joystick.get_count()
   controllers = {}
   print("Number of controllers attached: %s" % count)
   for i in range(0,count):
		controllers[i] = pygame.joystick.Joystick(i)
		controllers[i].init()
   while(True):
      events = pygame.event.get()
      for e in events:
         try:
            x = e.axis
            if x is not None:
					# Ignore higher indexed axes on complex controllers
					if not x > 1:
                  print("%s" % e)
         except Exception as ex:
            print("%s" % e)

if __name__ == "__main__":
   main()

