from NewUI import *
from NewObjects import *
from settings import *
import dependencies.FileHandlers as fh
import json

def ptc(x, y):
    return Vector(x/33.87 * SCREEN_SIZE.x, y/19.05 * SCREEN_SIZE.y)

'''
This is where nodes are edited
'''
class NodeEditor(Layer):
    def __init__(self, layer_name, surface, strip_preview):
        super().__init__(layer_name)

        self.surface = surface
        self.selected_node = None

        self.colour_picker = None
        self.colour_picker_crosshair = None

        self.rgb_inputs = [] #all input boxes for rgb
        self.hsv_inputs = [] #all input boxes for hsv
        self.hex_input = None #all input boxes for hex
        self.selected_colour = Colour() #This is the colour for the node

         #all input boxes for regular settings
        self.settings_inputs = {}

        self.strip_preview = strip_preview # the colourful strip along middle

    #Called when the colour picker is clicked
    #   sets all colour inputs to the chosen input
    #   does not call the node update immediately
    def colour_picker_function(self):
        if self.colour_picker != None:
            #Set the crosshair's position
            mouse = pygame.mouse.get_pos()
            self.colour_picker_crosshair.set_pos(mouse[0], mouse[1])

            self.selected_colour.set_rgb(self.colour_picker.last_colour)

            self.update_rgb()
            self.update_hsv()
            self.update_hex()


    #Update the input boxes for RGB
    def update_rgb(self):
        for input_i, input in enumerate(self.rgb_inputs):
            input.set_text(str(self.selected_colour.get_rgb()[input_i]))

    #Update the input boxes for HSV
    def update_hsv(self):
        for input_i, input in enumerate(self.hsv_inputs):
            input.set_text(str(self.selected_colour.get_hsv()[input_i]))

    #Update the input boxes for HEX
    def update_hex(self):
        self.hex_input.set_text(self.selected_colour.get_hex())


    #Update the variables of the node
    #   this is called every frame
    def update_node(self):
        node = self.selected_node

        if node != None:
            node.set_settings("col", self.selected_colour.get_rgb())

            #Change all the settings for the node
            #   only applies settings named in node
            for settings_tag in list(node.settings.keys()):
                #Only apply if tag is a valid input setting
                if settings_tag in self.settings_inputs.keys():
                    node.set_settings(settings_tag, self.settings_inputs[settings_tag].get_text())

    #Changes all the settings input fields to this node's
    #   additionally applies the settings to the node 
    def update_settings(self, node, settings):

        if isinstance(node.get_setting("col"), Colour):
            self.selected_colour.set_rgb(node.get_setting("col").get_rgb())
        else:
            self.selected_colour.set_rgb(node.get_setting("col"))

        self.update_rgb()
        self.update_hsv()
        self.update_hex()

        self.remove_UIelements(tags=["settings"])
        self.settings_inputs.clear()

        elements = []
        
        #Create settings UI
        for setting_i, setting_tag in enumerate(settings.keys()):
            setting = settings[setting_tag]

            if setting.display_name != None:
                text = setting.display_name
                value = setting.value
                tag = setting.setting_tag

                #Text on left
                _pos = ptc(18.79, 0.71 + setting_i * 0.8)
                _size = ptc(20, 1.03)
                _element = TextBox(self.surface, _pos.x, _pos.y, _size.x, _size.y, font_size=18)
                _element.set_text(text)
                _element.set_tags(["settings"])
                _element.fgcol = COLOURS["white"].get_rgb()
                elements.append(_element)

                #Input box
                _pos = ptc(22.19, 0.91 + setting_i * 0.8)
                _size = ptc(1.65, 0.64)
                _element = TextInput(self.surface, _pos.x, _pos.y, _size.x, _size.y, str(value), 3, use_int=True, max_val=PIXEL_COUNT, min_val=0)
                _element.set_tags([tag, "settings"])
                _element.fgcol = COLOURS["white"].get_rgb()
                _element.bgcol = COLOURS["dark_grey"].get_rgb()
                self.settings_inputs[tag] = _element
                elements.append(_element)

            #Set the text of the input box if setting in the available boxes
            if setting in self.settings_inputs.keys():
                self.settings_inputs[setting].set_text(str(setting.value))

        self.add_UIelements(element_list=elements)
        self.update_node() #this changes the actual variables of the node


    #Called by the timeline (or otherwise) to set the nodes colour via this editor
    def set_node(self, node):
        self.set_visibility(True)
        self.selected_node = node

        if node != None:
            self.update_settings(node, node.settings)

            
    #Set selected node to none and hide UI
    def de_select_node(self):
        self.selected_node = None
        self.strip_preview.reset()
        self.visible = False

    def draw(self):
        super().draw()


        if self.selected_node != None:

            self.selected_node.strip_interact()

            #Draw sub nodes for gradient node
            if self.selected_node.has_tag("gradient"):
                for node in self.selected_node.get_sub_nodes():
                    node.draw()


    @UIElement.require_visible
    def update(self, events):
        super().update(events)

        #Change colour with inputs
        change_colour = True

        #Extract rgb inputs
        rgb = []
        for rgb_input in self.rgb_inputs:
            if rgb_input.selected == True:
                change_colour = False
                break

            rgb.append(int(rgb_input.get_text()))

        #Extract hsv inputs
        hsv = []
        for hsv_input in self.hsv_inputs:
            if hsv_input.selected == True:
                change_colour = False
                break

            hsv.append(int(hsv_input.get_text()))

        #Extract hex inputs
        hex = ""
        hex_input = self.hex_input
        if hex_input.selected == True:
            change_colour = False
        hex = hex_input.get_text()

        if change_colour == True:
            #RGB input has detected change
            if tuple(rgb) != self.selected_colour.get_rgb():
                self.selected_colour.set_rgb(tuple(rgb))

                self.update_hsv()
                self.update_hex()
            #HSV input has detected change
            elif tuple(hsv) != self.selected_colour.get_hsv():
                self.selected_colour.set_hsv(tuple(hsv))

                self.update_rgb()
                self.update_hex()
            #HEX input has detected change
            elif hex != self.selected_colour.get_hex():
                self.selected_colour.set_hex(hex)

                self.update_rgb()
                self.update_hsv()

    
        #Sub node mouse interaction
        if self.selected_node != None:
            mpos = Vector(*pygame.mouse.get_pos())

            #Find sub node to select with cursor
            #   only apply when the selected node is a gradient node
            if self.selected_node.has_tag("gradient"):

                #Mouse detection
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        #Find node mouse is close to
                        for node in self.selected_node.get_sub_nodes():
                            if node.collision_point(mpos):
                                self.set_node(node)

        self.update_node()


    def create_UI(self):
        elements = []

        #Colour Picker
        _pos = ptc(1.03, 0.9)
        _size = ptc(12.7, 8.19)
        _element = ColourPicker(self.surface, _pos.x, _pos.y, _size.x, _size.y, "./dependencies/ColourPalette.jpg", self.colour_picker_function)
        self.colour_picker = _element
        elements.append(_element)

        #Crosshair - moves to position of mouse click
        _element = Rectangle(self.surface, _pos.x, _pos.y, 10, 10)
        self.colour_picker_crosshair = _element
        elements.append(_element)

        #RGB codes
        rgbs = ["R:", "G:", "B:"]
        for i in range(0, 3):

            #Text on left
            _pos = ptc(14.42, 0.71 + i * 0.8)
            _size = ptc(1.18, 1.03)
            _element = TextBox(self.surface, _pos.x, _pos.y, _size.x, _size.y, font_size=18)
            _element.set_text(rgbs[i])
            _element.fgcol = COLOURS["white"].get_rgb()
            elements.append(_element)

            #Input box
            _pos = ptc(16.07, 0.91 + i * 0.8)
            _size = ptc(1.65, 0.64)
            _element = TextInput(self.surface, _pos.x, _pos.y, _size.x, _size.y, "255", 3, use_int=True, max_val=255, min_val=0)
            _element.set_tags([rgbs[i], "rgb"])
            _element.fgcol = COLOURS["white"].get_rgb()
            _element.bgcol = COLOURS["dark_grey"].get_rgb()
            self.rgb_inputs.append(_element)
            elements.append(_element)

        #RGB codes
        hsvs = [["H:", 360], ["S:", 100], ["V:", 100]]
        for i in range(0, 3):
            text = hsvs[i][0]
            max_val = hsvs[i][1]

            #Text on left
            _pos = ptc(14.42, 4.22 + i * 0.8)
            _size = ptc(1.18, 1.03)
            _element = TextBox(self.surface, _pos.x, _pos.y, _size.x, _size.y, font_size=18)
            _element.set_text(text)
            _element.fgcol = COLOURS["white"].get_rgb()
            elements.append(_element)

            #Input box
            _pos = ptc(16.07, 4.42 + i * 0.8)
            _size = ptc(1.65, 0.64)
            _element = TextInput(self.surface, _pos.x, _pos.y, _size.x, _size.y, str(max_val), 3, use_int=True, max_val=max_val, min_val=0)
            _element.set_tags([text, "hsv"])
            _element.fgcol = COLOURS["white"].get_rgb()
            _element.bgcol = COLOURS["dark_grey"].get_rgb()
            self.hsv_inputs.append(_element)
            elements.append(_element)

        #Text on left
        _pos = ptc(14.42, 7.74)
        _size = ptc(1.88, 1.03)
        _element = TextBox(self.surface, _pos.x, _pos.y, _size.x, _size.y, font_size=18)
        _element.set_text("Hex:")
        _element.fgcol = COLOURS["white"].get_rgb()
        elements.append(_element)

        #Input box
        _pos = ptc(16.07, 7.94)
        _size = ptc(1.65, 0.64)
        _element = TextInput(self.surface, _pos.x, _pos.y, _size.x, _size.y, "#FFFFFF", 7)
        _element.set_font2("Comic Sans MS", 8)
        _element.set_tags(["hex"])
        _element.fgcol = COLOURS["white"].get_rgb()
        _element.bgcol = COLOURS["dark_grey"].get_rgb()
        self.hex_input = _element
        elements.append(_element)

        self.add_UIelements(element_list=elements)


