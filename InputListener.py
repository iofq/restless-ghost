from pynput.mouse import Button, Listener as MouseListener
from pynput.keyboard import Key, Listener as KeyboardListener
import datetime
import json

class InputListener(MouseListener, KeyboardListener):
  
    def __init__(self, file, offset):
        self.file = file
        self.offset = offset
        self.STOP = False
        self.RECORDING = False
        
        open(file, "w+") #clear file
    
    def on_move(self, x, y):
        if(self.STOP):
            return False
        if(self.RECORDING):
            self.log(TimedEvent(0, self.time_ms(), offset([x,y])))   

    def on_click(self, x, y, button, pressed):
        if(self.STOP):
            return False
        if(self.RECORDING and pressed):
            self.log(TimedEvent(1, self.time_ms(), offset([x,y,button])))
        elif(self.RECORDING and not(pressed)):
            self.log(TimedEvent(2, self.time_ms(), offset([x,y,button])))
       
    def on_scroll(self, x, y, dx, dy):
        if(self.STOP):
            return False
        if(self.RECORDING):
            self.log(TimedEvent(3, self.time_ms(), offset([x,y])))   

    def on_press(self, key):
            
        if key == Key.f8:
            self.RECORDING = not self.RECORDING
            if(self.RECORDING):
                print("Started Recording")
                self.START_TIME = round(datetime.datetime.utcnow().timestamp() * 1000)
            else:
                print("Stopped Recording")
                self.STOP = True
                return False
        if(self.RECORDING and not(key == Key.f8)):
            self.log(TimedEvent(4, self.time_ms(), [key]))   

    def on_release(self, key):
        if(self.RECORDING and not(key == Key.f8)):
            self.log(TimedEvent(5, self.time_ms(), [key]))   

    # Collect events until released by self.STOP
    def start(self):
        with MouseListener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll) as listener:
            with KeyboardListener(
                on_press=self.on_press,
                on_release=self.on_release) as listener:
                listener.join()
        #TODO cleanup, close file, stop thread, ask user to save or delete

    def time_ms(self): 
        return round(datetime.datetime.utcnow().timestamp() * 1000) - self.START_TIME

    def log(self, event):
        with open(self.file, "a") as write_file:
            json.dump(event.json(), write_file)
            write_file.write("\n")

    def offset(self, args):
        return [self.offset[0] - args[0], self.offset[1] - args[1]] + args[2:]


class TimedEvent():

    def __init__(self, code, time, data):
        self.code = code
        self.time = time
        self.data = data

    def __str__(self):
        return '{0} {1} {2}'.format(self.code, self.time, self.data)

    def json(self):
        json = {"code":self.code, "time_ms":self.time}
        for i,d in enumerate(self.data):
            json['data_{0}'.format(i)] = str(d)

        return json

