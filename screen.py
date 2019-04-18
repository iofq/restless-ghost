import pyautogui
import sys

def findImage(img):
    try:
        loc = pyautogui.locateOnScreen(img, confidence=.7)
    except:
        e = sys.exc_info()
        print('error with', e)
        return None
    return(loc.left, loc.top, loc.width, loc.height)
def screenSize():
    size = pyautogui.size()
    return (size.width, size.height)
def findOSRS():
    return findImage('/home/e/pynee/compass.jpg')[:2] #TODO fix this to be ~/pynee/


#def test():
#    x = findImage('/home/e/pynee/backpack.jpg')
#    print(x)
#    x = findOSRS()
#    print(x)
#    pyautogui.moveTo(x)
#test()