class TransitionEditor(Layer):
    def __init__(self, layer_name, surface, strip_preview):
        super().__init__(layer_name)

        self.surface = surface
        self.selected_transition = None
        self.strip_preview = strip_preview

        self.transition_sub_node = None

    def change_setting(self, settings_tag):
        self.transition_sub_node = self.selected_transition.sub_nodes[settings_tag]

    #Changes all the available selection boxes for this transition
    def update_settings(self, transition, settings):

        self.remove_UIelements(tags=["settings"])

        elements = []
        _buttons = []
        
        #Create settings UI
        for setting_i, setting_tag in enumerate(settings.keys()):
            setting = settings[setting_tag]

            # if setting.display_name != None:
            text = setting.transition_display_name
            value = setting.value
            tag = setting.setting_tag

            if text != None:
                #Selection button
                _pos = ptc(19, 0.83 + setting_i * 0.8)
                _size = ptc(2.72, 0.83)
                _element = SelectionButton(self.surface, _pos.x, _pos.y, _size.x, _size.y, self.change_setting, COLOURS["light_grey"].get_rgb(), COLOURS["dark_grey"].get_rgb(), _buttons, args=(tag, ))
                _element.set_text(text)
                _element.set_tags(["settings"])
                _element.fgcol = COLOURS["white"].get_rgb()
                elements.append(_element)

        self.add_UIelements(element_list=elements)
        # self.update_node() #this changes the actual variables of the node

    #Hide and remove the selected transition
    def de_select_transition(self):
        self.set_visibility(False)
        self.selected_transition = None
        self.transition_sub_node = None

    #Called by the timeline (or otherwise) to set the nodes colour via this editor
    def set_transition(self, transition):
        self.set_visibility(True)
        self.selected_transition = transition

        if transition != None:
            self.update_settings(transition, transition.from_node.settings)

    #Set the type of transition to use for that specific setting
    #   transition_type ; type of transition which MUST be compatible with the UI
    def set_transition_type(self, transition_type):
        #transition_sub_node == none when a setting isnt selected in the transition editor
        if self.transition_sub_node == None:
            pass
        else:
            self.transition_sub_node.set_transition(transition_type)

    def create_UI(self):
        
        elements = []

        #Linear type
        _pos = ptc(1.09, 0.79)
        _size = ptc(2.72, 0.83)
        _element = Button(self.surface, _pos.x, _pos.y, _size.x, _size.y, self.set_transition_type, args=("linear", ))
        _element.bgcol = COLOURS["light_grey"].get_rgb()
        _element.fgcol = COLOURS["white"].get_rgb()
        _element.set_text("Linear")
        elements.append(_element)

        #Bezier type
        _pos = ptc(4.29, 0.79)
        _size = ptc(2.72, 0.83)
        _element = Button(self.surface, _pos.x, _pos.y, _size.x, _size.y, self.set_transition_type, args=("bezier", ))
        _element.bgcol = COLOURS["light_grey"].get_rgb()
        _element.fgcol = COLOURS["white"].get_rgb()
        _element.set_text("Bezier")
        elements.append(_element)

        #None type
        _pos = ptc(7.49, 0.79)
        _size = ptc(2.72, 0.83)
        _element = Button(self.surface, _pos.x, _pos.y, _size.x, _size.y, self.set_transition_type, args=("none", ))
        _element.bgcol = COLOURS["light_grey"].get_rgb()
        _element.fgcol = COLOURS["white"].get_rgb()
        _element.set_text("None")
        elements.append(_element)

        self.add_UIelements(element_list=elements)


    @UIElement.require_visible
    def draw(self):
        super().draw()

        #Draw the interactive tansition maker
        if self.transition_sub_node != None:
            self.transition_sub_node.draw()

    @UIElement.require_visible
    def update(self, events):
        super().update(events)

        #Update the interactive transition maker
        if self.transition_sub_node != None:
            self.transition_sub_node.update(events)

