from pynput import keyboard 

def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def pause():
    input("press enter to resume"):
listener = mouse.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()
