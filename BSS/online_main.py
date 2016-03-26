import matlab.engine
from battery import Battery
from event import Event
from event_queue import EventQueue
from random import random, uniform
from math import factorial,exp, floor
from ev import Ev
import operator
import matplotlib.pyplot as plt 

INF = 99999
DELTAT = 0.25
Beta = 1.2
CapticalCost = 30.0
Alpha = 0.225
BatTotNum = 100
TRAFCOEF = 40
LAMBDA = [0, 0.3, 0.6, 0.6, 2]
Traffic = TRAFCOEF *3
SOC_NOM = 100
VMAX = 20
SOC_LEVEL = [0,0.25,0.5,0.75,1.00]
FINISHED = 0
ARRIVED = 1
EPOCH = 2
ETYPE = ["FINISHED","ARRIVED","EPOCH"]
CHARGING = 1
IDLE = 2
QOS = 0.95
prices =[2.3,2.2,2,1.9,1.9,2.2,1.6,2.6,2.6,2.9,3.3,4,5,5.3,6.1,7.9,9.2,8.2,5.6,4.7,4.6,3.4,3,2.4]

def BSS_start(ResBatNum):
    f = open('battery_init.dat', 'w')
    reserved_array = []
    for i in range(ResBatNum):
        soc_nom = SOC_NOM
        vmax = VMAX
        soc = soc_nom*random()
        ts = 0 
        reserved_array.append(Battery('0' +'_'+str(i),soc,soc_nom,vmax, ts))
    for i in range(len(reserved_array)):
        f.write('%s \t %f \t %f \t %f \t %f \t \n' %(reserved_array[i].id, reserved_array[i].soc,reserved_array[i].soc_nom,reserved_array[i].vmax, reserved_array[i].ts))
    f.close()
    return reserved_array

def BSS_request():
    f = open('traffic.dat', 'w')
    
    lamda = 3
    TotNum = lamda * TRAFCOEF
    requested_array = []
    for i in range(TotNum):
        soc_nom = SOC_NOM
        soc = soc_nom*random()
        ts = 24*random()
        soc_rt = uniform(soc,SOC_NOM+SOC_NOM*0.1)
        for j in range(len(SOC_LEVEL)-1):
            if soc_rt >= SOC_LEVEL[j]*SOC_NOM and soc_rt < SOC_LEVEL[j+1]*SOC_NOM:
                idx = j
                if SOC_LEVEL[idx]*SOC_NOM <= soc_rt:
                    idx +=1
            if soc_rt > SOC_LEVEL[len(SOC_LEVEL)-1]*SOC_NOM:
                idx = len(SOC_LEVEL)-1
                break
        vmax = VMAX
        requested_array.append(Ev('1' +'_'+str(i),soc,soc_nom,vmax, ts,SOC_LEVEL[idx]*SOC_NOM))
    requested_array.sort(key=operator.attrgetter("ts"), reverse=False)
    for i in range(len(requested_array)):
        f.write('%s \t %f \t %f \t %f \t %f \t %f \n' %(requested_array[i].id, requested_array[i].soc,requested_array[i].soc_nom,requested_array[i].vmax, requested_array[i].ts,requested_array[i].reqsoc))
    f.close()
    return requested_array

    
def evProvisioner(arrivRate,deltaT,qos):
    N = -1
    mu = arrivRate*deltaT
    qqos = 0
    while(qqos<qos):
        N += 1 
        qqos = 0
        for i in range(N+1):
            qqos += exp(-mu) * mu**i / factorial(i)
    return N

