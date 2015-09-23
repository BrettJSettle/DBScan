"""
@author: Brett Settle
@Department: UCI Neurobiology and Behavioral Science
@Lab: Parker Lab
@Date: August 6, 2015
"""
from basics import *
from BioDocks import getDirectory

def toFiles(directory, clusters, centers, areas, distances, closests):
    # r = [borders, centers, distances, closests, areasConvex, areasGrid, areasConcave]
    nonoise = [i for cluster in clusters for i in cluster] # data without noise list for output

    with open(directory + "/Clusters.txt", "w") as outFile:
        outFile.write("X\tY\n")
        for i, cluster in enumerate(clusters):
            for p in cluster:
                outFile.write("%.3f\t%.3f\n" % (p[0], p[1]))
            if i < len(clusters)-1:
                outFile.write('\n')

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
