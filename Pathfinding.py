__author__ = 'Lab Hatter'

# from panda3d.core import ConfigVariablString
import exceptions
from direct.actor.Actor import Actor
from BareBonesEditor import BareBonesEditor
from panda3d.core import GeomVertexFormat, GeomVertexData, GeomLines
from panda3d.core import Geom, GeomNode, GeomTriangles, GeomVertexWriter, ModelNode, NodePath
from panda3d.core import Vec3, Vec4, Point3
from panda3d.core import Triangulator, RenderModeAttrib
from Queue import PriorityQueue


def getCenterOfPointsXY(points):
    n = len(points)
    x = 0
    y = 0
    z = 0
    for i in points:
        x = x + i.x
        y = y + i.y
        z = z + i.z

    return Vec3(x/n, y/n, z/n)


def getTrueAngleXY(ptA, ptB):
    aNorm = Vec3(ptA.x, ptA.y, ptA.z)
    bNorm = Vec3(ptB.x, ptB.y, ptB.z)
    aNorm.normalize()
    bNorm.normalize()
    ang = aNorm.angleDeg(aNorm - bNorm)

    if aNorm.x - bNorm.x < 0 > aNorm.y - bNorm.y:  # 3rd quadrant
        ang += 180
    elif aNorm.x - bNorm.x < 0 < aNorm.y - bNorm.y:  # 2nd quadrant
        ang = 180 - ang
    elif aNorm.x - bNorm.x > 0 < aNorm.y - bNorm.y:  # 4th quadrant
        ang = 360 - ang

    return ang


def makeCcw(verts):
    import exceptions
    raise exceptions.StandardError("ccw doesn't work")
    cntr = getCenterOfPointsXY(verts)
    if cntr == Vec3(0, 0, 0):
        cntr += .01

    q = PriorityQueue()
    for i in verts:
        ang = getTrueAngleXY(cntr, i)
        q.put((ang, i))

    # print cntr, "makeCcw" ###############  PRINT
    verts = []
    while q.qsize() != 0:
        n = q.get_nowait()
        # print n, getTrueAngleXY(cntr, n[1]), "makeCcw"
        verts.append(n[1])

    return verts


def makeTriMesh( verts, holeVerts=[[]]):
    pointmap = (lambda x, y: (x, y, 0))
    if not hasattr(holeVerts[0], '__iter__'):
        holeVerts = [holeVerts]

    frmt = GeomVertexFormat.getV3n3cp()
    vdata = GeomVertexData('triangle', frmt, Geom.UHDynamic)

    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')

    bl = Vec4(0, 0, 0, 255)
    gr = Vec4(256/2 - 1, 256/2 - 1, 256/2 - 1, 255)

    trilator = Triangulator()
    zUp = Vec3(0, 0, 1)

    for i in verts:
        trilator.addPolygonVertex(trilator.addVertex(i.x, i.y))
        vertex.addData3f(pointmap(i.x, i.y))
        normal.addData3f(zUp)
        color.addData4f(bl)

    for w in holeVerts:
        trilator.beginHole()
        # print "new hole"
        for j in w:
            # print(j)  # ###################### PRINT #######################
            trilator.addHoleVertex(trilator.addVertex(j.x, j.y))
            vertex.addData3f(pointmap(j.x, j.y))
            normal.addData3f(zUp)
            color.addData4f(gr)

    trilator.triangulate()

    prim = GeomTriangles(Geom.UHStatic)
    for n in xrange(trilator.getNumTriangles()):
        prim.addVertices(trilator.getTriangleV0(n),
                         trilator.getTriangleV1(n),
                         trilator.getTriangleV2(n))
    prim.closePrimitive()
    geom = Geom(vdata)
    geom.addPrimitive(prim)
    node = GeomNode('gnode')
    node.addGeom(geom)

    # print trilator.isLeftWinding()

    return tuple((node, trilator))

def drawInds(adjLst):
    from direct.gui.OnscreenText import OnscreenText
    for i in range(0, len(adjLst)):
        center = getCenterOfPointsXY(adjLst[i].tri)
        dummy = render.attachNewNode(str(i))
        txt = OnscreenText(text=str(i), pos=center, scale=1)
        txt.reparentTo(dummy)
        dummy.setP(dummy.getP() - 90)

