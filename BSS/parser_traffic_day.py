from copy import deepcopy
if __name__ == '__main__':
    station1 = open('station1.csv','w')
    station1.write('station_#,tax_index,tax_brand,time_indx,month,day,weekday,hour,minitue,charge_demand')
    station1.write('\n')
    station2 = open('station2.csv','w')
    station2.write('station_#,tax_index,tax_brand,time_indx,month,day,weekday,hour,minitue,charge_demand')
    station2.write('\n')
    station3 = open('station3.csv','w')
    station3.write('station_#,tax_index,tax_brand,time_indx,month,day,weekday,hour,minitue,charge_demand')
    station3.write('\n')
    for i in range(1,537):
        file_handle = open('/home/luhao/Downloads/PEVData/taxi_outputs/Taxi_number(' + str(i)+').csv','r')
        line=file_handle.readline()
        tax_index = line.split(',')[2]
        line=file_handle.readline()
        tax_brand= line.split(',')[2]
        '''
        skip two lines
        '''
        file_handle.readline()
        file_handle.readline()
        '''
        read the data
        '''
        line = file_handle.readline()
        prev_state = 0 # not charging:0, charging: 1
        current_state = 0
        prev_station = '0'
        while line: # the time stamp
            line_splitted  = line.split(',')
            time_indx = line_splitted[1]
            month = line_splitted[2]
            day = line_splitted[3]
            weekday = line_splitted[4]
            hour = line_splitted[5]
            minitue = line_splitted[6]
            parking_station = line_splitted[10]
            power_drawing = float(line_splitted[11])
            #print [time_indx,month,day,weekday,hour,minitue,parking_station,power_drawing]
            line = file_handle.readline()
            start_end_flag = 0 # start and end charging flag, start: 1, end: 2, else: 0
            if (parking_station == '1' or parking_station == '2' or parking_station == '3' ) and power_drawing > 0 :
                current_state = 1
            else:
                current_state = 0
            if prev_state == 0 and current_state == 1:
                charge_demand = 0.0
                start_time = [time_indx,month,day,weekday,hour,minitue]
            if prev_state == 1 and current_state == 0:
                end_time = [time_indx,month,day,weekday,hour,minitue]
                data = [] 
                data.append(prev_station)
                data.append(tax_index)
                data.append(tax_brand)
                data.extend(start_time)
                data.append(charge_demand)
                
                str_to_wrtie =''
                for j in range(len(data)):
                    str_to_wrtie += str(data[j])
                    str_to_wrtie += str(',')
                if data[0] =='1':
                    station1.write(str_to_wrtie)
                    station1.write('\n')
                if data[0] =='2':
                    station2.write(str_to_wrtie)
                    station2.write('\n')
                if data[0] =='3':
                    station3.write(str_to_wrtie)
                    station3.write('\n')
            if current_state == 1:
                charge_demand += float("{0:.2f}".format(power_drawing* 1.0/60.0)) # the time step gap is 1 minitues
            prev_state = current_state
            prev_station = parking_station
        file_handle.close()
    station1.close()
    station2.close()
    station3.close()
        