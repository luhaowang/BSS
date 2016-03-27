

import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets, svm

Month = '5'
Day = '18' 
datasetNum = '1'
station1_1_dataset = open('station1_monday_dataset'+datasetNum+'.csv','r')
line = station1_1_dataset.readline()
line = station1_1_dataset.readline()
X1 = []
Y1 = []
while line:
    line_splitted = line.strip('\n').split(',')
    X1.append([float(line_splitted[0]),float(line_splitted[1])])
    Y1.append(float(line_splitted[2]))
    line = station1_1_dataset.readline()
station1_1_dataset.close()

Month = '5'
Day = '25' 
datasetNum = '2'
station1_1_dataset = open('station1_monday_dataset'+datasetNum+'.csv','r')
line = station1_1_dataset.readline()
line = station1_1_dataset.readline()
X2 = []
Y2 = []
while line:
    line_splitted = line.strip('\n').split(',')
    X2.append([float(line_splitted[0]),float(line_splitted[1])])
    Y2.append(float(line_splitted[2]))
    line = station1_1_dataset.readline()
station1_1_dataset.close()



n_sample = len(X1)

X_train = np.array(X1)
y_train = Y1
X_test = np.array(X2)
y_test = Y2
# fit the model
clf = svm.SVC(decision_function_shape='ovo')
clf.fit(X_train, y_train)
plt.figure(1)
plt.clf()
plt.scatter(X_train[:, 0], X_train[:, 1], c=y_train, zorder=10, cmap=plt.cm.Paired)
plt.scatter(X_test[:, 0], X_test[:, 1])
x_min = X_train[:, 0].min()
x_max = X_train[:, 0].max()
y_min = X_train[:, 1].min()
y_max = X_train[:, 1].max()
XX, YY = np.mgrid[x_min:x_max:200j, y_min:y_max:200j]
print 'prediction'
print clf.predict([0.02,2])
Z = clf.predict(np.stack((XX.ravel(), YY.ravel()),axis =-1))
# Put the result into a color plot
Z = Z.reshape(XX.shape)
plt.pcolormesh(XX, YY, Z, cmap=plt.cm.Paired)
#plt.contour(XX, YY, Z, colors=['k', 'k', 'k'], linestyles=['--', '-', '--'],
#            levels=[-.5, 0, .5])
plt.show()
