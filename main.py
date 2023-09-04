from CreateObjects import *
from settings import *
import NewObjects as no
from StripCompressor import *
from dependencies.CustomServer import Sender
 
# Initialize Pygame
pygame.init()

# Set up the display
win = pygame.display.set_mode((SCREEN_SIZE.x, SCREEN_SIZE.y))
pygame.display.set_caption("My Pygame Window")

root_layer = Layer("root layer")

strip_preview = StripPreview("strip preview", PIXEL_COUNT, win)

node_editor = NodeEditor("node editor", win, strip_preview)
node_editor.create_UI()
transition_editor = TransitionEditor("transition editor", win, strip_preview)
transition_editor.create_UI()

timeline_layer = TimelineEditor("timeline", win, node_editor, transition_editor, strip_preview)
timeline_layer.create_UI()

root_layer.add_child(strip_preview)
root_layer.add_child(timeline_layer)
root_layer.add_child(node_editor)
root_layer.add_child(transition_editor)
root_layer.set_visibility(True)

node_editor.set_visible(False)
transition_editor.set_visible(False)

set_positions = False

#Pixel test
# for pixel_i, pixel in enumerate(strip_preview.pixels):
#     if pixel_i % 2 == 0:
#         pixel.set_rgb((255, 0, 0))

# Set up connection with server
if OFFLINE_MODE == False:
    sender = Sender(HOST_ADDRESS, PORT, debug_mode=False)
    compressor = StripCompressor(PIXEL_COUNT)


# Set up the game clock
clock = pygame.time.Clock()
frame = 0

# Set up the game loop
running = True
while running:
    events = pygame.event.get()
    mpos = pygame.mouse.get_pos()

    # Handle events
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t: pass

    win.fill(COLOURS["bgcol"].get_rgb()) # fill the screen with white

    # Draw game objects
    
    root_layer.draw()
    root_layer.update(events)

    if OFFLINE_MODE == False and frame % 10 == 0:
        message = compressor.serialise_strip_from_numpy(strip_preview.pixels)

        sender.send_message(message)  

    # Update the display
    pygame.display.update()

    frame += 1
    # Wait for the next frame
    clock.tick(60) # limit the frame rate to 60 fps

# Quit Pygame
pygame.quit()

if OFFLINE_MODE == False:
    sender.close()