"""
@author: Brett Settle
@Department: UCI Neurobiology and Behavioral Science
@Lab: Parker Lab
@Date: August 6, 2015
"""
import os,sys,inspect
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import global_vars as g
g.settings = g.Settings()
import pyqtgraph as pg
from FileReader import file_to_array
import time
import numpy as np
from sklearn.cluster import DBSCAN
from ClusterMath import *

class Cluster():
    def __init__(self, points):
        self.points = points
        self.density = len(points)
        self.center = getCenter(points)
        self.area = area(points, g.settings['epsilon'])
        self.gridArea = gridArea(points)
        
def scan(data, epsi, minP, minDensity):
    labels = DBSCAN(eps=epsi, min_samples=minP).fit_predict(data)
    win.statusBar().showMessage('%d Clusters found. Removing small clusters...' % max(labels))
    clusters = []
    rejected = 0
    for i in range(max(labels) + 1):
        clust = []
        for p in np.where(labels == i)[0]:
           clust.append(data[p])
        if len(clust) > minDensity:
            clusters.append(clust)
            rejected += 1
    win.statusBar().showMessage('%d points -> %d Clusters after excluding %d small clusters.' % (len(data), max(labels), rejected))
    return clusters

def save_clusters(filename, clusters):
    data = np.array([[cluster.center[0], cluster.center[1], cluster.density, cluster.area, cluster.gridArea] for cluster in clusters])
    np.savetxt(filename, data, header="Center X\tCenter Y\tDensity\tArea\tArea Grid", delimiter='\t', fmt="%.4f")

def save_distances(filename, centers):
    data = getAllDistances(centers)
    np.savetxt(filename, data, header="Distances", delimiter='\t', fmt="%.4f")

def simulateCenters(filename, count, xrng, yrng):
    pts = np.random.random((count, 2))
    pts[:, 0] = pts[:, 0] * (xrng[1] - xrng[0]) + xrng[0]
    pts[:, 1] = pts[:, 1] * (yrng[1] - yrng[0]) + yrng[0]
    save_distances(filename, pts)

def read_files(filenames):
    x = []
    y = []
    start = time.time()
    for fname in filenames:
        win.statusBar().showMessage("Gathering points from %s..." % fname)
        try:
            d = file_to_array(fname, columns=['Xc', 'Yc'])
            x.extend(d['Xc'])
            y.extend(d['Yc'])
        except Exception as e:
            print("Could not read points from %s\n%s" % (fname, e))
    win.statusBar().showMessage("%d points read (%s s)" % (len(x), time.time() - start))
    return np.vstack([x, y]).T

def save_clusters(clusters):
    d = QFileDialog.getExistingDirectory(caption="Save DBScan results to a directory. Create or select a folder", directory=g.settings['last_dir'])
    t = time.time()
    save_clusters(os.path.join(d, "Clusters.txt"), clusters)
    win.statusBar().showMessage("Cluster Data saved. Calculating distances...")
    centers = [c.center for c in clusters]
    save_distances(os.path.join(d, "Distances.txt"), centers)
    win.statusBar().showMessage("Distances saved.")
    x, y = np.transpose(centers)
    if simulateCheck.isChecked():
        win.statusBar().showMessage("Generating simulated centers...")
        simulateCenters(os.path.join(d, "Simulated_distances.txt"), len(centers), [min(x), max(x)], [min(y), max(y)])
    win.statusBar().showMessage("DBScan Complete. (%s s)" % (time.time() - t))

def main():
    g.settings.update(epsilon=epsilon_spin.value(), min_neighbors=min_neighbors_spin.value(), min_density=min_density_spin.value())
    fnames = [file_list.item(i).text() for i in range(file_list.count())]
    points = read_files(fnames)
    if len(points) == 0:
        return
    t = time.time()
    clusterButton.setEnabled(False)
    clusts = scan(points, g.settings['epsilon'], g.settings['min_neighbors'], g.settings['min_density'])
    clusters = []
    for i in range(len(clusts)):
        clusters.append(Cluster(clusts[i]))
        QApplication.processEvents()
        if i % 10 == 0:
            win.statusBar().showMessage("Analyzed %d clusters of %d" % (i, len(clusts)))
    win.statusBar().showMessage("Clusters Analyzed (%s s)" % (time.time() - t))
    save_clusters(clusters)
    clusterButton.setEnabled(True)

def add_file(filename):
    for i in range(file_list.count()):
        if os.path.samefile(file_list.item(i).text(), filename):
            return
    item = QListWidgetItem(filename)
    file_list.addItem(item)

def remove_file(item):
    file_list.takeItem(file_list.row(item))

def get_files():
    files = QFileDialog.getOpenFileNames(win, caption="Select point files to cluster", directory=g.settings['last_dir'])
    if len(files) == 0:
        return
    g.settings['last_dir'] = os.path.dirname(files[0])
    for i in files:
        add_file(i)

def close_and_save(ev):
    g.settings.save()
    ev.accept()

class MainWindowEventEater(QObject):
    def __init__(self,parent=None):
        QObject.__init__(self,parent)
    def eventFilter(self,obj,event):
        if (event.type()==QEvent.DragEnter):
            if event.mimeData().hasUrls():
                event.accept()   # must accept the dragEnterEvent or else the dropEvent can't occur !!!
            else:
                event.ignore()
        if (event.type() == QEvent.Drop):
            if event.mimeData().hasUrls():   # if file or link is dropped
                url = event.mimeData().urls()[0]   # get first url
                filename=url.toString()
                filename=str(filename)
                filename=filename.split('file:///')[1]
                g.settings['last_dir'] = os.path.dirname(filename)
                add_file(filename)
                event.accept()
            else:
                event.ignore()
        return False # lets the event continue to the edit

mainWindowEventEater = MainWindowEventEater()

if __name__ == '__main__':
    win = QMainWindow()
    widg = QWidget()
    win.setCentralWidget(widg)
    win.setAcceptDrops(True)
    ly = QFormLayout(widg)
    file_list = QListWidget()
    file_list.contextMenuEvent = lambda ev: get_files()
    file_list.itemDoubleClicked.connect(remove_file)
    add_files_button = QPushButton("Add Files")
    add_files_button.pressed.connect(get_files)
    epsilon_spin = pg.SpinBox(value=g.settings['epsilon'])
    min_neighbors_spin = pg.SpinBox(value=g.settings['min_neighbors'], int=True, step=1)
    min_density_spin = pg.SpinBox(value=g.settings['min_density'], int=True, step=1)
    simulateCheck = QCheckBox("Simulate Center Proximities")
    clusterButton = QPushButton("Start Clustering")
    clusterButton.pressed.connect(main)

    ly.addRow("Files", file_list)
    ly.addWidget(add_files_button)
    ly.addRow("Epsilon", epsilon_spin)
    ly.addRow("Minimum neighbors to consider a point", min_neighbors_spin)
    ly.addRow("Minimum Cluster Density", min_density_spin)
    ly.addWidget(simulateCheck)
    ly.addWidget(clusterButton)

    win.installEventFilter(mainWindowEventEater)
    win.setWindowTitle("DBScan Clustering")
    win.closeEvent = close_and_save
    win.show()
    QApplication.instance().exec_()