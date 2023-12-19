from dependencies.CustomStructures import Vector, Colour

#Colours for UI
COLOURS = {
    "bgcol": Colour(rgb=(13, 13, 13)),
    "white": Colour(rgb=(231, 230, 230)),
    "dark_grey": Colour(rgb=(28, 28, 28)),
    "light_grey": Colour(rgb=(64, 64, 64)),
}

SCREEN_SIZE = Vector(1280, 720)
PIXEL_COUNT = 300
FPS = 60
TIMELINE_DURATION = 30

# Server related stuff
OFFLINE_MODE = True
HOST_ADDRESS = "169.254.90.8" #Laptop : "192.168.1.97" RPi: "169.254.90.8"
PORT = 54231

# External files
SAVE_FILE_NAME = "nodes.json" # This is the file name saved when "s" is presssed
LOAD_FILE_NAME = "nodes.json" # This file is loaded when the program is opened