'''

use ILP to solve the level assignment and deadline setting problem

'''
def batteryCharAssigner(ResBatArray,ArriRate,deltaT,ENG):
    eng = ENG
    eng.clear
    eng.clc
    N = []
    for i in range(len(ArriRate)):
        N.append(evProvisioner(ArriRate[i], deltaT, QOS))
    print N
    SOCs = []
    SOClevs = SOC_LEVEL
    Vmaxs = []
    for i in range(len(ResBatArray)):
        SOCs.append(ResBatArray[i].soc)
        Vmaxs.append(ResBatArray[i].vmax)
    mxij = len(ResBatArray)*len(SOClevs)
    mj = len(SOClevs)
    mi = len(ResBatArray)
    F = eng.ones(mxij,1)
    for i in range(len(SOCs)):
        for j in range(len(SOClevs)):
            F[i*len(SOClevs)+j][0] = f(SOCs[i],SOClevs[j]*SOC_NOM)
    #print 'F'
    #print F
    intcon = eng.zeros(mxij,1)
    for i in range(mxij):
        intcon[i][0] = intcon[i][0] + i + 1
    lb = eng.zeros(mxij,1 )
    ub = eng.ones( mxij,1 )
    Aeq = eng.zeros(mi,mxij)
    beq = eng.ones(mi,1)
    for i in range(mi):
        for j in range(mj):
            Aeq[i][i*mj+j] = 1
    A = eng.zeros(mj+mi,mxij)
    b = eng.zeros(mj+mi,1)
    for i in range(mj+mi):
        if i<mj:
            b[i][0] = -N[i]
        elif i>=mj:
            b[i][0] = SOCs[i-mj] + Vmaxs[i-mj]*deltaT
            
    for i in range(mj+mi):
        for j in range(mxij):
            if (i< mj) and (j%mj==i):
                A[i][j]=-1
            if (i>= mj):
                for k in range(mj):
                    A[i][(i-mj)*mj+k] = SOClevs[k]*SOC_NOM
    eng.workspace['F'] = F
    eng.workspace['intcon'] = intcon
    eng.workspace['A'] = A
    eng.workspace['b'] = b
    eng.workspace['Aeq'] = Aeq
    eng.workspace['beq'] = beq
    eng.workspace['lb'] = lb
    eng.workspace['ub'] = ub
    eng.eval('options = optimoptions(\'intlinprog\',\'Display\',\'off\');',nargout=0);
    eng.eval('x = intlinprog(F,intcon,A,b,Aeq,beq,lb,ub,options);',nargout=0)
    x = eng.workspace['x']
    return x
    
def batteryCharScheduler(ResBatArray,ArriRate,deltaT,ENG):
    N = int(2 / deltaT)
    mi = len(ResBatArray)
    mj = len(SOC_LEVEL)
    for n in range(N):
        x = batteryCharAssigner(ResBatArray,ArriRate,(n+1)*deltaT,ENG)
       
        if len(x) == 0:
            print "\n \t\t\t No feasible assignment! \n"
            print "batteryCharScheduler fail fullfil the future %f" %((n+1)*deltaT)
            continue
            
        print "batteryCharScheduler is predicting the future %f" %((n+1)*deltaT)

            
        #print x
        #print "length of x %d\n" %len(x)
        '''
        for i in range(mi):
            print "\n"
            for j in range(mj):
                print "%s" %x[i*mj+j][0],
        '''
        for i in range(mi):
            levidx = -1
            #print "\n"
            for j in range(mj):
                #print "\t %s" %x[i*mj+j][0],
                if (str(x[i*mj+j][0]) == '1.0'):
                    levidx = j
            if levidx == -1:
                print "\n error for finding the target soc\n"
            target  = x[i*mj+levidx][0]*SOC_LEVEL[levidx]*SOC_NOM
            #print "\n battery %s target %d is %f\n" %(ResBatArray[i].id,levidx,target)
            if target > ResBatArray[i].soc:
                if  ResBatArray[i].state == IDLE:
                    ResBatArray[i].set_state(CHARGING)
                    ResBatArray[i].set_td((n+1)*deltaT+ResBatArray[i].get_ts())
                    ResBatArray[i].set_targetsoc(target) 
                elif ResBatArray[i].state == CHARGING:
                    if (target - ResBatArray[i].soc)/ ((n+1)*deltaT)> ( ResBatArray[i].soc_target - ResBatArray[i].soc)/ (ResBatArray[i].td - ResBatArray[i].get_ts()):
                        ResBatArray[i].set_state(CHARGING)
                        ResBatArray[i].set_td((n+1)*deltaT+ResBatArray[i].get_ts())
                        ResBatArray[i].set_targetsoc(target)   
    for i in range(mi):
        if ResBatArray[i].state == CHARGING:
            return True
    return False
        #printBatInfor(battery_array)

def printBatInfor(battery_array):
    print "\t batteryID \t batterySOC \t battery_targetSOC \t StartTIme  \t Deadline \t Rate \t\t State "    
    for i in range(len(battery_array)):
        print "\t %s \t \t %f \t %f \t \t %f  \t %f \t %f \t %d \t %f " %(battery_array[i].id,battery_array[i].soc,battery_array[i].soc_target,battery_array[i].ts, battery_array[i].td,battery_array[i].rate,battery_array[i].state, battery_array[i].cost   )
    print "\n"
                   
        
def f(SOCi,SOCj):
    if SOCi >= SOCj:
        return 0
    elif SOCi < SOCj:
        return (SOCj-SOCi)        

