#############TODO
#implement mouse scrolls code==3
#standardize window via image search
#loop directory for data accumulation
#antiban
#quit hotkey - we'll need another listener
#this needs to be multiple files and heavily refactored
#figure out timing/optimize
from pynput.keyboard import Key, KeyCode, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import _xorg
from pathlib import Path
import random
import contextlib
import sys
import time
import datetime
import scipy
from scipy import interpolate
import math
import pyautogui
import json

k = KeyboardController()
m = MouseController()

MODIFIER_KEYS = ['alt_gr', 'alt', 'cmd', 'ctrl', 'shift']  
pressed = []

def load(file):
    data = []
    for l in open(file, 'r'):
        data.append(json.loads(l))
    return list(data)

def run_data(data): #this method needs a refactor
    global m #MouseController must be global because we write to m.position
    global pressed #must be global so we can access it in context managers
    numSteps = len(data)
    timeElapsed = data[-1]["time_ms"] - data[0]["time_ms"]
    clicks = find_clicks(data)
    pressed = []

    startTime = time_ms() 

    for i, d in enumerate(data):
        #unpack from dict
        code = d["code"]
        timeStamp = d["time_ms"]
        try:
            sleep = data[i+1]["time_ms"] - timeStamp
            if(sleep < 0):
                sleep = 0
        except: #either the data is invalid or it's the last step
            sleep = 0

        sleep = sleep / 1000 #ms
        time.sleep(sleep)

        mods = list(set(pressed).intersection(MODIFIER_KEYS))
        if(mods is None):
            mods = []

        if(code == 0):
            try:
                x = int(d["data_0"])
                y = int(d["data_1"])
            except:
                pass
            m.position = (x,y)


        elif(code == 1):
            try:
                x = int(d["data_0"])
                y = int(d["data_1"])
                button = d["data_2"]
            except:
                pass

            if(button == "Button.left"):
                button = Button(1)
            elif(button == "Button.middle"):
                button = Button(2)
            elif(button == "Button.right"):
                button = Button(3)
            
            print("click @ ", (x,y), button)
            
            with holdKeys(mods):
                m.press(button)
        
        elif(code == 2):
            try:
                x = int(d["data_0"])
                y = int(d["data_1"])
                button = d["data_2"]
            except:
                pass

            #should be able to do Button[button]
            if(button == "Button.left"):
                button = Button(1)
            elif(button == "Button.middle"):
                button = Button(2)
            elif(button == "Button.right"):
                button = Button(3)
            
            print("release @ ", (x,y))
            m.release(button)  


        elif(code == 4):
            try:
                key = (d["data_0"])
            except:
                e = sys.exc_info()
                print('error with', e)
            if(len(key.replace("'", "")) == 1):
                try:
                    if(key in pressed):
                        k.touch(KeyCode.from_char(key.replace("'", "")), True)
                    else:
                        k.press(KeyCode.from_char(key.replace("'", "")))
                        pressed.append(key)
                        
                except:
                    e = sys.exc_info()
                    print('error with', e)
            else:
                try:
                    if(key in pressed):
                        k.touch(_xorg.Key[key], True)
                    else:
                        key = key.split(".")[1].strip('"')
                        k.press(_xorg.Key[key])
                        pressed.append(key)
                except:
                    e = sys.exc_info()
                    print('error with', e)
            print("pressed key: ", key)

        elif(code == 5):
            try:
                key = (d["data_0"])
            except:
                e = sys.exc_info()
                print('error with', e)
            if(len(key.replace("'", "")) == 1):
                try:
                    k.release(KeyCode.from_char(key.replace("'", "")))
                    if(key in pressed):
                        pressed.remove(key)
                except:
                    e = sys.exc_info()
                    print('error with', e)
            else:
                try:
                    key = key.split(".")[1].strip('"')
                    k.release(_xorg.Key[key])
                    if(key in pressed):
                        pressed.remove(key)
                except:
                    e = sys.exc_info()
                    print('error with', e)
            print("released key: ", key)


                
        else:
            #???
            pass

    print("run time: {0} \n expected: {1}".format(time_ms() - startTime, timeElapsed))

####TODO: make startPoint be first click on next data to remove glitchy behavior
def run(data):
    startPoint = m.position
    for i in data:
        if(i["code"] == 1):
            startPoint = (i["data_0"], i["data_1"])
            break
        run_data(data)
        #spline(int(m.position[0]), int(m.position[1]), int(startPoint[0]), int(startPoint[1])) #Natural movement back to start of macro
        print("keys still pressed: ", pressed) #############
        releaseAll(pressed)
        print("after cleanup: ", pressed)

def find_clicks(data):
    clicks = []
    for d in data:
        if(d["code"] == 1):
            clicks.append(d)
    return clicks

def toKey(s):
    if(len(s.replace("'", "")) == 1):
        return KeyCode.from_char(s)
    else:
        return _xorg.Key[s]

def releaseAll(keys):
    for x in keys:
        k.release(toKey(x))
        pressed.remove(x)
       
    pass
@contextlib.contextmanager
def holdKeys(mods):
    """Executes a block with some keys pressed.

    :param mods: The keys to keep pressed.
    """
    for key in mods:
        if key:
            print("holding: ", key)
            k.press(_xorg.Key[key])

    try:
        yield
    finally:
        for key in mods:
            if(key not in pressed):
                print(pressed)
                print("stopped holding: ", key)

def time_ms():
    return round(datetime.datetime.utcnow().timestamp() * 1000)
    
def spline(x1, y1, x2, y2): # x,y start and x,y destination

    cp = random.randint(3, 5)  # Number of control points. Must be at least 2.

    # Distribute control points between start and destination evenly.
    x = scipy.linspace(x1, x2, num=cp, dtype='int')
    y = scipy.linspace(y1, y2, num=cp, dtype='int')

    # Randomise inner points a bit (+-RND at most).
    RND = 10
    xr = scipy.random.randint(-RND, RND, size=cp)
    yr = scipy.random.randint(-RND, RND, size=cp)
    xr[0] = yr[0] = xr[-1] = yr[-1] = 0
    x += xr
    y += yr

    # Approximate using Bezier spline.
    degree = 3 if cp > 3 else cp - 1  # Degree of b-spline. 3 is recommended.
                                      # Must be less than number of control points.
    tck, u = scipy.interpolate.splprep([x, y], k=degree)
    u = scipy.linspace(0, 1, num=max(pyautogui.size()))
    points = scipy.interpolate.splev(u, tck)

    prev = 0
    for point in zip(*(i.astype(int) for i in points)):
        if(not(point == prev)): #remove duplicate points 
            prev = point
            m.position = (point)

def calc_distance(start, finish):
    x1, y1 = start
    x2, y2 = finish
     
    x = abs(x1 - x2)
    y = abs(y1 - y2)
    return math.sqrt(x**2 + y**2)

if(__name__== "__main__"):

    directory = input("script: ")
    path = Path.home() / "pynee" / directory
    if(path.exists()):
        for x in path.iterdir():
            data = load(x)
            run(data)
