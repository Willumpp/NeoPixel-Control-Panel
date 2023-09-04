from dependencies.CustomObjects import *
from dependencies.CustomStructures import Colour
from settings import *
import NewUI as nu 

class Node(Object):
    #Used for creating and editing the settings within a node
    class NodeSetting:
        def __init__(self, value, setting_tag, display_name, transition_display_name):
            self.value = value #the value of the setting
            self.setting_tag = setting_tag #the tag the setting holds
            self.display_name = display_name #the name to draw the setting in the editor ; "None" to not display

            self.transition_display_name = transition_display_name

        def set_val(self, value):
            self.value = value

        def copy(self):
            return self.__class__(self.value, self.setting_tag, self.display_name, self.transition_display_name)

        def lerp(self, inp, t):
            return int(self.value + (inp.value - self.value) * abs(t))

        def get_setting(self):
            return self.value
        
        def __repr__(self):
            return f"Value: {self.value}; Tag:{self.setting_tag}"

    class ColourNodeSetting(NodeSetting):
        def lerp(self, inp, t):
            return self.value.lerp(inp.value, t)

        def copy(self):
            return self.__class__(self.value.copy(), self.setting_tag, self.display_name, self.transition_display_name)

        def set_val(self, rgb_code):
            if isinstance(rgb_code, tuple):
                self.value.set_rgb(rgb_code)
            elif isinstance(rgb_code, list):
                self.value.set_rgb(tuple(rgb_code))
            elif isinstance(rgb_code, Colour):
                self.value = rgb_code
            else:
                raise Exception(f"Error; Invalid colour set {rgb_code}")

        # def get_setting(self):
        #     return self.value.get_rgb()

    class ColourTupleNodeSetting(NodeSetting):
        def lerp(self, inp, t):
            _val1 = Colour(rgb=self.value)
            _val2 = Colour(rgb=inp.value)

            return _val1.lerp(_val2, t).get_rgb()

    class PixelIndexNodeSetting(NodeSetting):
        def set_val(self, value):
        
            self.value = value % (PIXEL_COUNT+1)


    def __init__(self, surface, camera, xpos, ypos, width, height, strip_preview):
        super().__init__(surface, camera, xpos, ypos, width, height)
        self.draw_offset = -0.5 * self.size
        self.strip_preview = strip_preview
        #self.col = (255, 0, 0)

        #Used for setting the settings of the node
        self.settings = {
            "col": Node.ColourTupleNodeSetting((255, 0, 0), "col", None, "Colour"),
        }

        self.transition = None #This is first added for the purpose of saving and loading of transitions

        self.add_tag("node")
    
    def set_settings(self, setting_tag, value):
        if setting_tag not in self.settings.keys():
            raise Exception(f"Error; Settings tag '{setting_tag}' not in the setting dictionary. {self.settings}")

        self.settings[setting_tag].set_val(value)

    def get_setting(self, setting_tag):
        if setting_tag not in self.settings.keys():
            raise Exception(f"Error; Settings tag '{setting_tag}' not in the setting dictionary. {self.settings}")

        return self.settings[setting_tag].get_setting()

    def draw(self):
        super().draw()
        if self.visible == True:
            try:
                pygame.draw.rect(self.surface, self.get_setting("col"), pygame.Rect(*self.get_screen_pos().get_pos(), *self.get_screen_size().get_pos()))
            except TypeError as e:
                raise Exception(f"Invalid colour argument {self.get_setting('col')}")

            self._draw_bbox()

    #Perform strip interaction
    #   called when the timeline line crosses the node
    def strip_interact(self):
        pass

    #Returns a copy of the settings
    def settings_copy(self):
        _out = {}
        for setting in self.settings.keys():

            _setting = self.get_setting(setting)
            if isinstance(_setting, Colour):
                _rgb = _setting.get_rgb()
                _setting = (int(_rgb[0]), int(_rgb[1]), int(_rgb[2]))

            elif isinstance(_setting, tuple) and setting == "col": #this is a bad way of doing it
                _setting = (int(_setting[0]), int(_setting[1]), int(_setting[2]))

            _out[setting] = _setting

        return _out

    #Print the node
    def __repr__(self):
        return f"Colour: {self.get_setting('col')}"
        
