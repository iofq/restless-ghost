#############TODO
#implement mouse scrolls code==3
#this needs to be heavily refactored
from pynput.keyboard import Key, KeyCode, Controller as KeyboardController
from pynput import keyboard
from pynput.keyboard import _xorg
from pynput.mouse import Button, Controller as MouseController
from pathlib import Path
import random
import contextlib
import sys
import time
import datetime
import json
import screen

k = KeyboardController()
m = MouseController()

MODIFIER_KEYS = ['alt_gr', 'alt', 'cmd', 'ctrl', 'shift']  
pressed = []
hotKey = ""

def load(file):
    data = []
    for l in open(file, 'r'):
        data.append(json.loads(l))
    return list(data)

def run_data(data, offset): #this method needs a refactor
    global m #MouseController must be global because we write to m.position
    global pressed #must be global so we can access it in context managers
    global hotKey
    timeElapsed = data[-1]["time_ms"] - data[0]["time_ms"]
    pressed = []
    startTime = time_ms() 

    for i, d in enumerate(data):
    
        if(hotKey == "quit"):
            quit()

        while(hotKey == "pause"):
            time.sleep(.50)

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
                x = offset[0] - int(d["data_0"])
                y = offset[1] - int(d["data_1"])
            except:
                pass
            m.position = (x,y)

        elif(code in [1,2]):
            try:
                x = offset[0] - int(d["data_0"])
                y = offset[1] - int(d["data_1"])
                button = d["data_2"]
            except:
                pass

            if(button == "Button.left"):
                button = Button(1)
            elif(button == "Button.middle"):
                button = Button(2)
            elif(button == "Button.right"):
                button = Button(3)
            
            with holdKeys(mods):
                if(code == 1):
                    m.press(button)
                    print("click @ ", (x,y), button)

                elif(code == 2):
                    m.release(button)
        
        elif(code in [4,5]):
            try:
                key = (d["data_0"])
            except:
                e = sys.exc_info()
                print('error with', e, "invalid keypress")
            if(len(key.replace("'", "")) == 1):  #is not a special key
                try:
                    if(code == 4):
                        if(key in pressed):
                            k.touch(KeyCode.from_char(key.replace("'", "")), True)
                        else:
                            k.press(KeyCode.from_char(key.replace("'", "")))
                            pressed.append(key)
                    elif(code ==5):
                        k.release(KeyCode.from_char(key.replace("'", "")))
                        if(key in pressed):
                            pressed.remove(key)
                        
                except:
                    e = sys.exc_info()
                    print('error with', e)
            else:
                try:
                    if(code == 4):
                        if(key in pressed):
                            k.touch(_xorg.Key[key], True)
                        else:
                            key = key.split(".")[1].strip('"')
                            k.press(_xorg.Key[key])
                            pressed.append(key)
                    elif(code == 5):
                        key = key.split(".")[1].strip('"')
                        k.release(_xorg.Key[key])
                        if(key in pressed):
                            pressed.remove(key)
                except:
                    e = sys.exc_info()
                    print('error with', e)
            print("pressed key: ", key)


    print("Runtime: ", time_ms() - startTime, " Expected: ", timeStamp)

def run(data, offset):
    run_data(data, offset)
    releaseAll(pressed)

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

def on_press(key):
    global hotKey
    if(key == keyboard.Key.f8):
        if(hotKey == "pause"):
            hotKey = ""
            print('RESUMED')
        else:
            hotKey = "pause"
            print('PAUSED')
    elif(key == keyboard.Key.f10):
        hotKey = "quit"
def on_release(key):
    pass

if(__name__== "__main__"):
    offset = screen.findOSRS()[:2]
    directory = sys.argv[1]
    path = Path.home() / "pynee" / directory

    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()


    if(path.exists()):
        while 1:
            for x in path.iterdir():
                print(x)
                data = load(x)
                run(data, offset)
