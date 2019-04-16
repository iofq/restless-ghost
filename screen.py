import pyautogui

def findImage(img):
    try:
        loc = pyautogui.locateOnScreen(img, confidence=.4)
    except pyautogui.ImageNotFoundException as e:
        print(e)
        return None
    return(loc.left, loc.top, loc.width, loc.height)
def screenSize():
    size = pyautogui.size()
    return (size.width, size.height)
def findOSRSWindow():
    pass


def test():
    x = findImage('osrs.jpg')
    print(x)
    pyautogui.moveTo(x[0], x[1])
test()
