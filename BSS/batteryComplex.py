CHARGING = 1
IDLE = 2
OneBatCost = 30.0
Beta1 = 1.2
Beta2 = 0.9
IREF = 10.0 # Reference current propotional to the nominal capacity 
VBAT = 220.0


class Battery:
    def __init__(self, id, soc,soc_nom,vmax, ts):
        self.soc = soc
        self.id = id
        self.soc_nom = soc_nom
        self.soc_full = soc_nom
        self.soc_target = soc
        self.vmax = vmax
        self.ts = ts 
        self.td = 24
        self.rate = 0
        self.Pbat = 0
        self.state = IDLE
        self.energyprice = 0
        self.cost = OneBatCost
        self.swapped = False
    
    def set_targetsoc(self,soc_target):
        self.soc_target = soc_target
        
    def get_targetsoc(self):
        return self.soc_target
    
    def set_rate(self,rate):
        self.rate = rate
    
    def get_rate(self):
        return self.rate
    
    def set_td(self,td):
        self.td  = td
    
    def get_td(self):
        return self.td
        
    def get_id(self):
        return self.id
    
    def set_id(self,idd):
        self.id  = idd
    
    def set_ts(self,ts):
        self.ts  = ts
    
    def get_ts(self):
        return self.ts
    
    def set_state(self,state):
        self.state = state
        
    def get_state(self):
        return self.state 
    
    def set_energyprice(self,price):
        self.energyprice = price
        
    def get_energyprice(self):
        return self.energyprice
    
    def get_outputPower(self):
        if self.rate/(VBAT*IREF) > 1: 
            self.Pbat = VBAT*IREF *(self.rate/(VBAT*IREF))**Beta1 
        elif self.rate/(VBAT*IREF) < -1:
            self.Pbat = -1*VBAT*IREF *(abs(self.rate)/(VBAT*IREF))**Beta2 
        elif self.rate/(VBAT*IREF) >= -1 and self.rate/(VBAT*IREF) <= 1:
            self.Pbat = self.rate
        return self.Pbat
    
    def get_SOH_deg(self):
        return (self.soc_nom-self.soc_full)/self.soc_nom
            
            
           
           
        
    