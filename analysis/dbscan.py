from PyQt4.QtGui import *
import pyqtgraph as pg

class AnalysisDialog():
	def __init__(self):
		self.items = []
		self.buttonRow = QHBoxLayout()
		self.buttonRow.addWidget(self.backButton)
		self.buttonRow.addSpacing()
		self.buttonRow.addWidget(self.submitButton)

	@classmethod
	def gui(self):
		self.dialog = QDialog()
		layout = QFormLayout()
		self.dialog.setLayout(layout)
		for item in items:
			if type(item) in (list, tuple):
				self.addRow(*item)
			else:
				self.addRow(item)
		self.dialog.addRow(self.buttonRow)
		self.dialog.show()

class DBScan(AnalysisDialog):
	def __init__(self):
		AnalysisDialog.__init__(self)
		self.items.append(('Epsilon', pg.SpinBox(value=g.settings['epsilon'])))
		self.items.append(('Minimum Neighbors per point', pg.SpinBox(value=g.settings['min_neighbors'], int=True, step=1)))
		self.items.append(("Minimum Cluster Density", pg.SpinBox(value=g.settings['min_density'], int=True, step=1)))
		self.items.append(QCheckBox("Simulate Center Proximities"))

	def __call__(self, epsilon, min_neighbors, min_density):
		pass
