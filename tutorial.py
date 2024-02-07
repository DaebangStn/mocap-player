from time import time
from vpython import *

def add_box():
    return box(pos=vec(0, 0, 0), length=0.5, height=0.5, width=0.5, color=color.yellow)


scene = canvas(title='My first box', width=600, height=600)
mybox = add_box()
add_box()
center = sphere(pos=vec(0, 0, 0), radius=0.1, color=color.red)
speed = 0.5


def change_speed(s):
    global speed
    speed = s.value

w = slider(min=0, max=1, value=speed, length=220, bind=change_speed, right=15)

while True:
    rate(100)
    t = time()
    mybox.pos = vec(speed*cos(t), speed*sin(t), 0)

