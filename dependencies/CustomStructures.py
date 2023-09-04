import math
import numpy as np

'''
Stack data structure
initialisation attributes:
    max_size
private variables:
    stack []
    size int
    max_size int

public methods:
    is_empty()
    is_full()
    push(val)
    peek()
    pop()
    get_size()
'''
class Stack:
    def __init__(self, max_size):
        #Set all attributes to private using __
        #   max_size : maximum size of the stack
        #   size : the current count of items; also acts as a head pointer
        #   stack : the list holding the stack's items
        self.__max_size = max_size
        self.__size = 0
        self.__stack = []

    #Performs a check if the stack contains any items
    def is_empty(self):
        #Stack doesnt contain items if the size/head pointer is at 0
        if self.__size == 0:
            return True #return true if empty

        return False #return false if not empty

    #Performs a check if the stack has reached its size limit
    #   size limit is specified upon stack initilisation
    def is_full(self):
        #Stack has reached size limit if size equals specified maximum size
        if self.__size == self.__max_size:
            return True #return true if full

        return False #return false if not full

    #Adds an item to the end of the list
    #   acts as pushing to the stack
    #given item can be of any data type
    def push(self, item):
        #Perform an error test if the stack is full
        if self.is_full() == True:
            #Raise error to inform developer that the stack is full
            raise Exception("Error. Cannot perform push; stack is full")
            return -1

        #Add item to the end of the stack using "size" pointer
        #   determine to increase the size of the array using append
        #   or use the stack pointer
        if self.__size < len(self.__stack):
            self.__stack[self.__size] = item
        else:
            self.__stack.append(item)
        self.__size += 1 #Increment stack size/head pointer

    #Returns the last item on the stack without removing the item
    def peek(self):
        if self.is_empty() == True:
            #Raise error for peak in case of any unexpected results with returning a placeholder
            raise Exception("Error. Cannot perform peek; stack is empty")

        #Return "size-1" as "size" points to the next free, empty location
        return self.__stack[self.__size - 1]

    #Returns the last item on the stack, removing the item
    def pop(self):
        if self.is_empty() == True:
            #Raise error to avoid unexpected results of returning and error code
            raise Exception("Error. Cannot perform pop; stack is empty")

        #Set output to "size-1" as "size" points to the next empty, free location
        _output = self.__stack[self.__size - 1] #Get the back item
        self.__size -= 1 #Decrement stack size, deleting the previous item
        return _output

    #Get method for stack size
    def get_size(self):
        return self.__size

    #Return the list of objects in the stack
    def get_list(self):
        return self.__stack.copy()

    #Display the stack list and size when printed
    def __repr__(self):
        return f"stack contents: {self.__stack[:self.__size]}; size : {self.__size}; list contents: {self.__stack}"