'''
Layer which holds the timeline
Child layers are the node and transition editors
'''
class TimelineEditor(Layer):
    def __init__(self, layer_name, surface, node_editor, transition_editor, strip_preview):
        super().__init__(layer_name)
        self.surface = surface
        self.timeline_ui = None
        self.strip_preview = strip_preview

        self.state = "idle" #state variable for state machine
        self.placement_node = None
        self.selected_node = None
        self.start_node = None #This node is for where the timeline iterator begins
        self.node_editor = node_editor
        self.transition_editor = transition_editor

        self.nodes = [] #All nodes on timeline are in here
        self.activated_nodes = []
        self.node_activation_queue = PriorityQueue(32) #Used for activating nodes in a top-down order

        self.transitions = []
        self.transition_activation_queue = PriorityQueue2(32)

        # _tag_to_class = {
        #     "single":SinglePixelNode,
        #     "fill":FillNode,
        #     "gradient":GradientNode,

        # }

        # # Load external file and add all nodes to the timeline
        # if LOAD_FILE_NAME != "":
        #     file = fh.TextFile(LOAD_FILE_NAME, "./")
        #     _tags = file.read_serialised()

        #     print(_tags)

        #     file.close()

    #Adds a given node to the timeline
    def add_node(self, node):
        self.nodes.append(node)
        self.timeline_ui.timeline_layer.add_objects(single_obj=node)
        node.add_tag("node")

    #Removes the given node (object) from the timeline
    def remove_node(self, node):
        if node != None:
            self.nodes.remove(node)
            self.timeline_ui.timeline_layer.remove_objects(obj_list=[node])

    #Adds a given transition to the timeline
    def add_transition(self, transition):
        self.transitions.append(transition)
        self.timeline_ui.timeline_layer.add_objects(single_obj=transition)
        transition.add_tag("transition")

    #Removes the given transition from the timeline
    def remove_transition(self, transition):
        if transition != None:
            self.transitions.remove(transition)
            self.timeline_ui.timeline_layer.remove_objects(obj_list=[transition])

    def reset(self):
        self.activated_nodes.clear()
        self.timeline_iterator.reset()
        self.strip_preview.reset()

        if self.start_node != None:
            self.timeline_iterator.set_pos(self.start_node.get_pos().x, self.timeline_iterator.get_pos().y)

    def update(self, events):
        #Rounds number to nearest value of resolution
        #   to how the offset works is beyond me (i just tried random combinations)
        def round(val, resolution, offset=0):
            return resolution * int(0.5 + (val + offset) / resolution) - offset

        super().update(events)
        mouse_pos = Vector(*pygame.mouse.get_pos())
        placement_vector = Vector(mouse_pos.x, mouse_pos.y) #This is where the node will get placed

        #Node/transition activation
        for node in self.nodes:
            #Dont activate same node twice
            if node in self.activated_nodes:
                continue

            _node_pos = node.get_pos()

            #If line in node range and node not already activated
            if _node_pos.x < self.timeline_iterator.get_pos().x < _node_pos.x + node.size.x:
                self.activated_nodes.append(node)
                self.node_activation_queue.enqueue(node, node.get_pos().y)


        #Get all transitions currently within range of the iterator
        #   sort all found tansitions by their y-ordinate
        #   lower down transitions are activated last
        _transitions = []
        for transition in self.transitions:
            _trans_pos = transition.get_pos()

            if _trans_pos.x < self.timeline_iterator.get_pos().x < _trans_pos.x + transition.size.x:
                _transitions.append(transition)

        _transitions = sorted(_transitions, key=lambda x: x.get_pos().y, reverse=False)

        #   Ensure node/transition activation in a top-down order using the priority queue
        for transition in _transitions:            
            _trans_pos = transition.get_pos()
            t = (self.timeline_iterator.get_pos().x - _trans_pos.x) / transition.size.x
            
            transition.strip_interact(t)
        
        _transitions.clear()

        for node in self.node_activation_queue.dequeue_iterator():
            node.strip_interact()

        #Node placement
        for event in events:
            if event.type == pygame.KEYDOWN:
                #Node placement
                #   must be in idle state
                if self.state != "idle" and self.state != "node editor":
                    pass
                #Pixel node - sets singular pixel to colour
                elif event.key == pygame.K_F1:
                    self.state = "placing node"
                    self.placement_node = SinglePixelNode(self.surface, self.timeline_ui.camera, mouse_pos.x, mouse_pos.y, 15, 15, self.strip_preview)
                #Fill node - fills entire strip
                elif event.key == pygame.K_F2:
                    self.state = "placing node"
                    self.placement_node = FillNode(self.surface, self.timeline_ui.camera, mouse_pos.x, mouse_pos.y, 15, 15, self.strip_preview)
                #Gradient node - fills a gradient accross strip
                elif event.key == pygame.K_F3:
                    self.state = "placing node"
                    self.placement_node = GradientNode(self.surface, self.timeline_ui.camera, mouse_pos.x, mouse_pos.y, 15, 15, self.strip_preview)
                #Spotlight node - fills a gradient accross a portion of the strip
                elif event.key == pygame.K_F4:
                    self.state = "placing node"
                    self.placement_node = SpotlightNode(self.surface, self.timeline_ui.camera, mouse_pos.x, mouse_pos.y, 15, 15, self.strip_preview)
                elif event.key == pygame.K_F12:
                    self.state = "placing node"
                    self.placement_node = TerminateNode(self.surface, self.timeline_ui.camera, mouse_pos.x, mouse_pos.y, 15, 15, self.strip_preview, self)
                elif event.key == pygame.K_F11:
                    self.state = "placing node"
                    _start_node = StartNode(self.surface, self.timeline_ui.camera, mouse_pos.x, mouse_pos.y, 15, 15, self.strip_preview)
                    self.placement_node = _start_node
                    self.start_node = _start_node


                if event.key == pygame.K_ESCAPE and (self.state == "placing node" or self.state == "placing transition"):
                    self.placement_node = None
                    self.state = "idle"
                
                if event.key == pygame.K_LSHIFT and self.state == "node editor":
                    self.state = "placing transition"

                #Delete the selected node
                if event.key == pygame.K_DELETE and self.state == "node editor":
                    self.node_editor.de_select_node() #Deselect to remove the editor options
                    self.remove_node(self.selected_node) # remove node from this timeline layer
                    self.selected_node = None
                    self.state = "idle" #now idle

                #Delete the selected transition
                if event.key == pygame.K_DELETE and self.state == "transition editor":
                    self.transition_editor.de_select_transition() #Deselect to remove the editor options
                    self.remove_transition(self.selected_transition) # remove node from this timeline layer
                    self.selected_transition = None
                    self.state = "idle" #now idle

                #Start timeline iteration
                #   sets the timeline iterator to the start and clears activated nodes
                if event.key == pygame.K_SPACE:
                    self.reset()

                #Save nodes to an external file
                if event.key == pygame.K_s:

                    def scrape_node(node):
                        _out = {}
                        _out["settings"] = node.settings_copy()
                        _out["pos"] = node.get_pos().get_pos()
                        _out["tags"] = node.get_tags()

                        return _out

                    file = fh.TextFile(SAVE_FILE_NAME, "./")
                    _out_nodes = []
                    _added_node_objects = [] #List of CLASSES of transition
                    _out_transitions = []

                    for transition in self.transitions:
                        _transition = {}

                        _from_node = scrape_node(transition.from_node)
                        _out_nodes.append(_from_node)
                        _added_node_objects.append(_from_node)
                        _transition["from_node"] = len(_out_nodes)-1

                        _to_node = scrape_node(transition.to_node)
                        _out_nodes.append(_to_node)
                        _added_node_objects.append(_to_node)
                        _transition["to_node"] = len(_out_nodes)-1

                        _transition["pos"] = transition.get_pos().get_pos()

                        _out_transitions.append(_transition)



                    for node in self.nodes:
                        if node not in _added_node_objects:
                            _out = scrape_node(node)

                            _out_nodes.append(_out)


                    file.write(json.dumps([_out_nodes, _out_transitions]))

                    file.close()

                #Load nodes from an external file
                if event.key == pygame.K_l:
                    file = fh.TextFile(LOAD_FILE_NAME, "./")

                    def create_node_from_json(node_json):
                        _pos = node_json["pos"]

                        if "single" in node_json["tags"]:
                            node = SinglePixelNode(self.surface, self.timeline_ui.camera, _pos[0], _pos[1], 15, 15, self.strip_preview)
                        elif "fill" in node_json["tags"]:
                            node = FillNode(self.surface, self.timeline_ui.camera, _pos[0], _pos[1], 15, 15, self.strip_preview)
                        elif "gradient_sub_node" in node_json["tags"]:
                            node = GradientSubNode(self.surface, self.timeline_ui.camera, _pos[0], _pos[1], 15, 15, self.strip_preview)
                        elif "gradient" in node_json["tags"]:
                            node = GradientNode(self.surface, self.timeline_ui.camera, _pos[0], _pos[1], 15, 15, self.strip_preview)
                        elif "terminate" in node_json["tags"]:
                            node = TerminateNode(self.surface, self.timeline_ui.camera, _pos[0], _pos[1], 15, 15, self.strip_preview, self)
                        elif "start" in node_json["tags"]:
                            node = StartNode(self.surface, self.timeline_ui.camera, _pos[0], _pos[1], 15, 15, self.strip_preview)
                            self.start_node = node
                        else:
                            node = None
                            print("Error with loading node:")
                            print(node_json)
                            raise Exception("Cannot load node")

                        if node != None:
                            for setting in node_json["settings"].keys():
                                node.set_settings(setting, node_json["settings"][setting])

                            self.add_node(node)

                            return node
                    
                    _json = json.loads(file.read())
                    _added_node_indexes = []

                    for transition_json in _json[1]:
                        _pos = transition_json["pos"]

                        _from_node = create_node_from_json(_json[0][transition_json["from_node"]])
                        _to_node = create_node_from_json(_json[0][transition_json["to_node"]])

                        transition = TransitionNode(self.surface, self.timeline_ui.camera, _from_node, _to_node, self.strip_preview)
                        self.add_transition(transition)

                    for node_json_i in range(0, len(_json[0])):
                        if node_json_i in _added_node_indexes:
                            continue

                        node_json = _json[0][node_json_i]
                        create_node_from_json(node_json)
                        


                    file.close()
            
            #If mouse is pressed and mouse is within timeline's range
            if event.type == pygame.MOUSEBUTTONDOWN and self.timeline_ui.collision_point(mouse_pos) and self.state == "placing node":
                self.state = "idle"

                #Add node to layer and node list
                self.add_node(self.placement_node)
                self.placement_node = None # reset placement node

            #Create a transition node
            if event.type == pygame.MOUSEBUTTONDOWN and self.state == "placing transition":
                select_node = False #this is used for node deselection

                #Find node mouse is colliding with
                for node in self.nodes:
                    #Check if mouse's world pos is in node's range
                    if (node.collision_point(node.to_world_pos(mouse_pos)) and 
                        select_node == False and 
                        type(node) == type(self.selected_node) and
                        node.get_pos().y == self.selected_node.get_pos().y):

                        _transition = TransitionNode(self.surface, self.timeline_ui.camera, self.selected_node, node, self.strip_preview)
                        self.add_transition(_transition)
                        self.state = "idle"
                        select_node = True
                        break

                if select_node == False:
                    self.state = "idle"
                    self.node_editor.de_select_node()

    
            #Node selection; only possible when idle or editing node
            #   mouse must be in timeline
            if event.type == pygame.MOUSEBUTTONDOWN and (self.state == "idle" or self.state == "node editor" or self.state == "transition editor") and self.timeline_ui.collision_point(mouse_pos):

                select_node = False #this is used for node deselection

                #Find node mouse is colliding with
                for node in self.nodes:
                    #Check if mouse's world pos is in node's range
                    if node.collision_point(node.to_world_pos(mouse_pos)) and select_node == False:

                        self.transition_editor.de_select_transition()
                        self.selected_node = node
                        self.node_editor.set_node(node) #set the node in the editor for colour changes
                        self.state = "node editor"
                        select_node = True
                        break

                #Find transition mouse is colliding with
                for transition in self.transitions:
                    if transition.collision_point(transition.to_world_pos(mouse_pos)):
                        
                        self.node_editor.de_select_node()
                        self.selected_transition = transition
                        self.transition_editor.set_transition(transition)
                        self.state = "transition editor"
                        select_node = True
                        break
    
                #Node de-selection
                if select_node == False:
                    self.state = "idle"
                    self.node_editor.de_select_node()
                    self.transition_editor.de_select_transition()



        if self.state == "placing node" and self.placement_node != None:
            snap = self.timeline_ui.grid_increments #grid increments are the amount of steps per grid line
            offset = 0.5 * self.placement_node.size

            _mpos = self.placement_node.to_world_pos(mouse_pos)

            #This snaps the node to a grid line
            placement_vector.set_pos(round(_mpos.x, snap.x, offset.x), round(_mpos.y, snap.y, offset.y))

            #Place the node into the timeline
            self.placement_node.set_pos(*placement_vector.get_pos()) 


    def create_UI(self):
        elements = []
        grid_x_increment = 50

        #Timeline UI
        _pos = ptc(0, 11.53)
        _size = ptc(33.87, 7.45)
        _element = Timeline(self.surface, _pos.x, _pos.y, _size.x, _size.y, grid_x_increment, 50, grid_x_increment * TIMELINE_DURATION)
        _element.bgcol = COLOURS["dark_grey"].get_rgb()
        _element.scroll_bar.bgcol = COLOURS["light_grey"].get_rgb()
        _element.scroll_widget.bgcol = COLOURS["light_grey"].get_rgb()
        self.timeline_ui = _element
        elements.append(_element)

        #left Panel
        _pos = ptc(0.71, 0.61)
        _size = ptc(13.39, 8.81)
        _element = Rectangle(self.surface, _pos.x, _pos.y, _size.x, _size.y)
        _element.bgcol = COLOURS["dark_grey"].get_rgb()
        elements.append(_element)

        #Middle Panel
        _pos = ptc(14.42, 0.61)
        _size = ptc(3.55, 8.81)
        _element = Rectangle(self.surface, _pos.x, _pos.y, _size.x, _size.y)
        _element.bgcol = COLOURS["dark_grey"].get_rgb()
        elements.append(_element)

        #Right Panel
        _pos = ptc(18.86, 0.61)
        _size = ptc(13.98, 8.81)
        _element = Rectangle(self.surface, _pos.x, _pos.y, _size.x, _size.y)
        _element.bgcol = COLOURS["dark_grey"].get_rgb()
        elements.append(_element)

        #Timeline iterator is the thing that goes accross the timeline activating nodes
        _speed = self.timeline_ui.grid_increments.x #Move at 1 grid increment / second

        #   start at size / 2 to account for camera offset
        self.timeline_iterator = TimelineIterator(self.surface, self.timeline_ui.camera, *(self.timeline_ui.get_pos() + Vector(self.timeline_ui.size.x/2, 0)).get_pos(), 0, self.timeline_ui.size.y, _speed)
        # self.timeline_iterator.velocity *= self.timeline_ui.scale #move faster if scaled upwards
        self.timeline_ui.timeline_layer.add_objects(single_obj=self.timeline_iterator)

        self.add_UIelements(element_list=elements)

    def draw(self):
        super().draw()

        if self.placement_node != None:
            self.placement_node.draw()


