import socket
import sys
import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_DOWN, KEY_UP
import pickle
from time import sleep
#-------------------------------------------------------------------------------------
class Snake(object):
    REV_DIR_MAP = {
        KEY_UP: KEY_DOWN, KEY_DOWN: KEY_UP,
        KEY_LEFT: KEY_RIGHT, KEY_RIGHT: KEY_LEFT,
    }

    def __init__(self, li,sc,sp,x,y ,window):
        self.body_list = li
        self.hit_score = sc
        self.timeout = TIMEOUT
        self.window = window
        self.direction = KEY_RIGHT
        self.last_head_coor = (x,y)
        self.direction_map = {
            KEY_UP: self.move_up,
            KEY_DOWN: self.move_down,
            KEY_LEFT: self.move_left,
            KEY_RIGHT: self.move_right
        }

    @property
    def score(self):
        return 'Score : {}'.format(self.hit_score)

    def add_body(self, body_list):
        self.body_list.extend(body_list)

    def eat_food(self, food):
        food.reset()
        body = Body(self.last_head_coor[0], self.last_head_coor[1])
        self.body_list.insert(-1, body)
        self.hit_score += 1
        if self.hit_score % 3 == 0:
            self.timeout -= 5
            self.window.timeout(self.timeout)

    @property
    def collided(self):
        if self.head.x == MAX_X or self.head.y == MAX_Y:
            return True
        #return any([body.coor == self.head.coor
        #            for body in self.body_list[:-1]])

    def update(self):
        last_body = self.body_list.pop(0)
        last_body.x = self.body_list[-1].x
        last_body.y = self.body_list[-1].y
        self.body_list.insert(-1, last_body)
        self.last_head_coor = (self.head.x, self.head.y)
        self.direction_map[self.direction]()

    def change_direction(self, direction):
        if direction != Snake.REV_DIR_MAP[self.direction]:
            self.direction = direction

    def render(self):
        for body in self.body_list:
            self.window.addstr(body.y, body.x, body.char)

    @property
    def head(self):
        return self.body_list[-1]

    @property
    def coor(self):
        return self.head.x, self.head.y

    def move_up(self):
        self.head.y -= 1
        if self.head.y < 1:
            self.head.y = MAX_Y

    def move_down(self):
        self.head.y += 1
        if self.head.y > MAX_Y:
            self.head.y = 1

    def move_left(self):
        self.head.x -= 1
        if self.head.x < 1:
            self.head.x = MAX_X

    def move_right(self):
        self.head.x += 1
        if self.head.x > MAX_X:
            self.head.x = 1

class Body(object):
    def __init__(self, x, y, char='-'):
        self.x = x
        self.y = y
        self.char = char

    @property
    def coor(self):
        return self.x, self.y

class Food(object):
    def __init__(self, x,y,z,window):
        self.x = x
        self.y = y
        self.char = z
        self.window = window

    def render(self):
        self.window.addstr(self.y, self.x, self.char)

    def reset(self):
        self.x = randint(1, MAX_X-2)
        self.y = randint(1, MAX_Y-2)

#----------------------------------------------------------------------------------

HOST = str(sys.argv[1])  # The server's hostname or IP address
PORT = int(sys.argv[2])        # The port used by the server
#----------------------------------------------------------------------------------
#WIDTH = 35
#HEIGHT = 20
#TIMEOUT = 500
#----------------------------------------------------------------------------------
if __name__ == '__main__':	
    msg = "Client"
    default = "RIGHT"
    ya = ""
    obj_received = "OBJECT received"
    game_over = "GAMER OVER !"
    looper = 0
    congo = 0
    snake = []
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    cord = s.recv(1024) #Object received. These are the screen coordinates.
    cord_obj = pickle.loads(cord)  #Loads is buit in fucntion that unpacks tha data i,e that was dumped at server end.
    WIDTH = cord_obj['width']
    HEIGHT = cord_obj['height']
    TIMEOUT = cord_obj['timeout']
    data = s.recv(64)
    wait_msg = data.decode() #waiting msg.. how many players still left
    print(wait_msg)
    n_data = s.recv(64)
    while not n_data:
        n_data = s.recv(64)
    print(n_data.decode())
    curses.initscr()
    curses.beep()
    window = curses.newwin(HEIGHT, WIDTH, 0, 0)
    window.timeout(TIMEOUT)
    window.keypad(1)
    curses.noecho()
    curses.curs_set(0)
    window.border(0)
    while True:
        window.clear()
        window.border(0)
        srec = s.recv(4096)
        sobj_arr = pickle.loads(srec)
        fobj = sobj_arr[-1]
        food = Food(fobj['x_coor'], fobj['y_coor'], fobj['fchar'], window)
        sobj_arr.remove(fobj)
        for i in sobj_arr:
            snake.append(Snake(i['blist'] , i['score'], i['speed'], i['x_c'], i['y_c'] , window))
        food.render()
        players = len(snake)
        for i in range(len(snake)):
            snake[i].render()
            window.addstr(0, int((WIDTH/players)*i), snake[i].score)
        window.refresh()
        snake = []
        event = window.getch() #take input from window in form of character i.e Keys UP DOWN LEFT RIGHT
        if event == -1:
            ya = default
        elif event == KEY_UP:
            ya = "UP"
        elif event == KEY_RIGHT:
            ya = "RIGHT"
        elif event == KEY_DOWN:
            ya = "DOWN"
        else:
            ya = "LEFT"
        default = ya
        s.sendall(ya.encode())
        datt = s.recv(10)
        final = datt.decode()
        if final == "closing":
            s.close()
            break
        elif final == "congo":
            s.close()
            congo = 1
            break
        else:
            continue #Game continues if neither the snake has died nor the game has ended i.e You have won.....
    curses.endwin()
    if congo:
        print("YOU WON")
    else:
        print("YOU LOST")
    print("GAME ENDED")

