import pygame
try:
    from .CustomStructures import *
except:
    from CustomStructures import *

'''
Simulation object class
Every object in the simulation should inherit from this

This allows for easy tracking of world position, camera position, and global position

Parameters:
    surface : the surface to draw pygame lines on
    camera : the camera which the object follows
    xpos and ypos : the global position of the object

Methods:
    to_screen_pos(vectos) : converts a given vector to the screen position to draw
'''
class Object:
    def __init__(self, surface, camera, xpos, ypos, width, height):
        self.camera = camera
        self.surface = surface
        self.size = Vector(width, height)
        self.direction = 0
        self._pos = Vector(xpos, ypos)
        self._screen_pos = Vector(xpos, ypos)
        self._tags = []
        self.visible = True
        self.draw_offset = Vector(0, 0)
        self.fgcol = (0, 0, 0)

    #Returns the vector of objects position
    def get_pos(self):
        return self._pos

    #Set the position of the object
    def set_pos(self, xpos, ypos):
        self._pos = Vector(xpos, ypos)

    #Returns the vector of objects screen position
    def get_screen_pos(self):
        if self.camera != None:
            return self.to_screen_pos(self._pos + self.draw_offset)
        else:
            return self._screen_pos + self.draw_offset

    #Returns the size of the object relative to the screen
    def get_screen_size(self):
        if self.camera != None:
            return self.camera.scale * self.size
        else:
            return self.size

    #Set the direction of the object
    #   direction ; direction in radians
    def set_direction(self, direction):
        self.direction = direction

    #Convert given vector to screen position with the camera
    def to_screen_pos(self, vector):
        return self.camera.scale * (vector - self.camera.get_pos()) + self.camera.get_screen_pos()

    #Convert given vector to world position
    def to_world_pos(self, vector):
        return ((1 / self.camera.scale) * (vector  - self.camera.get_screen_pos()) ) + self.camera.get_pos()

    #get/set method for tags
    #   tags : the tags to give the UI element
    def set_tags(self, tags):
        self._tags = tags.copy()

    def add_tag(self, tag):
        self._tags.append(tag)

    def get_tags(self):
        return self._tags

    def remove_tag(self, tag):
        self._tags.remove(tag)

    #Returns if object has all tags in passed tag list
    #   tags : list of tags that the object must contain
    #   needs_all : determine if at least one of the tags in the list is needed
    def has_tags(self, tags, needs_all=True):
        if needs_all == True:
            _has_all = True

            #If tag in list is not on object
            for tag in tags:
                if tag not in self._tags:
                    _has_all = False

            return _has_all
        else:
            for tag in tags:
                if tag in self._tags:
                    return True
            
            return False

    #Returns if tag is in object's tags
    def has_tag(self, tag):
        return (tag in self._tags)

    def draw(self):
        if self.camera != None:
            self._screen_pos = self.to_screen_pos(self._pos)

    def update(self, events):
        #Update screen position so its relative to camera
        #   +camera.screen pos to make the camera centered
        if self.camera != None:
            self._screen_pos = self.to_screen_pos(self._pos)

    

    #Set visibility of object
    def set_visible(self, active):
        self.visible = active

    #Return the top-left and bottom-right corner world position of the collision box
    def get_bbox(self):
        # self._bbox.set_pos(self._pos.x + self.size.x, self._pos.y + self.size.y)
        # return self._bbox
        _top_left = self._pos + self.draw_offset
        _bottom_right = self._pos + self.draw_offset + self.size

        return (_top_left, _bottom_right)

    #Returns the world centre of the object
    def get_centre(self):
        bbox = self.get_bbox()
        return 0.5 * (bbox[0] + bbox[1])

    #Returns the screen centre of the object to be drawn
    def get_draw_centre(self):
        return self.to_screen_pos(self.get_centre())

    def _draw_origins(self):
        pygame.draw.circle(self.surface, (0, 0, 255), self.get_draw_centre().get_pos(), 5) #draw centre of object
        pygame.draw.circle(self.surface, (0, 255, 0),  self.to_screen_pos(self._pos).get_pos(), 5) #draw position of object

    #Draws the bounding box of the object
    def _draw_bbox(self):
        bbox = self.get_bbox()
        bbox = (self.to_screen_pos(bbox[0]), self.to_screen_pos(bbox[1]))

        pygame.draw.lines(self.surface, self.fgcol, True, [
            (bbox[0].x, bbox[0].y),
            (bbox[1].x, bbox[0].y),
            (bbox[1].x, bbox[1].y),
            (bbox[0].x, bbox[1].y)], width=3)  

    #Returns if point is within bounding box
    #   point : WORLD point to check collision for
    def collision_point(self, point):
        bbox = self.get_bbox()
        return (bbox[0].x <= point.x <= bbox[1].x and bbox[0].y <= point.y <= bbox[1].y)


    

