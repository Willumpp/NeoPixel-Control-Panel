# NeoPixel-Control-Panel
Provides a GUI (using pygame) to interact with a programmable LED strip.

The controller/remote must be running on a powerful enough machine to run PyGame.
The reciever must be running on a RaspberryPi.

## Controls
- F1 : Creates a "single pixel" node
- F2 : Creates a "fill" node
- F3 : Creates a "gradient" node
- F11 : Creates a "start" node
- F12 : Creates a "terminate" node
- Shift+Click : Create transition node
- Esc : De-select node
- Delete : Delete the selected node
  
## Nodes

### Single pixel node
When activated, only sets one pixel to its colour.

### Fill node
When activated, sets the colour of the entire strip.

### Gradient node
First choose the number of "sub-nodes" to create a gradient between. These will appear on the strip preview when the gradient node is de-selected then selected.
Click on a sub-node to select its colour.
When activated, the node will create a linear gradient between sub-nodes on the strip.

### Start node
The location for which the animation begins

### Terminate node
When activated, the node resets the animation back to the start.

### Transition node
With one node selected, hold Shift and click another node on the same y-axis and of the same type. This creates a transition between the two.
Click on the transition node to edit how each variable is interpolated as the animation progresses through.

## Dependencies
- Pygame
- Numpy