'''
Vector data structure
Stores an x and y component whilst providing some useful mathematical functions
Methods:
    get_pos() : Returns the x and y of the vector as a tuple
    get_mag() : Calculates and returns the magnitude of the vector
    set_pos(x, y) : Set the x and y coordinate of the vector
    normalised() : Returns the direction of the vector
    dot(inp) : Returns the dot product of the given vector
    dir(inp) : Calculates the angle between two vectors
'''
class Vector:
    #x and y are public as methods should calculate using the x and y every time they are called
    #   this means x and y are freely changeable
    def __init__(self, x, y):
        self.x = x
        self.y = y

    #Returns a tuple containing the x and y component of the vector
    def get_pos(self):
        return (self.x, self.y)

    #Returns the magnitude of the vector
    #   Mag = sqrt(a^2 + b^2)
    def get_mag(self):
        return math.sqrt(self.x**2 + self.y**2)

    #Set the x and y coordinate of the vector
    def set_pos(self, x, y):
        self.x = x
        self.y = y

    #Set method for x (optional)
    def set_x(self, x):
        self.x = x

    #Set method for y (optional)
    def set_y(self, y):
        self.y = y

    #Returns the normalised vector (direction)
    #   Unit vector = 1/mag * vector
    def normalised(self):
        _mag = self.get_mag()
        if _mag != 0:
            return Vector(self.x / _mag, self.y / _mag)
        else:
            return Vector(0, 0)

    #Return the sign of each vector component
    def sign(self):
        _x = 0
        if self.x < 0:
            _x = -1
        elif self.x > 0:
            _x = 1
        if abs(self.x) <= 0.01:
            _x = 0

        _y = 0
        if self.y < 0:
            _y = -1
        elif self.y > 0:
            _y = 1
        if abs(self.y) <= 0.01:
            _y = 0

        return Vector(_x, _y)

    #Return the sign of a single number
    def sign_single(self, inp):
        _x = 0
        if inp < 0:
            _x = -1
        elif inp > 0:
            _x = 1
        return _x


    #Returns the dot product between two vectors
    #   dot(a, b) = a.x*b.x + a.y*b.y
    def dot(self, inp):
        return inp.x * self.x + inp.y * self.y

    #Returns the angle between two vectors (in radians)
    def angle(self, inp):
        return math.acos(self.dot(inp) / (self.get_mag()*inp.get_mag())) * self.sign_single(self.x * inp.y - self.y * inp.x)

    #Apply matrix transformation on vector
    #   col1 = Column 1 of matrix
    #   col2 = Column 2 of matrix
    def transformation(self, col1, col2):
        return Vector(col1.x * self.x + col2.x * self.y, col1.y * self.x + col2.y * self.y)

    #Returns the absolute value of the vector
    def abs(self):
        return Vector(abs(self.x), abs(self.y))

    #Performs linear interpolation between two vectors
    #   inp : the second vector to interpolate between (from self)
    #   t : percentage (0 <= t <= 1) along two vectors
    def lerp(self, inp, t):
        # return ((1 - t) * self) +  t * inp 
        return self + t * (inp - self) 

    #Returns a printable version of the vector
    def __repr__(self):
        return f"{(self.x, self.y)}"

    #Allows adding between two vectors
    def __add__(self, inp):
        return Vector(self.x + inp.x, self.y + inp.y)

    #Allows subtraction of vectors
    def __sub__(self, inp):
        return Vector(self.x - inp.x, self.y - inp.y)

    #Version 2:
    #Allows multiplication of a constant
    def __rmul__(self, inp):
        return Vector(self.x * inp, self.y * inp)

    #Performs an integer cast on the contents of the vector
    def int(self):
        return Vector(int(self.x), int(self.y))

    #Allows to index the vector
    #   Vector[0] = x
    #   Vector[1] = y
    def __getitem__(self, indices):
        if indices == 0:
            return self.x
        elif indices == 1:
            return self.y
        else:
            raise Exception("Error; Invalid index for Vector indexing")

