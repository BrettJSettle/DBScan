"""
@author: Brett Settle
@Department: UCI Neurobiology and Behavioral Science
@Lab: Parker Lab
@Date: August 6, 2015
"""
import os,sys,inspect
from PyQt4.QtGui import *
from PyQt4.QtCore import *
app = QApplication(sys.argv)
import global_vars as g
g.settings = g.Settings()
import pyqtgraph as pg
from FileReader import file_to_array
#from Analyzer import *
#from DataHandler import *
#from RandDists import gen

def dbscan():
    newLayout = QGridLayout()
    win.setLayout(newLayout)

def add_file(filename):
    for i in range(file_list.count()):
        if os.path.samefile(file_list.item(i).text(), filename):
            return
    file_list.addItem(QListWidgetItem(filename))

def get_files():
    files = QFileDialog.getOpenFileNames(win, caption="Select point files to cluster", directory=g.settings['last_dir'])
    if len(files) == 0:
        return
    g.settings['last_dir'] = os.path.dirname(files[0])
    for i in files:
        add_file(i)

win = QWidget()
win.setAcceptDrops(True)
ly = QFormLayout(win)
file_list = QListWidget()
add_files_button = QPushButton("Add Files")
add_files_button.pressed.connect(get_files)
epsilon_spin = pg.SpinBox(value=g.settings['epsilon'])
min_neighbors_spin = pg.SpinBox(value=g.settings['min_neighbors'])
min_density_spin = pg.SpinBox(value=g.settings['min_density'])
clusterButton = QPushButton("Start Clustering")
clusterButton.pressed.connect(dbscan)

ly.addRow("Files", file_list)
ly.addWidget(add_files_button)
ly.addRow("Epsilon", epsilon_spin)
ly.addRow("Minimum Neighbors to consider point", min_neighbors_spin)
ly.addRow("Minimum Cluster Density", min_density_spin)
ly.addWidget(clusterButton)

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
                  #This fails on windows symbolic links.  http://stackoverflow.com/questions/15258506/os-path-islink-on-windows-with-python
                event.accept()
            else:
                event.ignore()
        return False # lets the event continue to the edit
mainWindowEventEater = MainWindowEventEater()
win.installEventFilter(mainWindowEventEater)

win.show()
'''
def prepare(d):
    global op
    fs = d['Files'].split(', ')
    if len(fs) == 0:
        print("No files found")
        sys.exit(0)

    for f in fs:
        name = os.path.basename(f)[:-4]
        data = fileToArray(f)
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
    directory = getDirectory("Choose/create a folder to store the ", initial=name)
    if directory == "":
        return
    toFiles(directory, clusters, centers, areas, distances, closests)
    print("Simulating results...")
    pnts = len(clusters)
    x, y = np.transpose(points)
    gen(pnts, [min(x), max(x)], [min(y), max(y)], directory)
    print("Done")

ops = [{'key': 'Select files', 'type': 'action', 'value' : lambda : None},\
{'key': 'Files', 'value':''}, {'key': 'Epsilon', 'value': 30}, {'key': 'minP', 'name': 'Minimum Cluster Size', 'value': 10}]
op = ParameterWidget('DBScan Options', ops, doneButton=True)
op.parameters.param('Select files').sigActivated.connect(lambda : op.parameters.__setitem__('Files', \
    ', '.join(getFilenames(title='Select text files to perform Density Scan', filter='Text Files (*.txt)'))))
op.done.connect(prepare)
op.show()
'''
if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    QApplication.instance().exec_()
    QApplication.closeAllWindows()
