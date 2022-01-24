import pyautogui
import sys
import os

#TODO
#use mss and opencv to improve speed.. right now takes us over a second to locate OSRS.
#add methods for finding game objects.

def findImage(img):
    try:
        loc = pyautogui.locateOnScreen(img, confidence=.7)
    except:
        e = sys.exc_info()
        print('error with', e)
        return None
    if(loc is None):
        print("Couldn't find OSRS instance...")
        return None
    return(loc.left, loc.top, loc.width, loc.height)
def screenSize():
    size = pyautogui.size()
    return (size.width, size.height)
def findOSRS():
    return findImage(os.path.expanduser("~/pynee/scrot.png"))[:2] #TODO fix this to be ~/pynee/