def updateBatInfo(battery_array,time):
    batNum = len(battery_array)
    for i in range(batNum):
        battery_array[i].soc += (time-battery_array[i].ts)*battery_array[i].rate
        battery_array[i].cost += (time-battery_array[i].ts)*battery_array[i].rate*battery_array[i].energyprice
        battery_array[i].set_ts(time)
        battery_array[i].set_energyprice(prices[int(floor(time)) % 24])
        if abs(battery_array[i].soc - battery_array[i].soc_target)< 0.05:
            battery_array[i].soc = battery_array[i].soc_target
            battery_array[i].rate = 0
            battery_array[i].set_state(IDLE)
            battery_array[i].set_td(24)
        if time == battery_array[i].td:
            battery_array[i].soc = battery_array[i].soc_target
            battery_array[i].rate = 0
            battery_array[i].set_state(IDLE)
            battery_array[i].set_td(24)
            

def swapBat(battery_array,eventNow,ev_array):
    mbat = len(battery_array)
    mev = len(ev_array)
    for i in range(mev):
        if ev_array[i].id == eventNow.id:
            ev_idx = i
    MIN = INF
    Swapped = -1
    for i in range(mbat):
        if battery_array[i].soc >= ev_array[ev_idx].reqsoc:
            Swapped = ev_idx
            diff = battery_array[i].soc - ev_array[ev_idx].reqsoc
            if diff < MIN:
                MIN = diff
                bat_idx = i
    if Swapped == -1:
        print "No battery can swap\n"
    else:
        del battery_array[bat_idx]
        battery_array.append(Battery(ev_array[ev_idx].id, ev_array[ev_idx].soc,ev_array[ev_idx].soc_nom,ev_array[ev_idx].vmax, ev_array[ev_idx].ts))
    return Swapped
    
def updateEventQueue(battery_array,ev_array,time):
    EventQ = EventQueue(time)
    for i in range(len(ev_array)):
        if ev_array[i].get_ts() > time:
            EventQ.insert(Event(ARRIVED,ev_array[i].get_ts(), ev_array[i].get_id()))
    for i in range(len(battery_array)):
        if battery_array[i].get_td() > time and battery_array[i].get_td() < 24:
            EventQ.insert(Event(FINISHED,battery_array[i].get_td(), battery_array[i].get_id()))
    return EventQ  
            
def printEventQ(EventQ):
    for i in range(len(EventQ.elements)):
        print "\t %s \t %f \t %s " %(ETYPE[EventQ.elements[i].type],EventQ.elements[i].time,EventQ.elements[i].id)    

