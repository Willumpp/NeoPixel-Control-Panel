from dependencies.UIElements import *
import pygame
from dependencies.CustomStructures import Colour
from dependencies.CustomObjects import *
import math
from settings import *

#This converts powerpoint coordinates to on screen coordinates
def ptc(x, y):
    return Vector(x/33.87 * SCREEN_SIZE.x, y/19.05 * SCREEN_SIZE.y)

'''
Rectangle class for the UI
    Just draws a rectangle with the designated background colour
    does not draw text
'''
class Rectangle(UIElement):
    def __init__(self, surface, xpos, ypos, width, height):
        super().__init__(surface, xpos, ypos, width, height)

    @UIElement.require_visible
    def draw(self):
        self._draw_background()
        self._draw_sprite()
        self._draw_border()

'''
Colour Picker class
When clicked it sets the colour to the colour of the sprite at the clicked pixel
'''
class ColourPicker(Button):
    def __init__(self, surface, xpos, ypos, width, height, colour_palette_dir, function, *args):
        super().__init__(surface, xpos, ypos, width, height, function)

        self.set_image(colour_palette_dir)
        self.last_colour = (0,0,0) #This will be changing when wheel is clicked
        self.args = args

    def call_event(self):
        _pos = pygame.mouse.get_pos()
        _last_colour = self.sprite_image.get_at((int(_pos[0] - self._pos.x), int(_pos[1] - self._pos.y)))
        self.last_colour = (_last_colour[0], _last_colour[1], _last_colour[2]) #Dont include the alpha value of the colour
        self.function(*self.args)

    #Returns the last colour selected
    def get_colour(self):
        return self.last_colour

    @UIElement.require_visible
    def draw(self):
        self._draw_border()
        self._draw_sprite()



