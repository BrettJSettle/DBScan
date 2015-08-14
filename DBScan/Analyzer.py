"""
@author: Brett Settle
@Department: UCI Neurobiology and Behavioral Science
@Lab: Parker Lab
@Date: August 6, 2015
"""
from basics import *
from scipy.spatial import Delaunay

def distance(ptA, ptB):
    return np.linalg.norm(np.subtract(ptA, ptB))

def order_walls(walls):
    new_wall = walls.pop(0)
    while walls:
        add = [wall for wall in walls if new_wall[-1] in wall][0]
        walls.remove(add)
        add.remove(new_wall[-1])
        new_wall.extend(add)
    return new_wall

def getTriangleArea(A, B, C):
    return .5 * abs(A[0]*(B[1] - C[1]) + B[0]*(C[1] - A[1]) + C[0]*(A[1] - B[1]))

def concaveArea(points):
    print(len(points))
    if len(points) < 3:
        return 0
    tri = Delaunay(points)
    outerwalls = tri.convex_hull.tolist()
    outerwalls = order_walls(outerwalls)
    verts = tri.vertices.tolist()
    change = False
    i = 0
    while i < len(outerwalls) - 1:
        at = outerwalls[i]
        next = outerwalls[i + 1]
        outer_dist = distance(points[at], points[next])
        inner = None
        for t in verts:
            inners = set(t) ^ {at, next}
            if len(inners) == 1 and len(set(outerwalls) & set(t)) == 2:
                inner = inners.pop()
                break
        if inner != None and outer_dist > distance(points[at], points[inner]):
            outerwalls.insert(i+1, inner)
            change = True
            verts.remove(t)
            i += 1
        i += 1
        if i >= len(outerwalls) - 1 and change:
            change = False
            i = 0
    pts = np.array([points[i] for i in outerwalls])
    return sum(map(lambda vs: getTriangleArea(*[points[i] for i in vs]), verts))


def getCenter(clust):
    '''get center point of cluster'''
    Xtot = sum(map(lambda f: f[0], clust))
    Ytot = sum(map(lambda f: f[1], clust))
    return [Xtot / len(clust), Ytot / len(clust)]
