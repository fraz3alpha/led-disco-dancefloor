import sys,os

# set SDL to use the dummy NULL video driver, 
#   so it doesn't need a windowing system.
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame

from pygame.locals import * 
 
pygame.init() 

surface = pygame.Surface((20,10), 0, 24)
print surface

background_color = 0,0,255
surface.fill(background_color)

# Get the PixelArray, which will lock the screen
pxarray = pygame.PixelArray(surface)

# print out a pixel array value
for y in range(10):
  for x in range(10):
    print "%d " % pxarray[x][y],
  print ""
print ""

# The PixelArray must be explicity unloaded in order to unlcok the screen.
# You are required to unlock the screen before doing any blit operations
pxarray = None

myfont = pygame.font.SysFont("monospace", 8)
label = myfont.render("|!", 1, (0,0,0))
surface.blit(label, (0, 0))

# Get the PixelArray, which will lock the screen
pxarray = pygame.PixelArray(surface)

# print out a pixel array value
for y in range(10):
  for x in range(20):
    #print "%d %d %d, " % (pxarray[x][y], pxarray[x][y], pxarray[x][y]),
    print "%d, " % (pxarray[x][y]),
  print ""
print ""

pxarray = None
 
def input(events): 
   for event in events: 
      if event.type == QUIT: 
         sys.exit(0) 
      else: 
         print event 
 
while True: 
   input(pygame.event.get()) 
