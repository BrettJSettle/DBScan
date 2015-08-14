"""
@author: Brett Settle
@Department: UCI Neurobiology and Behavioral Science
@Lab: Parker Lab
@Date: August 6, 2015
"""

from random import uniform
from basics import *
import math

def gen(pnts, rangeX, rangeY, directory):
    distances = []
    cents = [(uniform(rangeX[0], rangeX[1]), uniform(rangeY[0], rangeY[1])) for i in range(pnts)]
    closests = []
    for i in range(len(cents)):
        distances.extend(getDistances(cents[i], cents[i + 1:]))
        closests.append(getClosest(cents[i], cents))

    with open(directory + "/RandDistances.txt", "w") as outFile:
        outFile.write("Distance\tClosest Dist\n")
        for dist in distances:
            outFile.write(str(dist) + "\n")

    with open(directory + "/RandClosests.txt", "w") as outFile:
        outFile.write("Closest Distance\n")
        for clo in closests:
            outFile.write(str(clo) + "\n")
