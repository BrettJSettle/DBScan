"""
@author: Brett Settle
@Department: UCI Neurobiology and Behavioral Science
@Lab: Parker Lab
@Date: August 6, 2015
"""
import os,sys,inspect
from BioDocks import *
from PyQt4.QtGui import *
app = QApplication(sys.argv)
from Analyzer import *
from DataHandler import *
from RandDists import gen

def prepare(d):
    global op
    fs = d['Files'].split(', ')
    if len(fs) == 0:
        print("No files found")
        sys.exit(0)

    for f in fs:
        name = os.path.basename(f)[:-4]
        data = file_to_arr(f)
        if type(data) == dict:
            op = ParameterWidget('Where are the X and Y coordinates', [{'key': 'Xc', 'name': 'X Coordinate', 'value': sort_closest(data.keys(), 'Xc')},\
                {'key': 'Yc', 'name': 'Y Coordinate', 'value': sort_closest(data.keys(), 'Yc')}], doneButton=True)
            op.done.connect(lambda d2: dbscan(name, np.transpose([data[d2['Xc']], data[d2['Yc']]]), d['Epsilon'], d['minP']))
            op.show()
        else:
            dbscan(name, np.transpose(data[0], data[1]), d['Epsilon'], d['minP'])

    with open("ParameterLog.txt", "w+") as outFile:
        outFile.write("\n%d\t%d\t" % (d['Epsilon'], d['minP']))

def dbscan(name, points, eps, minP):
    clusters = scan(points, eps, minP)
    if len(clusters) == 0:
        print('No Clusters Found')
        return
    print("Analyzing Areas...")
    areas = [concaveArea(clust) for clust in clusters]
    print("Analyzing Centers...")
    centers = [getCenter(clust) for clust in clusters]
    distances = []
    closests = []
    for i in range(len(centers)):
        distances.extend(getDistances(centers[i], centers[i + 1:]))
        closests.append(getClosest(centers[i], centers))
    print("Saving Results...")
    toFiles(name, clusters, centers, areas, distances, closests)
    print("Simulating results...")
    pnts = len(clusters)
    x, y = np.transpose(points)
    gen(pnts, [min(x), max(x)], [min(y), max(y)], name)
    print("Done")

ops = [{'key': 'Select files', 'type': 'action', 'value' : lambda : None},\
{'key': 'Files', 'value':''}, {'key': 'Epsilon', 'value': 30}, {'key': 'minP', 'name': 'Minimum Cluster Size', 'value': 10}]
op = ParameterWidget('DBScan Options', ops, doneButton=True)
op.parameters.param('Select files').sigActivated.connect(lambda : op.parameters.__setitem__('Files', \
    ', '.join(getFilenames(title='Select text files to perform Density Scan', filter='Text Files (*.txt)'))))
op.done.connect(prepare)
op.show()
if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    QApplication.instance().exec_()
    QApplication.closeAllWindows()