'''
Queue data structure
Functions as a circular queue
private attributes:
    max_size : the maximum size of the queue
    queue : the list containing the queue items
    back : the pointer at the back free location
    front: the pointer at the first item in the queue

methods:
    is_empty() : returns true/false depending on if the queue is empty
    is_full() : returns true/false depending on if the queue is full
    enqueue(item) : adds an item to the end of the queue
    dequeue() : removes an item from the front of the queue, returning the item
    head() : returns the front item of the queue, without removing the item
    get_size() : returns the current number of items in the queue
'''
class Queue:
    #max_size is the only parameter, which determines the capacity of the queue
    def __init__(self, max_size):
        self.__max_size = max_size #queue capacity
        self.__queue = [0 for i in range(max_size)] #create a list of placeholders, all zeroes
        self.__back = 0 #pointer to the next free location
        self.__front = 0 #pointer to the front item

    #Validation, checking the queue is empty
    #   makes use of the "get_size" method
    #returns true if the queue is empty
    def is_empty(self):
        if self.get_size() == 0:
            return True
        
        return False

    #Validation checking the queue is full
    #   makes use of the "get_size" method
    #returns true if the queue is full
    def is_full(self):
        if self.get_size() == self.__max_size:
            return True
        
        return False

    def __len__(self):
        return self.get_size()

    #Add an element to the back of the queue
    #   raises an error if the queue is full, this avoids unexpected outcomes
    #   does not return a value
    def enqueue(self, item):
        #Perform the validation check, raises an error if cannot add another item
        #   items will be overriden without this validation
        if self.is_full():
            raise Exception("Error. Cannot perform enqueue; queue is full")
        
        #Assign the new value to the queue list
        #   use back % max_size to cycle the values of the "back" pointer
        #   this enables the queue to be circular
        self.__queue[self.__back % self.__max_size] = item
        self.__back += 1 #Increment the back pointer

    #Remove an element from the front of the queue
    #   raises an error if the queue is empty, this avoids unexpected outcomes
    #   returns the front element removed
    def dequeue(self):
        #Perform the validation check, raises an error if cannot remove another item
        #   returning an error code could create unexpected outcomes in code
        if self.is_empty():
            raise Exception("Error. Cannot perfrom dequeue; queue is empty")

        #Uses front % max size to cycle the values of the "front" pointer
        #   this gives the queue a circular structure
        output = self.__queue[self.__front % self.__max_size]
        self.__front += 1
        return output

    #Returns the size of the queue
    def get_size(self):
        #Size = front pointer - back pointer
        return self.__back - self.__front

    #Returns the front item of the queue, without removing the item
    def head(self):
        #Perform validation check, raises an error if the queue is empty
        #   need to raise an error as returning an error code creates unexpected outcomes
        if self.is_empty():
            raise Exception("Error. Cannot perform head; queue is empty")
        
        #Return the front % max_size index
        #   perform % operation to give the queue a circular structure
        return self.__queue[self.__front % self.__max_size]

    #Returns the back item of the queue, without removing the item
    def tail(self):
        #Perform validation check, raises an error if the queue is empty
        #   need to raise an error as returning an error code creates unexpected outcomes
        if self.is_empty():
            raise Exception("Error. Cannot perform tail; queue is empty")

        #Return the front % max_size index
        #   perform % operation to give the queue a circular structure
        return self.__queue[(self.__back-1) % self.__max_size]

    #Resets the class
    def clear(self):
        self.__init__(self.__max_size)

    #Prints the queue list, front pointer, and back pointer
    def __repr__(self):
        return f"Queue: {self.__queue}; Front:{self.__front}; Back:{self.__back}"


