import numpy as np
from copy import copy, deepcopy
if __name__ == '__main__':
    '''
    station1 = open('station1.csv','r')
    station1_w1 = open('station1_1.csv','w')
    line = station1.readline()
    station1_w1.write(line)
    line = station1.readline()
    while line:
        line_splitted = line.split(',')
        if line_splitted[6]=='1':
            station1_w1.write(line)
        line = station1.readline()
    station1_w1.close()
    station1.close()
    '''
    # 05/18 05/25 06/01 06/08
    Month = '5'
    Day = '25' 
    datasetNum = '2'
    station1_1_handle = open('station1_1.csv','r')
    station1_1_dataset1 = open('station1_monday_dataset'+datasetNum+'.csv','w')
    line = station1_1_handle.readline()
    station1_1_dataset1.write('time,charging_demand,number')
    station1_1_dataset1.write('\n')
    line = station1_1_handle.readline()
    prev_line_splitted  = None
    prev_time_idx = 0
    time_prev =0
    current_time_idx = 0
    a_prev = None
    while line:
        if line.split(',')[4]==Month and line.split(',')[5]==Day:
        line_splitted = line.split(',')
        current_time_idx = line_splitted[3]
        if current_time_idx != prev_time_idx:
            time_now = (float(line_splitted[7])-1)*1+float(line_splitted[8])*1.0/60.0
            a = np.zeros(17)
            a[int(round(float(line_splitted[9])))] +=1
        else:
            a[int(round(float(line_splitted[9])))] +=1
        if current_time_idx != prev_time_idx and prev_line_splitted != None and a_prev != None:
            for j in range(len(a)):
                station1_1_dataset1.write(str(time_prev))
                station1_1_dataset1.write(','+str(j+1))
                station1_1_dataset1.write(','+str(a_prev[j]))
                station1_1_dataset1.write('\n')
        a_prev=copy(a)
        time_prev = float("{0:.2f}".format(time_now))
        prev_line_splitted = copy(line_splitted)
        prev_time_idx = current_time_idx
        line = station1_1_handle.readline()
    station1_1_handle.close()
    station1_1_dataset1.close()   
            
        
    