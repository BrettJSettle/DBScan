"""
@author: Brett Settle
@Department: UCI Neurobiology and Behavioral Science
@Lab: Parker Lab
@Date: August 6, 2015
"""
import numpy as np

class Cluster():
	def __init__(self, points):
		self.points = np.array(points)
		self.center = (np.mean(points[:, 0]), np.mean(points[:, 1]), np.mean(points[:, 2]))
		try:
			self.volume = volume(points)
		except:
			self.volume = -1

	def __len__(self):
		return len(self.points)

	def __iter__(self):
		for p in self.points:
			yield p


## next few methods are used to calculate volume
def det(a):
	return a[0][0]*a[1][1]*a[2][2] + a[0][1]*a[1][2]*a[2][0] + a[0][2]*a[1][0]*a[2][1] - a[0][2]*a[1][1]*a[2][0] - a[0][1]*a[1][0]*a[2][2] - a[0][0]*a[1][2]*a[2][1]

#unit normal vector of plane defined by points a, b, and c
def unit_normal(a, b, c):
	x = det([[1,a[1],a[2]],
			 [1,b[1],b[2]],
			 [1,c[1],c[2]]])
	y = det([[a[0],1,a[2]],
			 [b[0],1,b[2]],
			 [c[0],1,c[2]]])
	z = det([[a[0],a[1],1],
			 [b[0],b[1],1],
			 [c[0],c[1],1]])
	magnitude = (x**2 + y**2 + z**2)**.5
	return (x/magnitude, y/magnitude, z/magnitude)

#dot product of vectors a and b
def dot(a, b):
	return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

#cross product of vectors a and b
def cross(a, b):
	x = a[1] * b[2] - a[2] * b[1]
	y = a[2] * b[0] - a[0] * b[2]
	z = a[0] * b[1] - a[1] * b[0]
	return (x, y, z)

#volume of polygon poly
def volume(poly):
	if len(poly) < 3: # not a plane - no volume
		return 0

	total = [0, 0, 0]
	for i in range(len(poly)):
		vi1 = poly[i]
		if i is len(poly)-1:
			vi2 = poly[0]
		else:
			vi2 = poly[i+1]
		prod = cross(vi1, vi2)
		total[0] += prod[0]
		total[1] += prod[1]
		total[2] += prod[2]
	result = dot(total, unit_normal(poly[0], poly[1], poly[2]))
	return abs(result/2)
