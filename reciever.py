
import pygame
import numpy as np
from settings import *
from CreateObjects import *
from dependencies.CustomServer import Server
from StripCompressor import *

pygame.init()

compressor = StripCompressor(PIXEL_COUNT)

def handle_data(message):

    for packet in compressor.break_packets(message):
        strip_preview.pixels = np.array(packet)

win = pygame.display.set_mode((SCREEN_SIZE.x, SCREEN_SIZE.y))


# Set up the game clock
clock = pygame.time.Clock()

server = Server(HOST_ADDRESS, PORT, handle_data, debug_mode=False)
server.start_server()

strip_preview = StripPreview("strip preview", PIXEL_COUNT, win)


# Set up the game loop
running = True
while running:
    events = pygame.event.get()
    mpos = pygame.mouse.get_pos()

    # Handle events
    for event in events:
        if event.type == pygame.QUIT:
            running = False


    win.fill(COLOURS["white"].get_rgb())


    strip_preview.draw()
    
    # Update the display
    pygame.display.update()

    # Wait for the next frame
    clock.tick(60) # limit the frame rate to 60 fps

# Quit Pygame
pygame.quit()

server.close()