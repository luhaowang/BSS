from battery import Battery
class Ev(Battery):
    def __init__(self,idx, soc,soc_nom,vmax, ts, reqsoc):
        Battery.__init__(self, idx, soc, soc_nom, vmax, ts)
        self.reqsoc = reqsoc
    