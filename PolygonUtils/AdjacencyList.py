__author__ = 'Lab Hatter'

# from panda3d.core import Triangulator
from panda3d.core import Point3
from math import sqrt, pow
from PolygonUtils import getDistance
from Triangle import Triangle, getEdgeStr, getCenterOfPoint3s


def copyAdjLstElement(adjLstEl):
    cpy = AdjLstElement(adjLstEl.tri, adjLstEl.selfInd, adjLstEl.n12, adjLstEl.n23, adjLstEl.n13)
    cpy.par = adjLstEl.par
    cpy.g = adjLstEl.g
    cpy.f = adjLstEl.f
    return cpy


class AdjLstElement(Triangle):
    def __init__(self, triOrPts, slfInd, n12Ind=None, n23Ind=None, n13Ind=None):
        """If points are past they must be in a tuple-like object"""
        if isinstance(triOrPts, Triangle):
            Triangle.__init__(self, triOrPts.pt1, triOrPts.pt2, triOrPts.pt3)
        else:
            Triangle.__init__(self, triOrPts[0], triOrPts[1], triOrPts[2])

        self.selfInd = slfInd
        self.n12 = n12Ind
        self.n23 = n23Ind
        self.n13 = n13Ind
        self.par = None
        self.g = 100000
        self.f = 100000

    def getNaybs(self):
        n = []
        if self.n12 is not None:
            n.append(self.n12)
        if self.n23 is not None:
            n.append(self.n23)
        if self.n13 is not None:
            n.append(self.n13)
        return n

    def getDistanceToCentersOrPoint(self, other):
        if isinstance(other, tuple((AdjLstElement, Triangle))):
            pt1 = self.getCenter()
            pt2 = other.getCenter()
        else:
            pt1 = self.getCenter()
            pt2 = other

        return getDistance(pt1, pt2)

    def getNearestPointTo(self, pt):
        minInd = 0
        minDist = getDistance(self.tri[0], pt)
        for i in range(0, len(pt)):
            dist = getDistance(self.tri[i], pt)
            if dist < minDist:
                minDist = dist
                minInd = i

        return self.tri[minInd]

    def getSharedPoints(self, other):
        pts = []
        found = False
        for pt in self.tri:
            if pt in other.tri:
                found = True
                pts.append(pt)
        if not found:
            raise Exception("Wat?? %i\n%i", self.selfInd, other.selfInd)
        return pts

    def isConstrained(self, pt):
        """Returns true if the point is on an edge with no neighbour"""
        if pt not in self.tri:
            raise Exception("isConstrained: Point must be in this triangle." +
                            self.__repr__() + " pt " + str(pt))

        e12 = self.tri[:-1]
        e23 = self.tri[1:]
        e13 = [self.tri[0], self.tri[2]]
        if pt in e12 and self.n12 is None:
            return True
        elif pt in e23 and self.n23 is None:
            return True
        elif pt in e13 and self.n13 is None:
            return True
        else:
            #print "false: pt", pt, "self", self, "  naybs ", self.n12, self.n23, self.n13
            return False

    def getOppositePoints(self, pt):
        pts = []
        for p in self.tri:
            if p != pt:
                pts.append(p)
        return pts


    def __eq__(self, other):
        return self.selfInd == other.selfInd


    def __ne__(self, other):
        return self.selfInd != other.selfInd


    def __repr__(self):
        sr = "tri: < " + str(self.getTri())  +\
             " >   < slf: " + str(self.selfInd) +\
            " n12: " + str(self.n12) +\
            " n23: " + str(self.n23) +\
            " n13: " + str(self.n13) +\
            " >   < par: " + str(self.par) #+\
            # ", g: " + str(self.g) +\
            # ", f: " + str(self.f) + " >"

        return sr


class AdjacencyList(object):
    def __init__(self, triangulator):
        triLst = []
        self.adjLst = []
        # get the full list of triangles because we can't search a partial list
        for i in range(0, triangulator.getNumTriangles()):
            v0 = triangulator.getVertex(triangulator.getTriangleV0(i))
            v1 = triangulator.getVertex(triangulator.getTriangleV1(i))
            v2 = triangulator.getVertex(triangulator.getTriangleV2(i))
            self.adjLst.append(AdjLstElement(Triangle(Point3(v0.x, v0.y, 0),
                                                      Point3(v1.x, v1.y, 0),
                                                      Point3(v2.x, v2.y, 0)), i))

        # adjLst in the form [(triangle, n12, n23, n13)] i.e. n12 is the triInd across verts 1 & 2
        # find the neighbours
        for j in range(0, len(self.adjLst)):
            for k in range(0, len(self.adjLst)):
                if j != k:
                    nayb = getEdgeStr(self.adjLst[j], self.adjLst[k])
                    if nayb == '12':
                        self.adjLst[j].n12 = k
                    if nayb == '23':
                        self.adjLst[j].n23 = k
                    if nayb == '13':
                        self.adjLst[j].n13 = k

    def at(self, ind):
        return self.adjLst[ind]

    def getNaybsAt(self, ind):
        return self.adjLst[ind].getNaybs()


if __name__ == '__main__':
    app = AdjacencyList()