'''
UI element for defining a bezier curve or linear graph etc.
    Idea is that it is interactable and editable by the user
    Transitions are changed with "set transition"
'''
class Transition(UIElement):

    def __init__(self, surface, xpos, ypos, width, height):
        super().__init__(surface, xpos, ypos, width, height)
        self.held = False

        self.valid_transitions = ["linear", "bezier", "none"]
        self.transition_type = "bezier"
        self.graph_colour = (255, 0, 0)

        self.bezier_point2 = Vector(0.5, 0.25)
        self.bezier_point2 = Vector(self.bezier_point2.x * self.size.x, self.bezier_point2.y * self.size.y)
        self.bezier_point3 = Vector(0.5, 0.75)
        self.bezier_point3 = Vector(self.bezier_point3.x * self.size.x, self.bezier_point3.y * self.size.y)

        self.start_colour = Colour()
        self.start_colour.set_rgb((255, 0, 0))
        self.end_colour = Colour()
        self.end_colour.set_rgb((0, 0, 255))
    
    #See "valid transitions" array for valid transitions
    #   transitions : string input of the transition name
    def set_transition(self, transition):
        #Transition validation
        if transition not in self.valid_transitions:
            raise Exception(f"Error; transition '{transition}' not in valid transitions: {self.valid_transitions}")
        
        self.transition_type = transition

    #Generalised form of a cubic bezier
    #   p1-p4 : vector points for the bezier curve
    def cubic_bezier(self, p1, p2, p3, p4, t):
        return (-t**3 + 3*t**2 - 3*t + 1) * p1 + (3*t**3 - 6*t**2 + 3*t) * p2 + (-3*t**3 + 3*t**2) * p3 + (t**3) * p4
        
    #Returns the value from 0-1 for the graph
    #   t : input value from 0-1 for x value
    #returns y value 0-1
    def get_value(self, t):
        if self.transition_type == "linear":
            return t
        elif self.transition_type == "bezier":
            #Perform bezier curve for all points. Start of curve is at 0, 0 but drawn relative to ui element
            _point = self.cubic_bezier(Vector(0, self.size.y), self.bezier_point2, self.bezier_point3, Vector(self.size.x, 0), t)
            return 1 - _point.y / self.size.y #Flip orientation of curve
        elif self.transition_type == "none":
            return 0

    @UIElement.require_visible
    def update(self, events=[]):        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos_vec = Vector(*mouse_pos)
        _bbox = self.get_bbox()

        #Call event if "held" down and mouse is in bounding box range
        if (self.held == True and self._pos.x < mouse_pos[0] < _bbox.x and self._pos.y < mouse_pos[1] < _bbox.y):
            if ((mouse_pos_vec - self._pos) - self.bezier_point2).get_mag() < 25:
                self.bezier_point2 = mouse_pos_vec - self._pos

            if ((mouse_pos_vec - self._pos) - self.bezier_point3).get_mag() < 25:
                self.bezier_point3 = mouse_pos_vec - self._pos

        #Mouse button detection
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.held = True

            if event.type == pygame.MOUSEBUTTONUP:
                self.held = False

    @UIElement.require_visible
    def draw(self):
        self._draw_background()
        self._draw_sprite()
        self._draw_border()

        #Draw interaction points
        if self.transition_type == "bezier":
            #Draw interaction circles
            pygame.draw.circle(self.surface, (0, 255, 0), (self.bezier_point2 + self._pos).get_pos(), 10)
            pygame.draw.circle(self.surface, (0, 0, 255), (self.bezier_point3 + self._pos).get_pos(), 10)
            
            #Draw lines to interaction circles
            pygame.draw.line(self.surface, (0, 255, 0), (self._pos + Vector(0, self.size.y)).get_pos(), (self.bezier_point2 + self._pos).get_pos())
            pygame.draw.line(self.surface, (0, 0, 255), (self._pos + Vector(self.size.x, 0)).get_pos(), (self.bezier_point3 + self._pos).get_pos())

        #Draw line
        _point_count = 100
        _last_point = (self._pos + Vector(0, self.size.y)) #Needed to draw a smooth curve
        for x in range(0, _point_count):
            y = self.get_value(x / _point_count)
            _point = (self._pos + Vector(self.size.x * x/_point_count, self.size.y * (1 - y)))

            #Draw line connecting last point to current point
            pygame.draw.line(self.surface, self.start_colour.lerp(self.end_colour, y).get_rgb(), _last_point.get_pos(), _point.get_pos(), width=4)
            # pygame.draw.circle(self.surface, self.graph_colour, _poin.get_pos(), 2) #Draw points rather than "smooth" line

            _last_point = _point

    
'''
Scroll bar class
    Can hold click on this UI element and it sets the progress of the bar
Progress can be get via "get_progress" and obviously set conversely
Also can assign a scroll "widget" which moves with the bar's progress
'''
class ScrollBar(UIElement):
    def __init__(self, surface, xpos, ypos, width, height, padding, function, widget=None, args=()):
        super().__init__(surface, xpos, ypos, width, height)

        self.function = function #function to call upon button press
        self.args = args #Arguments for "function"
        self.held = False #if the scroll bar is held down
        self._progress = 0 #progress the bar is along ; range 0 - 1
        self.widget = widget #UI element to move with the scroll bar's progress
        self.padding = padding #Padding on BOTH ends of the bounding box

        self.set_progess(0)

    def set_progess(self, progress):
        progress = min(1, progress)
        progress = max(0, progress)
        self._progress = progress


        #Move widget if assigned
        if self.widget != None:
            _size = self.widget.size
            self.widget.set_pos(self._pos.x + self.padding - _size.x + (progress * (self.size.x - self.padding)), self._pos.y + self.size.y/2 - 0.5 * _size.y) 


    
    def get_progress(self):
        #If widget is size of whole bar it is always 0
        if self.widget != None:
            if self.widget.size.x == self.size.x:
                return 0

        return self._progress

    #Calls the function in "function" attribute
    def call_event(self):
        self.function(*self.args)

    #Retuns if the scroll bar is "held" down
    def is_held(self):
        return self.held

    @UIElement.require_visible
    def draw(self):
        self._draw_background()
        self._draw_sprite()
        self._draw_border()
            
    @UIElement.require_visible
    def update(self, events=[]):        
        mouse_pos = pygame.mouse.get_pos()
        _bbox = self.get_bbox()
        _padding = self.padding / 2

        #Call event if "held" down and mouse is in bounding box range
        if self.held == True and self._pos.x + _padding < mouse_pos[0] < _bbox.x - _padding and self._pos.y < mouse_pos[1] < _bbox.y:
            self.set_progess((mouse_pos[0] - self._pos.x - _padding)/(self.size.x - self.padding))
            self.call_event()
        elif self.held == True and _bbox.x - _padding < mouse_pos[0] < _bbox.x and self._pos.y < mouse_pos[1] < _bbox.y:
            self.set_progess(1)
            self.call_event()
        elif self.held == True and self._pos.x < mouse_pos[0] < self._pos.x + _padding and self._pos.y < mouse_pos[1] < _bbox.y:
            self.set_progess(0)
            self.call_event()

        #Mouse button detection
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.held = True

            if event.type == pygame.MOUSEBUTTONUP:
                self.held = False