'''
Priority queue
Functions like a linear queue but elements are added in order of a giver priority
Highest priority is always at the front of the queue
private attributes:
    max_size : the maximum size of the queue
    queue : the list containing the queue items
    back : the pointer at the back free location
    front: the pointer at the first item in the queue

methods:
    is_empty() : returns true/false depending on if the queue is empty
    is_full() : returns true/false depending on if the queue is full
    enqueue(item, priority) : adds an item to the end of the queue using given priority
    dequeue() : removes an item from the front of the queue, returning the item
    head() : returns the front item of the queue, without removing the item
    get_size() : returns the current number of items in the queue
'''
class PriorityQueue:
    #max_size is the only parameter, which determines the capacity of the queue
    def __init__(self, max_size):
        self.__max_size = max_size #queue capacity
        #Queue is a 2d array
        #   index 0 = data; index 1 = priority
        self.__queue = [(0, 0) for i in range(max_size)] #create a list of placeholders, all zeroes
        self.__back = 0 #pointer to the next free location
        self.__front = 0 #pointer to the front most item

    #Validation, checking the queue is empty
    #   makes use of the "get_size" method
    #returns true if the queue is empty
    def is_empty(self):
        if self.get_size() == 0:
            return True
        
        return False

    #Validation checking the queue is full
    #   makes use of the "get_size" method
    #returns true if the queue is full
    def is_full(self):
        if self.get_size() == self.__max_size:
            return True
        
        return False

    #Add an element to the back of the queue
    #   raises an error if the queue is full, this avoids unexpected outcomes
    #   does not return a value
    def enqueue(self, item, priority):
        #Perform the validation check, raises an error if cannot add another item
        #   items will be overriden without this validation
        if self.is_full():
            raise Exception("Error. Cannot perform enqueue; queue is full")
        
        #Find the location to insert new element
        #   loop through the queue list until a higher priority is met
        for index in range(self.__front, self.__back+1):

            #Priority check, if priority is now higher...
            if priority > self.__queue[index % self.__max_size][1]:
                #Shift elements accross the queue
                #   loop from back of queue to the new index
                #   shift elements one-by-one
                for index2 in range(self.__back, index, -1):
                    #Element shift
                    self.__queue[index2 % self.__max_size] = self.__queue[(index2-1) % self.__max_size]

                #Insert item
                self.__queue[index % self.__max_size] = (item, priority)

                break

        self.__back += 1

    #Remove an element from the front of the queue
    #   raises an error if the queue is empty, this avoids unexpected outcomes
    #   returns the front element removed
    def dequeue(self):
        #Perform the validation check, raises an error if cannot remove another item
        #   returning an error code could create unexpected outcomes in code
        if self.is_empty():
            raise Exception("Error. Cannot perfrom dequeue; queue is empty")

        #Uses front % max size to cycle the values of the "front" pointer
        #   this gives the queue a circular structure
        output = self.__queue[self.__front % self.__max_size]

        self.__front += 1
        return output[0]

    #Useful for looping with the queue to remove all elements
    #   e.g "for item in queue.dequeue_iterator():"
    def dequeue_iterator(self):

        while self.is_empty() == False:
            yield self.dequeue()

    #Returns the size of the queue
    def get_size(self):
        #Size = front pointer - back pointer
        return self.__back - self.__front

    #Returns the front item of the queue, without removing the item
    def head(self):
        #Perform validation check, raises an error if the queue is empty
        #   need to raise an error as returning an error code creates unexpected outcomes
        if self.is_empty():
            raise Exception("Error. Cannot perform head; queue is empty")
        
        #Return the front % max_size index
        #   perform % operation to give the queue a circular structure
        return self.__queue[self.__front % self.__max_size][0] #Output data contents with index [0]

    #Returns the back item of the queue, without removing the item
    def tail(self):
        #Perform validation check, raises an error if the queue is empty
        if self.is_empty():
            raise Exception("Error. Cannot perform head; queue is empty")
        
        #Return the front % max_size index
        #   perform % operation to give the queue a circular structure
        return self.__queue[(self.__back-1) % self.__max_size][0] #Output data contents with index [0]

    #Returns a copy of self
    def copy(self):
        _out = PriorityQueue(self.__max_size)
        for element in self.__queue:
            _out.enqueue(element[0], element[1])
        return _out

    #Clears the queue
    def clear(self):
        self.__front = 0
        self.__back = 0
        self.__queue = [(0, 0) for i in range(max_size)] #create a list of placeholders, all zeroes

    #Prints the queue list, front pointer, and back pointer
    def __repr__(self):
        return f"Queue: {self.__queue}; Front:{self.__front}; Back:{self.__back}"

#V2
class PriorityQueue2(Queue):
    #max_size is the only parameter, which determines the capacity of the queue
    def __init__(self, max_size):
        self._Queue__max_size = max_size #queue capacity
        #Queue is a 2d array
        #   index 0 = data; index 1 = priority
        self._Queue__queue = [(0, 0) for i in range(max_size)] #create a list of placeholders, all zeroes
        self._Queue__back = 0 #pointer to the next free location
        self._Queue__front = 0 #pointer to the front most item


    #Add an element to the back of the queue
    #   raises an error if the queue is full, this avoids unexpected outcomes
    #   does not return a value
    def enqueue(self, item, priority):
        #Perform the validation check, raises an error if cannot add another item
        #   items will be overriden without this validation
        if self.is_full():
            raise Exception("Error. Cannot perform enqueue; queue is full")
        
        #Find the location to insert new element
        #   loop through the queue list until a higher priority is met
        for index in range(self._Queue__front, self._Queue__back+1):

            #Priority check, if priority is now higher...
            if priority > self._Queue__queue[index % self._Queue__max_size][1]:
                #Shift elements accross the queue
                #   loop from back of queue to the new index
                #   shift elements one-by-one
                for index2 in range(self._Queue__back, index, -1):
                    #Element shift
                    self._Queue__queue[index2 % self._Queue__max_size] = self._Queue__queue[(index2-1) % self._Queue__max_size]

                #Insert item
                self._Queue__queue[index % self._Queue__max_size] = (item, priority)

                break

        self._Queue__back += 1
    
    #Useful for looping with the queue to remove all elements
    #   e.g "for item in queue.dequeue_iterator():"
    def dequeue_iterator(self):

        while self.is_empty() == False:
            yield self.dequeue()

    def dequeue(self):
        return super().dequeue()[0]