def makeLines(adjLst):
    frmt = GeomVertexFormat.getV3n3cp()
    vdata = GeomVertexData('triangle', frmt, Geom.UHDynamic)

    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')

    prim = GeomLines(Geom.UHStatic)
    for i in range(0, len(adjLst)):
        center = getCenterOfPointsXY(adjLst[i].tri)
        vertex.addData3f(center)  # adjLst[i].pt1, i.y, i.z)
        normal.addData3f(Point3(0, 0, 1))
        color.addData4f(256/2, 0, 0, 1)
        inds = [i]
        from direct.gui.OnscreenText import OnscreenText
        dummy = render.attachNewNode('dummy')
        txt = OnscreenText(text=str(i), pos=center, scale=1)
        txt.reparentTo(dummy)
        dummy.setP(dummy.getP() - 90)
        if adjLst[i].n12 is not None:
            inds.append(adjLst[i].n12)
        if adjLst[i].n23 is not None:
            inds.append(adjLst[i].n23)
        if adjLst[i].n13 is not None:
            inds.append(adjLst[i].n13)
        print inds  # ######################################
        if len(inds) < 3:
            inds.append(i)
            # j = 0
            # while len(inds) < 3:
            #     j += 1
            #     for k in range(j, len(inds)-1):
            #         if inds[k] != inds[0]:
            #             inds.insert(k+1, i)  # .addVertices() takes 3-5 args. So add redundant verts. Hoping beginning = end of line.

        prim.addVertices(*inds)
    #for n in xrange(trilator.getNumTriangles()):

    prim.closePrimitive()
    geom = Geom(vdata)
    geom.addPrimitive(prim)
    node = GeomNode('lineNode')
    node.addGeom(geom)
    return node


def getSharedVerts(triA, triB):
    """Returns the edge that B shares w/ A i.e. If B lies on A's 12 edge, returns '12', otherwise returns '' or '1'"""
    if triA is None or triB is None:
        return ''

    vertsA = triA.getVerts()
    vertsB = triB.getVerts()
    # two matching vertices means their neighbours
    found = ''
    for i in range(0, len(vertsA)):
        if vertsA[i] is not None and vertsA[i] == vertsB[0] or vertsA[i] == vertsB[1] or vertsA[i] == vertsB[2]:
            found = str(i + 1)
            break
    # none match
    if found == '':
        return found

    # now that we found one lets see if there's a second match
    if i + 1 <= len(vertsA):
        for j in range(i + 1, len(vertsA)):
            if vertsA[j] is not None:  # and j != i:
                if vertsA[j] == vertsB[0] or vertsA[j] == vertsB[1] or vertsA[j] == vertsB[2]:
                    found += str(j + 1)
                    # print vertsA[i], vertsB[j]
                    return found

    return found


class Triangle(object):
    def __init__(self, pt1, pt2, pt3):
        self.tri = tuple((pt1, pt2, pt3))
        # print "triangle = ", self.tri
        self.pt1 = pt1
        self.pt2 = pt2
        self.pt3 = pt3

    def getTri(self):
        return tuple((self.pt1, self.pt2, self.pt3))

    def getPt1(self):
        return self.tri[0]

    def getPt2(self):
        return self.tri[1]

    def getPt3(self):
        return self.tri[2]

    def getEdge12(self):
        return tuple((self.pt1, self.pt2))

    def getEdge23(self):
        return tuple((self.pt2, self.pt3))

    def getEdge13(self):
        return tuple((self.pt1, self.pt2))

    def getVerts(self):
        return [self.pt1, self.pt2, self.pt3]

    # def __str__(self):
    #     return "dmflksdj;fklj"
    #
    # def __repr__(self):
    #     sr = "Tri: < " + self.pt1 + ", " + self.pt2 + ", " + self.pt3 + " >"
    #     return "dmflksdj;fklj"


