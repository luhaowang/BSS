FINISHED =  0
ARRIVED = 1
EPOCH = 2
class Event():
    def __init__(self,Type,Time,ID =None):
        self.type = Type
        self.time = Time
        self.id = ID
        
        