This file explains the implementation and running of the game SnakeIO.
We used the code provided in the video tutorial and modified it to implement the snake game.
Following are the features of our game:
---------------------------------------
FEATURES
1) Game Starts when all the players connect to the server.
2) Snake dies when he hits the body of other snake.
3) Head-on collision of snakes kills them.
4) If a snake hits its own body part it gets killed.
5) The food objects are rendered on screen and are eatable by the snake.
6) When snake eats the food, it gets enlarged.
7) When the score of a player becomes multiple of 3, the speed of its snake increases thus increasing the difficulty.
8) Once a food object gets eaten, it is rendered at a new randomly generated position.
9) Score of all the players are made visible on the screen of every player.(Every player can see his and as well as other's score)
10 The one who survives till last wins the game.
---------------------------------------
Implementation
- Used the code from the video tutorial provided by the TAs. Modified it to suit our project.
- Used socket library for client-server connection.
- Used pickle library for sending objects containing food and snakes coordinates.
- Used curses library to implement the snake game.
- Added Both bonus features i.e. Score and Food
-------------------------------------------------------
How to Play
1)Start the server by command:
python server.py *IP* *PORT* *Number of players*

2)Connect the clients by command:
pythin client.py *IP* *PORT*

3) Once all the players are connected the game starts.

4) Players can control their snakes by arrow keys i.e. (UP DOWN LEFT RIGHT)

---------------------------------------------------------
Regards,
Mohammad Abdullah (20100144)
Daud Nofel (20110173)
-----------------------------------------------------------
