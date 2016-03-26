from event import Event
import operator

FINISHED =  0
ARRIVED = 1
EPOCH = 2

class EventQueue():
    def __init__(self,time):
        self.elements = []
        self.create(time)
        
    def create(self,time):
        for epoch in range(24):
            if time < epoch:
                self.elements.append(Event(EPOCH,epoch))
        self.elements.sort(key=operator.attrgetter("time"), reverse=False)
        
    def pop(self):
        event = self.elements.pop(0)
        return event
    
    def insert(self,Event):
        self.elements.append(Event)
        self.elements.sort(key=operator.attrgetter("time"), reverse=False)
    
    def hasNext(self):
        return len(self.elements)>0
        
    