'''
Network class
Used to forward pass a set of data through a neural network

Parameters:
    sequence : array of the node counts for each layer
        sequence[layer_index] = node count
    weights : the weights the network should use
    biases : the biases the network should use
    gen_new : generate the network with random numbers using the given sequence
'''
class Network:

    def __init__(self, sequence, weights=[], biases=[], gen_new=True):
        self.weights = weights.copy()
        self.biases = biases.copy()
        self.sequence = sequence

        #Randomly generate network with given node counts for each layer
        if gen_new == True:
            for layer_i in range(1, len(sequence)):
                #Generate values from -5 to 5 (1 to 10 then subtract 5)
                # self.weights.append(np.random.randint(10, size=(sequence[layer_i], sequence[layer_i-1])) - 5)
                # self.biases.append(np.random.randint(10, size=(sequence[layer_i], 1)) - 5)
                self.weights.append(np.random.rand(sequence[layer_i], sequence[layer_i-1]) - 0.5)
                self.biases.append(np.random.rand(sequence[layer_i], 1) - 0.5)

        self.activation = self.sigmoid_activation
        self.activation_np = np.vectorize(self.activation)

        #weights[layer_i][node_i][weight_i]
        #   this means the number of weights is the number of columns for each node and the number of previous nodes

    #Sets the weights and biases of the network
    def set_network(self, weights, biases):
        self.weights = weights.copy()
        self.biases = biases.copy()


    #Forward an array of inputs through network
    #   inp : "2D array", each element corresponds to the value passed to the node on the input layer
    #   e.g [[1,], [2,], [3,]] 
    def forward(self, inp):
        output = np.copy(inp)

        for weights, biases in zip(self.weights, self.biases):
            #matrix multiplication of weights matrix * output matrix
            output = np.matmul(weights, output) + biases
            output = self.activation_np(output)

        return output

    #sigmoid function
    #   1 / 1 + e^-x
    #   math.exp(x) = e^x
    def sigmoid_activation(self, inp):
        return 1 / (1 + math.exp(-inp))

    def __repr__(self):
        out = ""

        #Display all weights and biases in network
        for layer_i in range(0, len(self.sequence)-1):
            print("Node count:", self.sequence[layer_i+1])
            print(self.weights[layer_i])
            print("+")
            print(self.biases[layer_i])
            print("\n")

        return out

