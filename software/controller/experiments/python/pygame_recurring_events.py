import pygame
import pygame.joystick
from pygame.locals import *

def main():
   pygame.init()
   clock = pygame.time.Clock()
   ue = pygame.event.Event(USEREVENT, {'code':'drop'})
   pygame.time.set_timer(USEREVENT+3, player="2", 500)
   pygame.time.set_timer(USEREVENT+3, player="1", 500)
   while(True):
      events = pygame.event.get()
      for e in events:
         print(e)
      clock.tick(2)

if __name__ == "__main__":
   main()