class AdjLstElement(Triangle):
    def __init__(self, triOrPts, slfInd, n12Ind=None, n23Ind=None, n13Ind=None):
        """If points are past they must be in a tuple-like object"""
        if isinstance(triOrPts, tuple):
            Triangle.__init__(self, triOrPts[0], triOrPts[1], triOrPts[2])
        elif isinstance(triOrPts, Triangle):
            Triangle.__init__(self, triOrPts.pt1, triOrPts.pt2, triOrPts.pt3)
        self.selfInd = slfInd
        self.n12 = n12Ind
        self.n23 = n23Ind
        self.n13 = n13Ind
        self.par = None
        self.g = 0
        self.f = 0

    def getNaybs(self):
        n = []
        if self.n12 is not None:
            n.append(self.n12)
        if self.n23 is not None:
            n.append(self.n23)
        if self.n13 is not None:
            n.append(self.n13)
        return n


    # def __str__(self):
    #     return self.__repr__()

    def __repr__(self):
        sr = "tri: < " + str(self.getTri()) +\
            " >   < slf: " + str(self.selfInd) +\
            " n12: " + str(self.n12) +\
            " n23: " + str(self.n23) +\
            " n13: " + str(self.n13) +\
            " >   < par: " + str(self.par) +\
            ", g: " + str(self.g) +\
            ", f: " + str(self.f) + " >"

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
                    nayb = getSharedVerts(self.adjLst[j], self.adjLst[k])
                    if nayb == '12':
                        self.adjLst[j].n12 = k
                    if nayb == '23':
                        self.adjLst[j].n23 = k
                    if nayb == '13':
                        self.adjLst[j].n13 = k

                    # if len(nayb) != 2: ##################### DEBUG
                    #     vertsJ = self.adjLst[j].getVerts()
                    #     vertsK = self.adjLst[k].getVerts()
                    #     print " nayb ", nayb, vertsJ[0] == vertsK[0], vertsJ[1] == vertsK[1], vertsJ[2] == vertsK[2]
                    #     print "j: ", self.adjLst[j], "\nk: ", self.adjLst[k]


        # debug crap #################################
        # for w in range(0, len(self.adjLst)):
            #print "adj", self.adjLst[w].getTri(), self.adjLst[w].n12, self.adjLst[w].n23, self.adjLst[w].n13
            # if self.adjLst[w].n12 is not None:
            #     l = self.adjLst[w].n12
            #     # print "triNayb", self.adjLst[l].tri

    def at(self, ind):
        return self.adjLst[ind]



class Pathfinding(BareBonesEditor):
    def __init__(self):
        BareBonesEditor.__init__(self)
        camera.setPos( 15.0, 15.0, 15.0)
        camera.lookAt(0)

        # from barebones.utilities import ConvexHull

        hole1 = []
        hole1.append(Vec3(-2, -2, 0))
        # hole1.append(Vec3(-1, -2, 0))
        # hole1.append(Vec3(-1, .5, 0))
        # hole1.append(Vec3(1, .5, 0))
        # hole1.append(Vec3(1, -2, 0))
        hole1.append(Vec3(2, -2, 0))
        hole1.append(Vec3(2, 2, 0))
        hole1.append(Vec3(-2, 2, 0))


        hole2 = []
        hole2.append(Vec3(3, 3, 0))
        hole2.append(Vec3(4, 3, 0))
        hole2.append(Vec3(4, 4, 0))
        hole2.append(Vec3(3, 4, 0))

        holes = []
        holes.append(hole1)
        holes.append(hole2)

        map = []
        map.append(Vec3(-10, -10, 0))
        map.append(Vec3(10, -10, 0))
        map.append(Vec3(10, 10, 0))
        map.append(Vec3(-10, 10, 0))

        mesh_trilator = makeTriMesh(map, holes)
        adjLst = AdjacencyList(mesh_trilator[1])
        for i in adjLst.adjLst:
            print i
        drawInds(adjLst.adjLst)  # Lines are broken but it does put text on each triangle
        modelNP = render.attachNewNode(mesh_trilator[0])
        modelNP.setRenderMode(RenderModeAttrib.MWireframe, .5, 0)






if __name__ == '__main__':
    # import sys
    # sys.stdout = None

    # a way to redirect print ##############################
    # import sys
    # import os
    #
    # def thwErr(stuff):
    #     exceptions.StandardError()
    # sys.stdout = open(  os.devnull, "w")
    #
    #
    # thwErr('')
    #
    # sys.stdout = sys.__stdout__
    ######################################################
    app = Pathfinding()
    app.run()
