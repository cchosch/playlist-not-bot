import threading

class Heartbeat(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(Heartbeat,self).__init__(*args, **kwargs)
        self.stop = False
    
    def stop_exe(self):
        self.stop = True
    
    def run(self):
        print("hello world")