#Sets the colour of a singlue pixel
class SinglePixelNode(Node):
    def __init__(self, surface, camera, xpos, ypos, width, height, strip_preview):
        super().__init__(surface, camera, xpos, ypos, width, height, strip_preview)

        self.settings["pixel_index"] = Node.PixelIndexNodeSetting(0, "pixel_index", "Pixel Index:", "Pixel Index")

        self.add_tag("single")
    
    def strip_interact(self):

        #with numpy
        _pixel_index = self.get_setting("pixel_index")
        _col = self.get_setting("col")
        self.strip_preview.pixels[_pixel_index-1] = _col

#Sets the colour of the entire strip
class FillNode(Node):
    def __init__(self, surface, camera, xpos, ypos, width, height, strip_preview):
        super().__init__(surface, camera, xpos, ypos, width, height, strip_preview)

        self.add_tag("fill")

    def strip_interact(self):

        #With numpy
        self.strip_preview.pixels[...] = self.get_setting("col")

class GradientNode(Node):

    def __init__(self, surface, camera, xpos, ypos, width, height, strip_preview):
        super().__init__(surface, camera, xpos, ypos, width, height, strip_preview)

        self.settings["node_count"] = Node.NodeSetting(0, "node_count", "Node Count:", None)

        self.sub_nodes = [] #List of all nodes to form gradient , nodes MUST be in order of their index
        self.strip_size = strip_preview.pixel_count

        self.add_tag("gradient")

    def set_settings(self, setting_tag, value):
        super().set_settings(setting_tag, value)

        #Changing sub-node count and evenly distributing
        if setting_tag == "node_count" and isinstance(value, int) and value != self.node_count():
            self.sub_nodes.clear()

            #If more than 0 nodes are chosen
            if value != 0:
                #Find how much spacing is needed per node
                spacing = self.strip_size//value
                ypos = self.strip_preview._pos.y + self.strip_preview.size.y / 2

                #Evenly distribute
                #   spacing//2 for start so even width between start and end
                for i in range(spacing//2, self.strip_size, spacing):
                    _col = Node.ColourNodeSetting(Colour(rgb=(0, 0, 0)), "col_"+str(len(self.sub_nodes)), None, "Colour")
                    _index = Node.NodeSetting(0, "index_"+str(len(self.sub_nodes)), "Pixel Index:", "Pixel Index")


                    self.settings["col_"+str(len(self.sub_nodes))] = _col
                    self.settings["index_"+str(len(self.sub_nodes))] = _index

                    _node = GradientSubNode(self.surface, self.camera, i, ypos, 10, self.strip_preview.size.y, self.strip_preview, self, len(self.sub_nodes))

                    _node.set_settings("pixel_index", i)
                    self.sub_nodes.append(_node)

            self.re_order_nodes()

    def get_sub_nodes(self):
        return self.sub_nodes.copy()

    #Sorts all sub nodes based on their xposition
    def re_order_nodes(self):
        nodes = np.array(self.sub_nodes.copy()) #use numpy array as it is faster

        nodes = sorted(nodes, key=lambda x:x.get_setting("pixel_index"))
        self.sub_nodes = nodes #re-assign list

    #Returns the number of sub nodes
    def node_count(self):
        return len(self.sub_nodes)

    #Perform interpolation between subnodes for gradient
    def strip_interact(self):
        self.re_order_nodes()

        strip_size = self.strip_size

        #Check if nodes are actually available
        if self.node_count() > 0:
            last_node = self.sub_nodes[-1] #Node to interpolate from
            next_node = self.sub_nodes[0] #Node to interpolate towards
        else:
            return
        
        node_set = -1 #Counter for which pair of nodes are transitioning between

        last_node_i = last_node.get_setting("pixel_index")
        next_node_i = next_node.get_setting("pixel_index")

        #With numpy
        #Loop through every pixel on the strip
        for pixel_i in range(len(self.strip_preview.pixels)):
            
            
            #For when the gradient is before the first node on the strip
            try:
                if node_set < 0:
                    _progress = (pixel_i - last_node_i + strip_size) / (next_node_i - last_node_i + strip_size)
                
                #For when the gradient is in the centre of the strip
                elif 0 <= node_set < self.node_count()-1:
                    _progress = (pixel_i - last_node_i) / (next_node_i - last_node_i)

                #For when the gradient reaches the end of the strip
                elif node_set >= self.node_count()-1:
                    _progress = (pixel_i - last_node_i) / (next_node_i + strip_size - last_node_i)
            except ZeroDivisionError:
                _progress = 1 # At full progress if nodes are touching


            #Interpolate to get a colour
            #   the "col" in last node is the "Colour" object, not a tuple
            _col = last_node.get_setting("col").lerp(next_node.get_setting("col"), _progress).get_rgb()
            self.strip_preview.pixels[pixel_i] = _col #set the colour on the strip

            #Cycle to next two gradient points
            if _progress > 1:
                node_set += 1
                last_node = self.sub_nodes[node_set] 
                next_node = self.sub_nodes[(node_set+1) % self.node_count()] 

                last_node_i = last_node.get_setting("pixel_index")
                next_node_i = next_node.get_setting("pixel_index")

class GradientSubNode(Node):
    def __init__(self, surface, camera, xpos, ypos, width, height, strip_preview, parent, index):
        super().__init__(surface, camera, xpos, ypos, width, height, strip_preview)

        self.index = index
        
        self.add_tag("gradient_sub_node")
        self.add_tag("gradient")
        self.parent = parent
        self.camera = Camera(self.surface, 0, 0)
        # self.draw_offset = -0.5 * self.size
        self.set_xpos(xpos)

    def get_sub_nodes(self):
        return self.parent.get_sub_nodes()

    def strip_interact(self):
        return self.parent.strip_interact()

    #Modified to also set the x position
    def set_settings(self, setting_tag, value):

        #Get the parent's rather than itself
        if setting_tag == "col":
            self.parent.set_settings("col_" + str(self.index), value)
            return 1
        if setting_tag == "pixel_index":
            self.parent.set_settings("index_" + str(self.index), value)
            self._pos.x = self.index_to_xpos(value)
            return 1

        super().set_settings(setting_tag, value)

    def get_setting(self, setting_tag):
        if setting_tag == "col":
            return self.parent.get_setting("col_" + str(self.index))
        if setting_tag == "pixel_index":
            return self.parent.get_setting("index_" + str(self.index))
        
        super().get_setting(setting_tag)

    
    #Set the xposition of the node
    #   also sets the index
    def set_xpos(self, xpos):
        self._pos.x = xpos

        self.set_settings("pixel_index", self.xpos_to_index(xpos))

    #Converts index to on screen x position
    def index_to_xpos(self, index):
        return (index * SCREEN_SIZE.x / self.parent.strip_size) % SCREEN_SIZE.x

    #Converts a given x position to an index on the strip
    def xpos_to_index(self, xpos):
        return (xpos * self.parent.strip_size // SCREEN_SIZE.x) % self.parent.strip_size

    def draw(self):
        self._pos.x = self.index_to_xpos(self.get_setting("pixel_index")) 
        _rect = pygame.Rect(*self.get_screen_pos().get_pos(), self.size.x, self.size.y)

        pygame.draw.rect(self.surface, self.get_setting("col").get_rgb(), _rect)

        self.fgcol = self.get_setting("col").invert().get_rgb()
        self._draw_bbox()

    def __repr__(self):
        return f"Colour: {self.get_setting('col')} \nIndex: {self.get_setting('pixel_index')}\n"


class SpotlightNode(Node):
    def __init__(self, surface, camera, xpos, ypos, width, height, strip_preview):
        super().__init__(surface, camera, xpos, ypos, width, height, strip_preview)

        self.settings = {
            "col": Node.NodeSetting((0, 0, 0), "col", None, "Colour"),
            "pixel_index": Node.NodeSetting(120, "pixel_index", "Pixel Index:", "Pixel Index"),
            "radius": Node.NodeSetting(10, "radius", "Radius:", "Radius")
        }

        self.add_tag("spotlight")

    def strip_interact(self):
        pixels = self.strip_preview.get_pixels(copy=True)
        _pixel_index = self.get_setting("pixel_index")
        _radius = int(self.get_setting("radius"))
        _diameter = 2 * _radius
        _col = Colour(rgb=self.get_setting("col"))
        _pixel_col = Colour()

        for pixel_i in range(-_radius, _radius, 1):
            _index = (pixel_i + _pixel_index) % PIXEL_COUNT
            _t =  2 * abs(pixel_i) / _diameter

            _pixel_col.set_rgb(self.strip_preview.pixels[_index])
            
            self.strip_preview.pixels[_index] = _col.lerp(_pixel_col, _t)

class TerminateNode(Node):
    def __init__(self, surface, camera, xpos, ypos, width, height, strip_preview, timeline_ui):
        super().__init__(surface, camera, xpos, ypos, width, height, strip_preview)
        self.timeline_ui = timeline_ui
        self.set_settings("col", (0,0,0))

        self.add_tag("terminate")

    def strip_interact(self):
        self.timeline_ui.reset()

class StartNode(Node):
    def __init__(self, surface, camera, xpos, ypos, width, height, strip_preview):
        super().__init__(surface, camera, xpos, ypos, width, height, strip_preview)
        self.set_settings("col", (0,0,255))

        self.add_tag("start")

    def strip_interact(self):
        pass




class TransitionNode(Object):
    def __init__(self, surface, camera, node1, node2, strip_preview):
        super().__init__(surface, camera, 0, 0, 0, 0)

        #Swap order if the second node is before the first
        if node2.get_pos().x < node1.get_pos().x:
            self.from_node = node2
            self.to_node = node1
        else:
            self.from_node = node1 #Node to start the transition
            self.to_node = node2 #Node to end the transition

        self.from_node.transition = self
        self.to_node.transition = self

        self.strip_preview = strip_preview
        self.fgcol = (255, 255, 255)
        self.col = (255, 0, 0)

        self.draw_offset = Vector(0, -0.5 * self.size.y)

        self._pos = self.from_node.get_pos()
        self.size = self.to_node.get_pos() - self.from_node.get_pos() - Vector(2, 0)


        #__class__ gets the class from an object
        self.interaction_node = self.from_node.__class__(None, None, 0, 0, 0, 0, strip_preview) #this will be used to apply the settings to the strip preview
        if node1.has_tag("gradient"):
            self.interaction_node.set_settings("node_count", node1.get_setting("node_count"))


        #Dictionary of sub nodes
        #Used to select a different transition for a different unique setting
        #   key ; the setting the transition effects
        #   value ; the type of node which is transitioning
        self.sub_nodes = {}
        for setting in self.from_node.settings.keys():

            #Apply transition if available
            if self.from_node.settings[setting].transition_display_name != None:

                #Create UI transition element
                _pos = nu.ptc(3.97, 1.82)
                _size = nu.ptc(7.2, 7.2)
                _trans = nu.Transition(surface, _pos.x, _pos.y, _size.x, _size.y)
                _trans.bgcol = COLOURS["bgcol"].get_rgb()
                self.sub_nodes[setting] = _trans


    #t ; t value for transition (progress of transition) 0 < t < 1
    def strip_interact(self, t):
        # self.interaction_node.settings = self.from_node.settings_copy()
        set_value = None


        #Loop through all sub-settings to transition
        for setting_i, setting_tag in enumerate(self.sub_nodes.keys()):

            _val1 = self.from_node.settings[setting_tag]
            _val2 = self.to_node.settings[setting_tag]

            #Apply setting to the interaciton node , interpolate for the individual setting using the "sub nodes" dictionary
            self.interaction_node.set_settings(setting_tag, _val1.lerp(_val2, self.sub_nodes[setting_tag].get_value(t)))
        
        #Apply state to the strip preview
        self.interaction_node.strip_interact()


    def placeholder(self, *args):
        pass

    def draw(self):
        super().draw()

        self._pos = self.from_node.get_pos()
        self.size = self.to_node.get_pos() - self.from_node.get_pos() + Vector(0, 10)
        self.draw_offset = Vector(0, -0.5 * self.size.y)

        #Draw line connecting two nodes
        _rect = pygame.Rect(*self.get_screen_pos().get_pos(), *self.get_screen_size().get_pos())
        pygame.draw.rect(self.surface, self.col, _rect)


class TimelineIterator(Object):
    def __init__(self, surface, camera, xpos, ypos, width, height, speed):
        super().__init__(surface, camera, xpos, ypos, width, height)
        self.velocity = speed #speed of which the timeline moves
        self.start_pos = Vector(xpos, ypos)

    def update(self, events):
        super().update(events)

        self._pos.x += self.velocity * 1/FPS

    def reset(self):
        #Reset position
        self._pos.set_pos(self.start_pos.x, self.start_pos.y)

    def draw(self):
        super().draw()

        # print(self.visible)
        # if self.visible == True:
        #Draw line
        pygame.draw.line(self.surface, (255, 0, 0), (self.get_screen_pos().x , self._pos.y), (self.to_screen_pos(self._pos + self.size).x, self._pos.y + self.size.y))