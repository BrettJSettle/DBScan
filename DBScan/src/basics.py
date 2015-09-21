"""
@author: Brett Settle
@Department: UCI Neurobiology and Behavioral Science
@Lab: Parker Lab
@Date: August 6, 2015
"""
from collections import namedtuple
from math import sqrt, acos
Result = namedtuple("Result", "borders, centers, distances, closests, areasConvex, areasGrid, areasConcave")
from sklearn.cluster import DBSCAN
import numpy as np

def scan(data, epsi, minP):
    labels = DBSCAN(eps=epsi, min_samples=minP).fit_predict(data)
    print('%d Clusters found' % max(labels))
    clusters = []
    for i in range(max(labels) + 1):
        clust = []
        for p in np.where(labels == i)[0]:
           clust.append(data[p])
        clusters.append(clust)
    epsi = epsi
    minP = minP
    return clusters

def distance(p1, p2):
    '''simple distance formula'''
    return np.linalg.norm(np.subtract(p1, p2))

def getDistances(p1, ps):
    '''yields distances between all center points'''
    return [distance(p1, p2) for p2 in ps if not (p1[0] == p2[0] and p1[1] == p2[1])]

def getClosest(center, centers):
    return min(getDistances(center, centers))
