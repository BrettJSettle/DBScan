import pyqtgraph as pg
from PyQt4.QtCore import Qt

from pyqtgraph import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl


class PointWidget(pg.PlotWidget):
	def __init__(self, points):
		pg.PlotWidget.__init__(self)
		self.setAspectLocked(True)
		self.setDownsampling(auto=True)
		self.setClipToView(True)
		x, y = points.transpose()
		self.pointPlot = pg.ScatterPlotItem(pos=points, size=2, pen=QtGui.QPen(Qt.green), brush = QtGui.QBrush(Qt.green), symbol='o', pxMode=True, name='Scatter')
		self.addItem(self.pointPlot)