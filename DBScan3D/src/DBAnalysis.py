"""
@author: Brett Settle
@Department: UCI Neurobiology and Behavioral Science
@Lab: Parker Lab
@Date: August 6, 2015
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
from collections import defaultdict, namedtuple

Line = namedtuple('Line', 'start location distance')

class DataSet():
	def __init__(self, points, epsilon):
		self.map = defaultdict(list)
		points = sorted(points, key=lambda f: f[0])
		for i, pt in enumerate(points):
			print(i)
			for pt2 in points[i+1:]:
				if abs(pt[0] - pt2[0]) > epsilon:
					continue
				self.map[tuple(pt)].append(Line(pt, pt2, np.linalg.norm(np.subtract(pt, pt2))))

	def within(self, epsilon):
		new_map = {}
		for tup in self.map:
			new_map = [line for line in self.map[tup] if line.distance <= epsilon]
		return new_map

class MapPoints(QThread):
	done = Signal(list)
	def __init__(self, points, epsilon):
		super(MapPoints, self).__init__()
		self.points = points
		self.epsilon = epsilon

	def run(self):
		clusters = []
		ps = range(len(self.points))
		while ps:
			print("%s left" % len(ps))
			cl = {ps[0]}
			to_scan = {ps[0]}
			while to_scan:
				found = set()
				for p in to_scan:
					for p2 in ps:
						if abs(self.points[p][0] - self.points[p2][0]) > self.epsilon:
							continue
						if np.linalg.norm(np.subtract(self.points[p2], self.points[p])) <= self.epsilon and p2 not in (found | to_scan):
							found.add(p2)
				cl |= found
				for p in to_scan:
					ps.remove(p)
				to_scan = found
			if len(cl) > 1:
				clusters.append(cl)
		clusters = [np.array([self.points[i] for i in cl]) for cl in clusters]
		self.done.emit(clusters)
