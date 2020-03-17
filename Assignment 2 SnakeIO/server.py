import socket
import socketserver
import sys
from _thread import *
import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_DOWN, KEY_UP
from random import randint
import json
import time
import pickle 
# -------------------------------------------------------------------------------------
HOST = str(sys.argv[1])  # The server's hostname or IP address
PORT = int(sys.argv[2])        # The port used by the server
PLAYERS = int(sys.argv[3])
# HOST = "127.0.0.1"
# PORT = 65432
# PLAYERS = 2

# -------------------------------------------------------------------------------------
WIDTH = 35
HEIGHT = 20
MAX_X = WIDTH - 2
MAX_Y = HEIGHT - 2
SNAKE_LENGTH = 3
SNAKE_X = SNAKE_LENGTH + 1
SNAKE_Y = 3
TIMEOUT = 500

#-------------------------------------------------------------------------------------

class Snake(object):
    REV_DIR_MAP = {
        KEY_UP: KEY_DOWN, KEY_DOWN: KEY_UP,
        KEY_LEFT: KEY_RIGHT, KEY_RIGHT: KEY_LEFT,
    }

    def __init__(self, x, y, window):
        self.body_list = []
        self.hit_score = 0
        self.timeout = TIMEOUT

        for i in range(SNAKE_LENGTH, 0, -1):
            self.body_list.append(Body(x - i, y))

        self.body_list.append(Body(x, y, 'o'))
        self.window = window
        self.direction = KEY_RIGHT
        self.last_head_coor = (x, y)
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
    @property
    def head_collision(self):
        for s in range (len(snake)):
            if snake[s] != self and snake[s].head == self.head:
                killed_snakes.append(snake[s])
                closed_connections.append(con_array[s])
                return True
        return False

    @property
    def side_collision(self):
        for s in snake:
            if s != self:
                return any([body.coor == self.head.coor
                    for body in s.body_list[:-1]])


    @property
    def self_collision(self):
        return any([body.coor == self.head.coor
                    for body in self.body_list[:-1]])

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
    def __init__(self, window, char='*'):
        self.x = randint(1, MAX_X)
        self.y = randint(1, MAX_Y)
        self.char = char
        self.window = window

    def render(self):
        self.window.addstr(self.y, self.x, self.char)

    def reset(self):
        self.x = randint(1, MAX_X-2)
        self.y = randint(1, MAX_Y-2)

def rem_players(num):
    return 'Waiting for remaining Players : {}'.format(PLAYERS - num)
def send_score(scr):
    return 'Your Score is : {}'.format(scr)


#----------------------------------------------------------------------------------

if __name__ == "__main__":
    loop_cond = 1
    closing_msg = "closing"
    congo = "congo"
    done_msg = "done"
    snake = []
    snake_obj_array = []
    closed_connections = []
    killed_snakes = []
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    players_joined = 0
    con_array = []
    cord = {"width": WIDTH , "height": HEIGHT, "timeout": TIMEOUT}
    cord_obj = pickle.dumps(cord)
    while players_joined < PLAYERS:
        print("Waiting for number of players: ", PLAYERS - players_joined)
        conn, addr = s.accept()
        con_array.append(conn)
        players_joined += 1
        conn.sendall(cord_obj)
        msg = rem_players(players_joined)
        conn.sendall(msg.encode())
    startmsg = "All players Connected ! Starting Game"
    for conn in con_array:
        conn.send(startmsg.encode())
    curses.initscr()
    curses.beep()
    window = curses.newwin(HEIGHT, WIDTH, 0, 0)
    window.timeout(TIMEOUT)
    window.keypad(1)
    curses.noecho()
    curses.curs_set(0)
    window.border(0)
    food = Food(window, '*')
    for y in range(len(con_array)):
        snake.append(Snake(SNAKE_X+y, SNAKE_Y+y, window))
    while loop_cond:
        window.clear()
        window.border(0)
        food.render()
        for y in range(len(snake)):
            snake[y].render()
            window.addstr(0, int((WIDTH/PLAYERS)*y), snake[y].score)
        window.refresh()
        f_obj = {"x_coor": food.x , "y_coor": food.y , "fchar": food.char}
        for i in snake:
            snake_obj = {"blist": i.body_list , "score": i.hit_score ,"speed": i.timeout , "x_c": i.last_head_coor[0] , "y_c": i.last_head_coor[1]}
            snake_obj_array.append(snake_obj)
        snake_obj_array.append(f_obj)
        toSend_snake = pickle.dumps(snake_obj_array)
        for co in con_array:
            co.sendall(toSend_snake)
        snake_obj_array = []
        for c in range(len(con_array)):
            mrec = con_array[c].recv(10)
            event = mrec.decode()
            if event == "UP":
                snake[c].change_direction(KEY_UP)
            if event == "DOWN":
                snake[c].change_direction(KEY_DOWN)
            if event == "RIGHT":
                snake[c].change_direction(KEY_RIGHT)
            if event == "LEFT":
                snake[c].change_direction(KEY_LEFT)
        for sn in snake:
            if sn.head.x == food.x and sn.head.y == food.y:
                sn.eat_food(food)
        for i in range(len(snake)):
            snake[i].update()
        for o in range(len(snake)):
            if snake[o].collided or snake[o].self_collision or snake[o].side_collision:
                closed_connections.append(con_array[o])
                killed_snakes.append(snake[o])
        for j in range(len(snake)):
            if snake[j].head_collision:
                if snake[j] not in killed_snakes:
                    killed_snakes.append(snake[j])
                    closed_connections.append(con_array[j])
        for k in range(len(killed_snakes)):
            snake.remove(killed_snakes[k])
        for k in range(len(closed_connections)):
            closed_connections[k].send(closing_msg.encode())
            con_array.remove(closed_connections[k])
        killed_snakes.clear()
        closed_connections.clear()
        if len(snake) < 2:
            loop_cond = 0
            continue
        for conn in con_array:
            conn.send(done_msg.encode())
    curses.endwin()
    if not con_array:
        print("NOBODY WON !!!")
    for i in con_array:
        i.send(congo.encode())
    print("Game Over")
    s.close()