class RotationObject(Object):
    def __init__(self, surface, camera, xpos, ypos, width, height):
        super().__init__(surface, camera, xpos, ypos, width, height)

        self.rect_surface = pygame.Surface((self.size.x, self.size.y)) #Create the rect as a surface, this allows rotation
        #Set the background colour of the surface, this removes a coloured background in rotation
        self.rect_surface.set_colorkey((255, 255, 255)) 
        self.draw_offset = -0.5 * self.size

    #Returns if point is inside the SQUARE bouding box of size
    #   point : vector of point
    # def collision_point(self, point):
    #     bbox = self.get_bbox()

    #     #Get cornders of bounding box
    #     _top_bottom = (self.bottom_right - self.top_left).sign() #direction piece is facing

    #     _top_left = (self.top_left + self._pos).int() - _top_bottom
    #     _bottom_right = (self.bottom_right + self._pos).int() - _top_bottom

    #     #Check if point lies in bounding box
    #     #   divide by "top bottom" to flip the inequality for when the top left is greater than the bottom right
    #     if _top_left.x/_top_bottom.x <= point.x/_top_bottom.x <= _bottom_right.x/_top_bottom.x and _top_left.y/_top_bottom.y <= point.y/_top_bottom.y <= _bottom_right.y/_top_bottom.y:
    #         return True

    #     return False

    #Returns the offest to apply to the object when rotating
    def _rotation_world_offset(self):
        size = self.size
        width = abs(size.x * math.cos(self.direction)) + abs(size.y * math.sin(self.direction))
        height = abs(size.x * math.sin(self.direction)) + abs(size.y  * math.cos(self.direction))

        return 0.5 * Vector(width, height)


    def draw(self):
        super().draw()

        draw_size = self.get_screen_size()
        
        #Create new rotated rect surface
        if self.rect_surface.get_width() != draw_size.x or self.rect_surface.get_height() != draw_size.y:
            self.rect_surface = pygame.Surface(draw_size.get_pos())
            
        _new_pos = self.get_centre() - self._rotation_world_offset() #Apply offset to centre object
        
        self.rect_surface.fill((255,0,0)) #Fill red

        #Rotate the image
        rotated_image = pygame.transform.rotate(self.rect_surface, self.direction*180/math.pi) #Save the image to get the width etc
        self.surface.blit(rotated_image, self.to_screen_pos(_new_pos).get_pos()) #Draw rotated surface to screen

        self._draw_origins()
        self._draw_bbox()



'''
Camera class
Every object will be drawn relative to the camera's coordinates
'''
class Camera(Object):
    def __init__(self, surface, xpos, ypos):
        super().__init__(surface, None, xpos, ypos, 0, 0)
        self.scale = 1
        self.camera = self

    def get_screen_pos(self):
        return self._screen_pos #returns camera position relative to top-left of screen

    #Draw the camera at the screen position (debugging)
    def draw(self):
        pygame.draw.rect(self.surface, (255,0,0), pygame.Rect(self._screen_pos.x, self._screen_pos.y, 10, 10))


    def update(self, events):
        # pass
        #Temporary camera movement test
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self._pos.x -= 10
        elif keys[pygame.K_RIGHT]:
            self._pos.x += 10

        if keys[pygame.K_UP]:
            self._pos.y -= 10
        elif keys[pygame.K_DOWN]:
            self._pos.y += 10

'''
Placehodler for objects
Has no other functionality other than drawing
'''
class Square(Object):
    def __init__(self, surface, camera, xpos, ypos, width, height):
        super().__init__(surface, camera, xpos, ypos, width, height)
        self.draw_offset = -0.5 * self.size

    def draw(self):
        super().draw()

        #Draw position is self.to_screen_pos(self._pos) or could be self.get_screen_pos()
        pygame.draw.rect(self.surface, (255, 0, 0), pygame.Rect(*self.get_screen_pos().get_pos(), *self.get_screen_size().get_pos()))
        self._draw_origins()
        self._draw_bbox()



if __name__ == "__main__":
    from UIElements import *

    # Initialize Pygame
    pygame.init()

    # Set up the display
    screen_width = 1280
    screen_height = 720
    win = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("My Pygame Window")

    def test_scroll_func():
        pass


    #Create Objects
    objects = []
    camera = Camera(win, screen_width/2, screen_height/2)
    obj = Square(win, camera, screen_width/2, screen_height/2, 100, 100)

    objects.append(obj)
    objects.append(camera)

    main_layer = Layer("main layer")
    main_layer.add_objects(obj_list=objects)


    # Set up the game clock
    clock = pygame.time.Clock()

    # Set up the game loop
    running = True
    while running:
        events = pygame.event.get()
        mpos = Vector(*pygame.mouse.get_pos())

        # Handle events
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(obj.to_world_pos(mpos))
                print(obj.collision_point(obj.to_world_pos(mpos)))

        # Clear the screen
        win.fill((255, 255, 255)) # fill the screen with white

        obj.set_direction(math.atan2(-mpos.y + obj.get_screen_pos().y, mpos.x - obj.get_screen_pos().x))

        # Draw game objects
        main_layer.draw()
        main_layer.update(events)

        # Update the display
        pygame.display.update()

        # Wait for the next frame
        clock.tick(60) # limit the frame rate to 60 fps

    # Quit Pygame
    pygame.quit()