# sandbox
CI, Sim, and Script Testing

## Rules of Go Moses, Go!

- Moses is represented by an “M” (for now). He is front of all other agents and only moves in a straight line in the middle of the grid. He is ultimately moving from the far middle left of the grid to the far middle right. 

- Moses moves one grid space at a time, in the previously mentioned straight line from middle left to middle right.

- Moses and all his followers move over 40 turns representing 40 years. We will start with having 50 followers organized in 5 rows of 10 columns behind Moses.

- All followers can move two moves in any direction, with a 50% (modifiable constant) chance to move in the same direction as Moses each turn.

- Followers can move in any direction including diagonally, but are unable to move into the same space another follower will move into. They must move to an available grid square with no other agent present in it, even if it is less than 2 squares away. 

- Followers will be represented with I + their number to keep track of them and for bug testing. So “I1” would be the first follower, “I50” the last.

- Diagonals count as a single space.

- If any follower is more than 10 spaces away from Moses for 2 turns and is adjacent to one other follower or less, they “die of thirst in the desert”. When this happens that agent stops moving and is permanently represented with “D” in their resting space for the remainder of the simulation’s 40 turns 

- If three or more adjacent followers are more than 10 turns away from Moses for 5 turns, they all get changed to “V” symbols and stop moving for the rest of the simulation to represent that they founded a village. 

- When Moses makes it to the promised land, any follower agent that is not dead or in a village has won the game. The ending screen shows the results. 
