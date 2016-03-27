from matplotlib.colors import ListedColormap
from sklearn.neighbors.nearest_centroid import NearestCentroid
from sklearn import neighbors
import numpy as np
import matplotlib.pyplot as plt


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

Month = '6'
Day = '1' 
datasetNum = '3'
station1_1_dataset = open('station1_monday_dataset'+datasetNum+'.csv','r')
line = station1_1_dataset.readline()
line = station1_1_dataset.readline()
X3 = []
Y3 = []
while line:
    line_splitted = line.strip('\n').split(',')
    X3.append([float(line_splitted[0]),float(line_splitted[1])])
    Y3.append(float(line_splitted[2]))
    line = station1_1_dataset.readline()
station1_1_dataset.close()

Month = '6'
Day = '8' 
datasetNum = '4'
station1_1_dataset = open('station1_monday_dataset'+datasetNum+'.csv','r')
line = station1_1_dataset.readline()
line = station1_1_dataset.readline()
X4 = []
Y4 = []
while line:
    line_splitted = line.strip('\n').split(',')
    X4.append([float(line_splitted[0]),float(line_splitted[1])])
    Y4.append(float(line_splitted[2]))
    line = station1_1_dataset.readline()
station1_1_dataset.close()


X_train = np.vstack((X1,X2,X3,X4))
y_train = np.concatenate((Y1,Y2,Y3,Y4))
X_test = np.array(X4)
y_test = Y4

cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#AAAAFF','#FFFFAA','#FAAAFF','#FAAFFF','#ff0000','#004d00'])
cmap_bold = ListedColormap(['#FF0000', '#00FF00', '#0000FF','#FF00FF','#00FFFF','#000FFF','#ff0000'])


clf = NearestCentroid()
n_neighbors = 10
weights = 'distance'
#clf = neighbors.KNeighborsClassifier(n_neighbors, weights=weights)
clf.fit(X_train, y_train) 
plt.figure(1)
plt.clf()
plt.scatter(X_train[:, 0], X_train[:, 1], c=y_train)
x_min = X_train[:, 0].min()
x_max = X_train[:, 0].max()
y_min = X_train[:, 1].min()
y_max = X_train[:, 1].max()
XX, YY = np.mgrid[x_min:x_max:200j, y_min:y_max:200j]
Z = clf.predict(np.stack((XX.ravel(), YY.ravel()),axis =-1))
# Put the result into a color plot
Z = Z.reshape(XX.shape)
plt.pcolormesh(XX, YY, Z, cmap=cmap_light)
plt.scatter(X_test[:, 0], X_test[:, 1], c=y_test,cmap=cmap_light)
print clf.predict([15.19,2])
plt.show()