'''
Handles colour data
    Includes conversions between colours
    Includes arithmetic with the colours
Makes use of numpy
'''
class Colour:
    def __init__(self, rgb=(0, 0, 0), light=False):
        if light == False:
            self.set_rgb(rgb)
        else:
            self._rgb = np.array(rgb)
            self._hsv = np.array((0,0,0))
            self._hex = "000000"

    #Convert each to tuple as they are numpy arrays (except hex code)
    def get_rgb(self, dtype=np.int16):
        return tuple(self._rgb.astype(dtype))

    def get_hsv(self):
        return tuple(self._hsv)

    def get_hex(self):
        return self.beautify_hex(self._hex)

    #Sets the rgb code
    #converts to all other code also
    #   rgb : rgb code as tuple in range 0 - 255
    def set_rgb(self, rgb):
        _arr = np.array(rgb)
        np.clip(_arr, 0, 255, out=_arr) #Clamp rgb range from 0 to 255
        _arr = _arr.astype(int) #cast to integers
    
        self._rgb = _arr.copy()

        #Set the hsv code
        _arr = np.array(self.rgb_to_hsv(rgb))
        self._hsv = _arr.copy()

        #Set hex code
        _arr = np.array(self.rgb_to_hex(rgb))
        self._hex = np.array(_arr).copy()

    
    #Sets hsv code
    #converts to all other codes also
    #   hsv : hsv code as tuple in format (0-360, 0-100, 0-100)
    def set_hsv(self, hsv):
        _arr = [*hsv]
        _arr[0] = min(360, _arr[0]) #h
        _arr[1] = min(100, _arr[1]) #s
        _arr[2] = min(100, _arr[2]) #v

        _arr = np.array(_arr)
        np.maximum(_arr, 0, out=_arr) #Clamp all value to be above 0
        _arr = _arr.astype(int) #cast to integers
        self._hsv = _arr.copy()

        #Set the rgb code
        _arr = np.array(self.hsv_to_rgb(hsv))
        self._rgb = _arr.copy()

        #Set hex code
        _arr = np.array(self.rgb_to_hex(self.get_rgb()))
        self._hex = np.array(_arr).copy()

    #Sets the hex code
    #   converts to all other codes also
    #   hex : hex code in format #000000
    def set_hex(self, hex):
        hex = hex.replace("#","")
        if len(hex) < 6:
            raise Exception("Error; Hex code is too short. Needs to be in format '#000000'")
        
        r = hex[:2]
        g = hex[2:4]
        b = hex[4:6]
        self._hex = (r, g, b)

        #Convert to rgb
        _rgb = self.hex_to_rgb(hex)
        self._rgb = np.array(_rgb) 

        #Convert to hsv
        _hsv = self.rgb_to_hsv(_rgb)
        self._hsv = np.array(_hsv)



    #Returns the fraction of 255 for the rgb code (range 0 - 1)
    def get_rgb_normalised(self):
        _arr = self._rgb/255
        return tuple(_arr)

    #Returns the fraction of hsv code (range 0 - 1)
    def get_hsv_normalised(self):
        _arr = self._hsv
        return (_arr[0]/360, _arr[1]/100, _arr[2]/100)


    #Convert rgb code to hsv code
    #   rgb code as tuple in range 0 - 255
    #   outputs hsv as (0-360, 0-100, 0-100)
    def rgb_to_hsv(self, rgb):
        r, g, b = tuple(np.clip(rgb, 0, 255).astype(int)) #Clamp rgb range from 0 to 255 and cast to integers

        max_val = max(r, g, b)
        min_val = min(r, g, b)
        delta = max_val - min_val

        #Compute hue
        if delta == 0:
            h = 0
        elif max_val == r:
            h = int((60 * ((g - b) / delta) + 360) % 360)
        elif max_val == g:
            h = int((60 * ((b - r) / delta) + 120) % 360)
        else:
            h = int((60 * ((r - g) / delta) + 240) % 360)

        #Compute saturation
        if max_val == 0:
            s = 0
        else:
            s = int((delta / max_val) * 100)

        #Compute value
        v = int((max_val / 255) * 100)

        return (h, s, v)

    #Convert denary to hex
    #   include padding of 0 if number is 1 digit
    #does not return in the python hex format, returns as string without the "0x"
    def denary_to_hex(self, denary):
        _hex = np.base_repr(denary, base=16)
        if len(_hex) == 1:
            _hex = "0"+_hex
        return _hex

    #Convert hex to denary
    #   returns integer
    def hex_to_denary(self, hex):
        return int(hex, 16) #convert to integer in base 16


    #Convert rgb code to hex code
    #   rgb : input rgb tuple
    #output hex as tuple of hex values as strings
    def rgb_to_hex(self, rgb):
        _arr = np.array(rgb)
        np.clip(_arr, 0, 255, out=_arr) #Clamp rgb range from 0 to 255
        _arr = _arr.astype(int) #cast to integers

        
        #Vectorsied calls the function on each element in the array
        vectorised_func = np.vectorize(self.denary_to_hex)
        _arr = vectorised_func(_arr)

        #Convert to hex and include hashtag
        return tuple(_arr)


    #Convert hex code to rgb code
    #   hsv : input hsv tuple (0-360, 0-100, 0-100)
    def hsv_to_rgb(self, hsv):
        _arr = [*hsv]
        _arr[0] = min(360, _arr[0]) #h
        _arr[1] = min(100, _arr[1]) #s
        _arr[2] = min(100, _arr[2]) #v

        _arr = np.array(_arr)
        np.maximum(_arr, 0, out=_arr) #Clamp all value to be above 0
        _arr = _arr.astype(int) #cast to integers
        H, S, V = tuple(_arr)

        S = S / 100
        V = V / 100

        C = V * S
        X = C * (1 - abs((H / 60) % 2 - 1)) #i have no idea why this works i just found a formula online
        m = V - C

        #Calculate the rgb values relative to H
        if 0 <= H < 60 or H == 360:
            r = C
            g = X
            b = 0
        if 60 <= H < 120:
            r = X
            g = C
            b = 0
        if 120 <= H < 180:
            r = 0
            g = C
            b = X
        if 180 <= H < 240:
            r = 0
            g = X
            b = C
        if 240 <= H < 300:
            r = X
            g = 0
            b = C
        if 300 <= H < 360:
            r = C
            g = 0
            b = X

        return (int((r + m) * 255), int((g + m)*255), int((b + m)*255))
    
    #Convert given hex code to an rgb code
    #   hex : hex code to convert in format '#000000'
    #returns rgb code in range 0-255
    def hex_to_rgb(self, hex):
        hex = hex.replace("#","")
        if len(hex) < 6:
            raise Exception("Error; Hex code is too short. Needs to be in format '#000000'")

        r = hex[:2]
        g = hex[2:4]
        b = hex[4:6]
        _hex = np.array([r, g, b])

        vectorised_func = np.vectorize(self.hex_to_denary)
        return tuple(vectorised_func(_hex))
        


    #Convert tuple of hex into single string with hashtag
    def beautify_hex(self, hex):
        return "#"+"".join(tuple(hex))



    #Linearly interpolates between two colour values
    #   outputs rgb code , not new object
    def lerp(self, inp, t):
        # if t >= 0:
        #     _rgb = self._rgb + (inp._rgb - self._rgb) * t
        # else:
        #     _rgb = inp._rgb + (inp._rgb - self._rgb) * t
        t = min(1, max(0, t))
        _rgb = self._rgb + (inp._rgb - self._rgb) * abs(t)
        return Colour(rgb=_rgb, light=True)

    def invert(self):
        _rgb = np.array([255, 255, 255]) - self._rgb
        return Colour(rgb=tuple(_rgb))

    #Adds the colour codes of the rgbs
    #   should automatically clamp values
    def __add__(self, inp):
        col = Colour()
        col.set_rgb(self._rgb + inp._rgb)
        return col

    #Subtracts the colour codes of the rgbs
    #   should automatically clamp values
    def __sub__(self, inp):
        col = Colour()
        col.set_rgb(self._rgb - inp._rgb)
        return col

    #Multiplies colour codes
    def __rmul__(self, inp):
        col = Colour()
        col.set_rgb(inp * self._rgb)
        return col

    def __mul__(self, inp):
        col = Colour()
        col.set_rgb(inp * self._rgb)
        return col
    
    def __repr__(self):
        return f"RGB: {self.get_rgb()}, HSV: {self.get_hsv()}, HEX: {self.get_hex()}"

if __name__ == "__main__":
    col = Colour()
    col.set_rgb((255, 0, 0))
    col2 = Colour()
    col2.set_rgb((0, 0, 255))
    print(col.lerp(col2, -0.1))