'''
Timeline UI component
Contains a scroll bar and widget
Draws a progressible UI thing. Hides any UI elements outside the bounding box
'''
class Timeline(UIElement):
    def __init__(self, surface, xpos, ypos, width, height, grid_x_increment, grid_y_increment, internal_width):
        self.scroll_bar_height = 30
        height -= self.scroll_bar_height

        super().__init__(surface, xpos, ypos, width, height)

        self.scroll_widget = Rectangle(self.surface, 0, 0, 0, self.scroll_bar_height)
        self.scroll_bar = ScrollBar(self.surface, self._pos.x, self._pos.y + self.size.y, self.size.x, self.scroll_bar_height, 0, self.scroll_function, widget=self.scroll_widget)

        self.camera = Camera(surface, xpos, ypos + height/2)
        self.camera.scale = 1 #this scales the timeline (almost like zooming in), higher number = greater zoom
        self.timeline_layer = Layer("timeline")
        self.timeline_layer.set_visible(True)

        # self.set_internal_width(internal_width)

        self.grid_increments = Vector(grid_x_increment, grid_y_increment) #Grid increments in x and y
        self.set_internal_width(internal_width)


    #Internal width is the size of the "canvas" that is the timeline
    #   all drawn objects are drawn relative to this "canvas"
    #   objects outside the internal width are not drawn
    #   width : the width of the "canvas"
    def set_internal_width(self, width):
        if width < self.size.x:
            raise Exception("Error; Invalid interal width. Needs to be equal to or larger than timeline width")

        self._internal_width = width * self.camera.scale
        
        # self.scroll_widget = None
        #Needed so the scroll bar adjusts with the timeline canvas size
        widget_width = self.size.x * self.size.x / (self._internal_width)
        self.scroll_widget.size.set_x(widget_width)
        self.scroll_bar.padding = widget_width
        
        self.scroll_bar.set_progess(0)

    def get_internal_width(self):
        return self._internal_width

    def set_visible(self, active):
        super().set_visible(active)
        self.timeline_layer.set_visibility(active)

    #Get the layer to draw timeline objects on
    def get_layer(self):
        return self.timeline_layer

    def scroll_function(self):
        pass
    
    #Returns the timeline layer for the ui
    def get_timeline_layer(self):
        return self.timeline_layer


    @UIElement.require_visible
    def update(self, events=[]):        
        self.scroll_bar.update(events)
        self.camera.update(events)
        # self.timeline_layer.update(events)

        self.camera.set_pos(self._pos.x + ((self._internal_width - self.size.x) * self.scroll_bar.get_progress()) + self.size.x/2, self._pos.y + self.size.y/2)

        #Control all objects in the timeline's layer
        _objects = self.timeline_layer.get_objects()
        for obj in _objects:
            #Get position of the object
            _pos = obj.get_screen_pos()

            #Hide/show objects based on their appearance in the timeline
            if self.collision_point(_pos):
                obj.set_visible(True)
            else:
                obj.set_visible(False)

        self.timeline_layer.update(events)


    @UIElement.require_visible
    def draw(self):
        self._draw_background()
        self._draw_sprite()
        self._draw_border()

        #Draw grid
        second = -1
        x_increment, y_increment = self.grid_increments.get_pos()
        for i in range(int(self._pos.x), int(self._pos.x + self._internal_width)): #Loop till the end of the canvas
            #Draw grid lines relative to the camera
            xpos = (i * self.camera.scale - self.camera.get_pos().x + self.size.x / 2)

            if i % x_increment == 0:
                second += 1

            #Dont draw line if outside range of timeline
            if not (self._pos.x < xpos < self._pos.x + self.size.x):
                continue
        
            #Number incremental grid line
            if i % x_increment == 0:
                #Every second
                pygame.draw.line(self.surface, self.fgcol, (xpos, self._pos.y), (xpos, self._pos.y + self.size.y), width=2)

                text_surface = self._font.render(str(second), False, (0, 255, 0))
                self.surface.blit(text_surface, (xpos, self._pos.y - 20))
            
            #Draw secondary grid line
            if (i + x_increment//2) % x_increment == 0:
                #Every other second
                pygame.draw.line(self.surface, self.fgcol, (xpos, self._pos.y), (xpos, self._pos.y + self.size.y), width=1)

        
        self.scroll_bar.draw()
        self.scroll_widget.draw()
        self.timeline_layer.draw()


if __name__ == "__main__":

    # Initialize Pygame
    pygame.init()

    # Set up the display
    screen_width = 1280
    screen_height = 720
    win = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("My Pygame Window")

    def test_scroll_func():
        pass


    #Create UI
    elements = []
    scroll_widget = Rectangle(win, 0, 0, 10, 10)
    scroll_widget.bgcol = (64, 64, 64)

    scroll_bar = ScrollBar(win, 0, 200, 100, 50, 0, test_scroll_func, widget=scroll_widget)
    scroll_bar.bgcol = (0, 0, 0)

    colour_picker = ColourPicker(win, 0, 0, 300, 200, "./dependencies/ColourPalette.jpg", test_scroll_func)

    transition = Transition(win, 300, 0, 500, 400)

    timeline = Timeline(win, 0, screen_height - 200, screen_width, 200, screen_width * 4)
    timeline.fgcol = (0, 0, 0)
    # _rects = []
    # for i in range(screen_height//2, screen_height, 40):
    #     _rects.append(Node(win, timeline.camera, screen_width/2, i+3))
    # for i in range(screen_height//2, screen_height, 40):
    #     _rects.append(Node(win, timeline.camera, 1280 * 2 - 100, i+3))

    # timeline.get_layer().add_objects(obj_list=_rects)

    elements.append(scroll_bar)
    elements.append(scroll_widget)
    elements.append(colour_picker)
    elements.append(timeline)
    elements.append(transition)

    main_layer = Layer("main layer")
    main_layer.add_UIelements(element_list=elements)



    # Set up the game clock
    clock = pygame.time.Clock()

    # Set up the game loop
    running = True
    while running:
        events = pygame.event.get()

        # Handle events
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen
        win.fill((255, 255, 255)) # fill the screen with white

        # Draw game objects
        main_layer.draw()
        main_layer.update(events)

        # Update the display
        pygame.display.update()

        # Wait for the next frame
        clock.tick(60) # limit the frame rate to 60 fps

    # Quit Pygame
    pygame.quit()
