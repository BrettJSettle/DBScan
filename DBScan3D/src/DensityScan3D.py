"""
@author: Brett Settle
@Department: UCI Neurobiology and Behavioral Science
@Lab: Parker Lab
@Date: August 6, 2015
"""
import os,sys
from BioDocks import *
from DBAnalysis import *
from cluster import *
from sklearn.cluster import DBSCAN
from scipy.spatial import ConvexHull
from PyQt4.QtGui import *
import pyqtgraph.opengl as gl

app = QApplication([])

win = DockWindow(addMenu=False)
win.resize(1700, 900)
plot3DWidget = Plot3DWidget()
Data = {}
current_cluster = 0
min_size = 4

def set_min_size(v):
	global min_size, Data, current_cluster
	if 'all_clusters' not in Data:
		return
	min_size = v
	Data['clusters'] = [c for c in Data['all_clusters'] if len(c.points) >= min_size]
	current_cluster = 0
	Data['cluster_count'] = len(Data['clusters'])
	update()

def get_all_pts():
	pts = []
	for item in plot3DWidget.items:
		if isinstance(item, gl.GLScatterPlotItem) and item.visible():
			if np.size(pts) == 0:
				pts = item.pos
			else:
				pts = np.vstack((pts, item.pos))
	return pts

def analyze(d):
	global Data
	Data.update(d)
	print('Clustering Data...')
	scanner = DBSCAN(eps = Data['Epsilon'], min_samples=Data['Minimum Cluster Size'])
	db = scanner.fit(Data['points'])
	clusterWidget.update({'Minimum Cluster Size': Data['Minimum Cluster Size']})

	Data['all_clusters'] = []

	# Number of clusters in labels, ignoring noise if present.
	Data['cluster_count'] = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
	for i in range(Data['cluster_count']):
		Data['all_clusters'].append(Cluster(np.array([Data['points'][j] for j in np.where(db.labels_ == i)[0]])))
	print('Found %d clusters' % Data['cluster_count'])
	set_min_size(Data['Minimum Cluster Size'])
	win.addWidget(clusterWidget, name='Buttons', size=(1, 6), renamable=False, where=('right', plot3DDock))

def removeCluster(i):
	global current_cluster
	Data['all_clusters'].remove(Data['clusters'][i])
	del Data['clusters'][i]
	Data['cluster_count'] -= 1
	current_cluster -= 1
	update()

def update(d = {}):
	global Data
	Data.update(d)
	cl = Data['clusters'][current_cluster]
	data = [(current_cluster,), (Data['cluster_count'],), (len(cl),), (str(cl.center),), (str(cl.volume),)]
	tableWidget.setData(data)
	tableWidget.setVerticalHeaderLabels(['Cluster #', 'Cluster count', 'Points in Cluster', 'Center', 'Volume'])
	ch = ConvexHull(cl.points)
	md = gl.MeshData(vertexes=ch.points, faces=ch.simplices)
	if 'cluster' in Data:
		Data['cluster'].setMeshData(meshdata=md)
	else:
		Data['cluster'] = gl.GLMeshItem(meshdata=md)
		plot3DWidget.addItem(Data['cluster'], name='Cluster')
	plot3DWidget.moveTo(pos = cl.center)

def get_analysis_params():
	Data['points'] = get_all_pts()
	_, _, zs = zip(*Data['points'])
	Data.update({'Epsilon': abs(np.max(zs) - np.min(zs)), 'Minimum Cluster Size': 4})
	win.p = ParameterWidget('Options for Density Based Scan', [{'key': name, "value" : float(Data[name])} for name in \
		('Epsilon', 'Minimum Cluster Size')], about = \
'''    The parameters below are used to run a density based scan on \n\
the 3d scattered data. \n\n\
  * Epsilon - maximum distance between two points to place them \n\
          in the same cluster. \n\
  * Minimum Cluster Size - minimum coordinate count to be \n\
          considered a cluster.''', doneButton=True)
	win.p.done.connect(analyze)
	win.p.show()

def export_clusters():
	fname = getSaveFilename(caption="Saving Cluster points to file", initial_dir='clusters.txt')
	with open(fname, 'w') as outFile:
		print('Saving Clusters...')
		for i in Data['clusters']:
			np.savetxt(outFile, i.points, fmt='%.4f')
			outFile.write('\n')
		print('Clusters saved successfully')

def moveCluster(d):
	global current_cluster
	current_cluster += d
	current_cluster %= Data['cluster_count']
	update()

def plotAverages():
	centers = []
	for cl in Data['clusters']:
		centers.append(cl.center)

	plot3DWidget.addItem(gl.GLScatterPlotItem(pos=np.array(centers), color=(1, 0, 0, 1), size=20), name='Centers')


fileMenu = win.menuBar().addMenu('&File')
fileMenu.addAction(QAction('&Import Data', fileMenu, triggered = plot3DWidget.load_file))
fileMenu.addAction(QAction('&Close', fileMenu, triggered = win.close))
clusterMenu = win.menuBar().addMenu('Cluster Options')
clusterMenu.addAction(QAction('Cluster all plotted', clusterMenu, triggered=get_analysis_params))
clusterMenu.addAction(QAction('Export Clusters', clusterMenu, triggered=export_clusters))
clusterMenu.addAction(QAction('Plot Centers', clusterMenu, triggered=plotAverages))
plot3DDock = win.addWidget(plot3DWidget, size=(10, 6))
clusterWidget = OptionsWidget('Cluster Options', \
	[{'key': 'Next Cluster', 'action': lambda : moveCluster(1)}, \
	{'key': 'Previous Cluster', 'action': lambda : moveCluster(-1)}, \
	{'key': 'Remove Cluster', 'action': lambda : removeCluster(current_cluster)}, \
	{'key': 'Minimum Cluster Size', 'value': 4, 'minimum': 4, 'step':1, 'int': True}], shape=(2, 4))
clusterWidget.valueChanged.connect(lambda f: set_min_size(f['Minimum Cluster Size']))
tableWidget = DataWidget()
clusterWidget.addWidget(tableWidget, (2, 0, 5, 4))
win.addWidget(QLabel("Plot 3D Widget Controls\n\tArrows or Left click and drag to rotate camera\n\tMiddle click and drag to pan\n\
\tScroll mouse wheel to zoom\n\tRight Click for plotted item options"), where=['bottom', plot3DDock], size=(1, 1))

win.show()
sys.exit(app.exec_())