def chargingScheduler(battery_array,time,ENG):
    print "chargingScheduler is calculating the optimal Charging rate at time %f. \n" %(time)
    tpoints = []
    tpoints.append(time)
    charidx = []
    SOCs = []
    TargetSOCs = []
    Vmaxs = []
    for i in range(24+1):
        if i > time:
            tpoints.append(float(i))
    for i in range(len(battery_array)):
        if battery_array[i].state == CHARGING:
            charidx.append(i)
            SOCs.append(battery_array[i].soc)
            TargetSOCs.append(battery_array[i].soc_target)
            Vmaxs.append(battery_array[i].vmax)
            tpoints.append(battery_array[i].td)
    tpoints = list(set(tpoints))
    tpoints.sort()
    #print tpoints
    intvidx = []
    for i in range(len(charidx)):
        intvidx.append(tpoints.index(battery_array[charidx[i]].td))
    tintv = []
    energyprice_intv = []
    for i in range(len(tpoints)-1):
        tintv.append(tpoints[i+1]-tpoints[i])
    '''    
    print "\n tintv %d\t" %(len(tintv))
    print tintv
    print "\n tpoints %d \t" %(len(tpoints))
    print tpoints
    '''
    for i in range(len(tintv)):
        energyprice_intv.append(prices[int ( floor(tpoints[i]) ) % 24])
        #print "int ( floor(tpoints[i]) ) : %d" %(int ( floor(tpoints[i]) ))
    
    #print energyprice_intv
    '''
    fmincon in matlab
    '''   
    eng = ENG
    eng.clear
    eng.clc
    invNum = len(tintv)
    btNum = len(SOCs)
    eng.workspace['invNum'] = invNum
    eng.workspace['btNum'] = btNum
    eng.workspace['Alpha'] = Alpha
    eng.workspace['Beta'] = Beta
    
    #delta_tao = eng.zeros(1,invNum*btNum)
    delta_tao = eng.zeros(1,invNum)
    #for i in range(btNum):
    #    for j in range(invNum):
            #delta_tao[0][i*invNum+j] = tintv[j]*energyprice_intv[j]
    for j in range(invNum):
        delta_tao[0][j] = tintv[j]*energyprice_intv[j]
    eng.workspace['delta_tao'] = delta_tao
    
    auxMatrix = eng.zeros(invNum,btNum*invNum)
    for j in range(invNum):
        for i in range(btNum):
            auxMatrix[j][i*invNum+j] = 1
    eng.workspace['auxMatrix'] = auxMatrix 
          
    eng.eval('fun = @(x)(delta_tao*(Alpha*(auxMatrix*x).^2+Beta*auxMatrix*x));',nargout=0)
    
    #eng.eval('fun = @(x)(delta_tao*(Alpha*x.^2+Beta*x));',nargout=0)
    
    A = eng.zeros(btNum,btNum*invNum)
    for i in range(btNum):
        for j in range(invNum):
            A[i][i*invNum+j] = -1*tintv[j]
    eng.workspace['A'] = A
    
      
    b = eng.zeros(btNum,1)
    if btNum >1:
        for i in range(btNum):
            b[i][0] = -1.0*(TargetSOCs[i] - SOCs[i])
    elif btNum == 1:
        b = -1.0*(TargetSOCs[i] - SOCs[i])
    eng.workspace['b'] = b
    
    '''    
    Aeq = eng.zeros(btNum,btNum*invNum)
    for i in range(btNum):
        for j in range(invNum):
            if j>= intvidx[i]:
                Aeq[i][i*invNum+j] = 1
    eng.workspace['Aeq'] = Aeq
    print "\nAeq \n"
    for i in range(btNum):
        print Aeq[i]
    
    beq = eng.zeros(len(charidx),1)
    eng.workspace['beq'] = beq
    
    print "\nbeq \n"
    print beq
    '''
    lb = eng.zeros(invNum*btNum,1)
    eng.workspace['lb'] = lb
    
    ub = eng.zeros(invNum*btNum,1)
    for i in range(btNum):
        for j in range(invNum):
            if j>= intvidx[i]:
                ub[i*invNum+j][0] = 0
            else:
                ub[i*invNum+j][0] = Vmaxs[i]
    eng.workspace['ub'] = ub    
              
    eng.eval('x0 = zeros(invNum*btNum,1);',nargout=0)
    eng.eval('options = optimoptions(@fmincon,\'Display\', \'off\',\'TolCon\',1e-12,\'TolX\',1e-12);',nargout=0)
    eng.eval('x = fmincon(fun,x0,A,b,[],[],lb,ub,[],options);',nargout=0)
    x = eng.workspace['x']
    for i in range(btNum):
        idx = charidx[i]
        battery_array[idx].set_rate(x[i*invNum][0])
    # if you want to print the charging rate
    '''
    print tpoints
    for i in range(len(charidx)):
        for j in range(invNum):
            print x[i*invNum+j][0],
            print "\t",
        print "\n"
    '''
     
        
def BSS_request_read(filename):
    f = open(filename,'r')
    ev_array = []
    line = f.readline()
    while(line !=''):
        line = line.split("\t")
        ev_id = line[0]
        soc = line[1]
        soc_nom = line[2]
        vmax = line[3]
        ts = line[4]
        soc_target= line[5]
        ev_array.append(Ev(str(ev_id),float(soc),float(soc_nom),float(vmax), float(ts),float(soc_target)))
        line = f.readline()
    f.close()
    return ev_array

def BSS_start_read(filename):
    f = open(filename,'r')
    bat_array = []
    line = f.readline()
    while(line !=''):
        line = line.split("\t")
        ev_id = line[0]
        soc = line[1]
        soc_nom = line[2]
        vmax = line[3]
        ts = line[4]
        bat_array.append(Battery(str(ev_id),float(soc),float(soc_nom),float(vmax), float(ts)))
        line = f.readline()
    f.close()
    return bat_array
    
def totalCost(CumuCost,BatTotNum,CapticalCost):
    totalCost =CumuCost[-1] + BatTotNum * CapticalCost
    return totalCost

def CumuCost(bat_array,time_series,time,cumucost_points):
    totalCost = 0
    RateSum = 0
    for i in range(len(bat_array)):
        RateSum += bat_array[i].rate
    totalCost = (Alpha*RateSum**2+Beta*RateSum)*(time - bat_array[0].ts)*(bat_array[0].energyprice)
    if (len(cumucost_points)==0):
        cumucost_points.append(totalCost)
    else:
        cumucost_points.append(totalCost + cumucost_points[-1])
    time_series.append(time)
    