'''
This draws the strip preview across the screen
'''
class StripPreview(Layer):
    def __init__(self, layer_name, pixel_count, surface):
        super().__init__(layer_name)
        self.surface = surface
        self.pixel_count = pixel_count

        self.pixels = np.zeros([pixel_count, 3], dtype=np.uint16)
        # self.pixels.fill(255)

        self.offset = 0
        self.sub_nodes = []

        self._pos = Vector(*ptc(0, 9.87).get_pos())
        self.size = Vector(*ptc(0, 1.2).get_pos())

        # self.pixels = [Colour((255, 255, 255)) for i in range(pixel_count)]

    #Returns the array of pixels which are drawn
    def get_pixels(self, copy=False):
        if copy == True:
            return self.pixels.copy()
        else:
            return self.pixels

    def reset(self):
        self.pixels = np.zeros([self.pixel_count, 3], dtype=np.uint16)

    def shift_pixels(self, amount):
        self.offset += amount

    def draw(self):
        super().draw()

        #Draw the strip preview
        top = ptc(0, 9.87).y
        height = ptc(0, 1.2).y

        #With numpy
        for pixel_i, pixel in enumerate(self.pixels):
            try:
                xpos = self.offset + pixel_i * SCREEN_SIZE.x /self.pixel_count
                if xpos < 0:
                    xpos += SCREEN_SIZE.x
                elif xpos > SCREEN_SIZE.x:
                    xpos -= SCREEN_SIZE.x

                #offset % screen size to allow screen scrolling
                #   sub 4 to avoid some strange effect on screen edge
                _rect = pygame.Rect(xpos, self._pos.y, int(SCREEN_SIZE.x/self.pixel_count)+1, self.size.y)
                pygame.draw.rect(self.surface, pixel, _rect)

            except ValueError as e:
                print("User colour:", pixel)
                raise ValueError(e)
        
        # for pixel_i, pixel in enumerate(self.pixels):
        #     pygame.draw.rect(self.surface, pixel.get_rgb(), pygame.Rect(pixel_i * SCREEN_SIZE.x /self.pixel_count, top, int(SCREEN_SIZE.x/self.pixel_count)+1, height))


    
    