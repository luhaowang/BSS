if __name__ == '__main__':
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
        