if __name__ == '__main__':
    eng = matlab.engine.start_matlab()
    Failcount = 0
    batRecord = []
    time_points = []
    cumucost_points = []
    battery_array = BSS_start(BatTotNum)
    #battery_array = BSS_start_read("battery_init_%d.dat" %(BatTotNum))
    BatTotNum =len(battery_array)
    for i in range(len(battery_array)):  # record all batteries
        batRecord.append(battery_array[i])
    ev_array = BSS_request()
    #ev_array = BSS_request_read("traffic_%d.dat" %(Traffic))
    for i in range(len(ev_array )):
        print "\t %s \t \t %f \t %f \t \t %f  \t %f \t %f \t %d " %(ev_array[i].id,ev_array[i].soc,ev_array[i].soc_target,ev_array[i].ts, ev_array[i].td,ev_array[i].reqsoc,ev_array[i].state   )
    EventQ = EventQueue(-1)
    for i in range(len(ev_array)):
        EventQ.insert(Event(1,ev_array[i].get_ts(), ev_array[i].get_id()))
    printEventQ(EventQ)    
    while(EventQ.hasNext()):
        eventNow = EventQ.pop()
        print "\n-------------------------------------------------------------------------"
        print "\n \t Battery information before process the event at time %f \n" %(eventNow.time)
        printBatInfor(battery_array)
        print "Now Processing the Event \t %s \t %f \t %s " %(ETYPE[eventNow.type],eventNow.time,eventNow.id)
        print "Online"
        print "battery_init_%d.dat" %(BatTotNum)
        print "traffic_%d.dat" %(Traffic)
        if ETYPE[eventNow.type] == "EPOCH":
            CumuCost(battery_array,time_points,eventNow.time,cumucost_points)
            updateBatInfo(battery_array,eventNow.time)
            print "CumuCost = %f\n" %(cumucost_points[-1])
            NeedCharge = batteryCharScheduler(battery_array,LAMBDA,DELTAT,eng)
            EventQ=updateEventQueue(battery_array,ev_array,eventNow.time)
            if NeedCharge==True: 
                chargingScheduler(battery_array,eventNow.time,eng)  
            #printEventQ(EventQ)
            print "\t Battery information After process the event EPOCH \n"
            printBatInfor(battery_array)
            print "\t Battery Record information After process the event EPOCH \n"
            printBatInfor(batRecord)
        elif ETYPE[eventNow.type] == "FINISHED":
            CumuCost(battery_array,time_points,eventNow.time,cumucost_points)
            updateBatInfo(battery_array,eventNow.time)
            print "CumuCost = %f\n" %(cumucost_points[-1])
            NeedCharge = batteryCharScheduler(battery_array,LAMBDA,DELTAT,eng)
            EventQ=updateEventQueue(battery_array,ev_array,eventNow.time)
            if NeedCharge==True: 
                chargingScheduler(battery_array,eventNow.time,eng)  
            #printEventQ(EventQ)
            print "\t Battery information After process the event FINISHED \n"
            printBatInfor(battery_array)
            print "\t Battery Record After process the event FINISHED \n"
            printBatInfor(batRecord)
        elif ETYPE[eventNow.type] == "ARRIVED":
            CumuCost(battery_array,time_points,eventNow.time,cumucost_points)
            updateBatInfo(battery_array,eventNow.time)
            print "CumuCost = %f\n" %(cumucost_points[-1])
            Swapped = swapBat(battery_array,eventNow,ev_array)
            if Swapped == -1: # no battery can be swapped
                Failcount += 1
            else:
                batRecord.append(battery_array[-1])
            updateBatInfo(battery_array,eventNow.time)
            NeedCharge = batteryCharScheduler(battery_array,LAMBDA,DELTAT,eng)
            EventQ=updateEventQueue(battery_array,ev_array,eventNow.time)
            #printEventQ(EventQ)
            if NeedCharge==True: 
                chargingScheduler(battery_array,eventNow.time,eng)  
            print "\t Battery information After process the event ARRIVED \n"
            printBatInfor(battery_array)
            print "\t Battery Record information After process the event ARRIVED \n"
            printBatInfor(batRecord)
    print "\n \t \t Successfully Finish One day!! \n" 
    print "\n \t \t Failures: %d !! \n" %(Failcount)
    printBatInfor(batRecord)  
    
    print "Total cost = %f \n" %totalCost(cumucost_points,BatTotNum,CapticalCost)
    data_save = open("cumudata__opt_opt_%d_%d_%d.dat" %(BatTotNum,Traffic,Failcount),'w')
    for i in range(len(cumucost_points)):
        data_save.write("%f \t %f \n" %(time_points[i],cumucost_points[i]))
    data_save.write(str(LAMBDA))
    data_save.close()
    plt.plot(time_points, cumucost_points, 'ro')
    plt.show()  