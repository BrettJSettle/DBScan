"""
@author: Brett Settle
@Department: UCI Neurobiology and Behavioral Science
@Lab: Parker Lab
@Date: August 6, 2015
"""
from os import path, makedirs
from basics import *
from glob import glob

def toFiles(fileName, clusters, centers, areas, distances, closests):
    # r = [borders, centers, distances, closests, areasConvex, areasGrid, areasConcave]
    nonoise = [i for cluster in clusters for i in cluster] # data without noise list for output

    directory = path.abspath(path.join(path.dirname( __file__), path.basename(fileName))) # open the directory
    if not path.exists(directory):
        makedirs(directory)

    with open(directory + "/DBResults.txt", "w") as outFile:
        outFile.write("X\tY\tNo Noise X\tNo Noise Y\tCenters X\tCenters Y\n")
        for i in range(len(nonoise)):
            line = "%s\t%s\n" % (getPoint(i, nonoise), getPoint(i, centers))
            outFile.write(line)

    with open(directory + "/cluster_info.txt", "w") as outFile:
        outFile.write("Cluster\tDensity\tArea Concave\n")
        for i in range(len(clusters)):
            outFile.write("%d\t%d\t%f\n" %(i + 1, len(clusters[i]), areas[i]))

    with open(directory + "/Distances.txt", "w") as outFile:
        outFile.write("Distance\n")
        for dist in distances:
            outFile.write(str(dist) + "\n")

    with open(directory + "/Closests.txt", "w") as outFile:
        outFile.write("Closest Distance\n")
        for clo in closests:
            outFile.write(str(clo) + "\n")

def getPoint(index, runThrough):
    if index >= len(runThrough):
        return "\t"
    else:
        return asStr(runThrough[index])

def asStr(pnt):
    return "%s\t%s" % (pnt[0], pnt[1])
