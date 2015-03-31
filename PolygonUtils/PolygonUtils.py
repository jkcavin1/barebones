__author__ = 'Lab Hatter'

from panda3d.core import GeomVertexFormat, GeomVertexData, GeomLines
from panda3d.core import Geom, GeomNode, GeomTriangles, GeomVertexWriter, ModelNode, NodePath
from panda3d.core import Vec3, Vec4, Point3
from panda3d.core import Triangulator
from math import sqrt, pow
from Queue import PriorityQueue


def getDistance(pt1, pt2):
    return sqrt(pow(pt1.x - pt2.x, 2) + pow(pt1.y - pt2.y, 2) + pow(pt1.z - pt2.z, 2))


def getDistance2d(pt1, pt2):
    return sqrt(pow(pt1.x - pt2.x, 2) + pow(pt1.y - pt2.y, 2))


def makeCcw(verts):
    print "makeCcw only works on convex hulls"
    cntr = getCenterOfPoint3s(verts)
    if cntr == Vec3(0, 0, 0):
        cntr += .01

    q = PriorityQueue()
    for i in verts:
        ang = getTrueAngleXYBetweenPoints(cntr, i)
        q.put((ang, i))

    # print cntr, "makeCcw" ###############  PRINT
    verts = []
    while q.qsize() != 0:
        n = q.get_nowait()
        # print n, getTrueAngleXYBetweenPoints(cntr, n[1]), "makeCcw"
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

    bl = Vec4(50, 50, 50, 255)
    gr = Vec4(256/2 - 1, 256/2 - 1, 256/2 - 1, 255)

    trilator = Triangulator()
    zUp = Vec3(0, 0, 1)

    for i in verts:
        #print "verts", verts
        trilator.addPolygonVertex(trilator.addVertex(i.x, i.y))
        vertex.addData3f(pointmap(i.x, i.y))
        normal.addData3f(zUp)
        color.addData4f(bl)
    #if len(holeVerts) != 1 and holeVerts[0] != []:
    for w in holeVerts:
        trilator.beginHole()
        print "new hole"
        for j in w:
            # print(j)  # ###################### PRINT #######################
            trilator.addHoleVertex(trilator.addVertex(j.x, j.y))
            vertex.addData3f(pointmap(j.x, j.y))
            normal.addData3f(zUp)
            color.addData4f(gr)

    # try:
    trilator.triangulate()
    # except AssertionError:
    #     pass

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


def getCenterOfPoint3s(points):
    n = len(points)
    x = 0
    y = 0
    z = 0
    for i in points:
        x = x + i.x
        y = y + i.y
        z = z + i.z
    return Point3(x/n, y/n, z/n)


def getTrueAngleXYBetweenPoints(ptA, ptB):
    """don't use anywhere new"""
    aNorm = Vec3(ptA.x, ptA.y, ptA.z)
    bNorm = Vec3(ptB.x, ptB.y, ptB.z)
    aNorm.normalize()
    bNorm.normalize()
    ang = aNorm.angleDeg(aNorm - bNorm)
    print "a b norm", aNorm, bNorm, "ang", ang

    if aNorm.x - bNorm.x < 0 > aNorm.y - bNorm.y:  # 3rd quadrant
        ang += 180
    elif aNorm.x - bNorm.x < 0 < aNorm.y - bNorm.y:  # 2nd quadrant
        ang = 180 - ang
    elif aNorm.x - bNorm.x > 0 < aNorm.y - bNorm.y:  # 4th quadrant
        ang = 360 - ang

    return ang


def getAngleXYVecs(vecA, vecB):
    """don't use anywhere new"""
    aNorm = vecA
    bNorm = vecB
    aNorm.normalize()
    bNorm.normalize()
    ang = aNorm.angleDeg(bNorm)
    # print "a b norm", aNorm, bNorm, "ang", ang

    # if aNorm.x - bNorm.x < 0 > aNorm.y - bNorm.y:  # 3rd quadrant
    #     ang += 180
    # elif aNorm.x - bNorm.x < 0 < aNorm.y - bNorm.y:  # 2nd quadrant
    #     ang = 180 - ang
    # elif aNorm.x - bNorm.x > 0 < aNorm.y - bNorm.y:  # 4th quadrant
    #     ang = 360 - ang

    return ang

def getLeftPt(pt, ptPair):
    """Takes the center of two points then returns the left point as viewed from a third point (1st parameter)."""
    midPt = getCenterOfPoint3s(ptPair)
    vecToMid = midPt - pt
    vecToPt1 = ptPair[0] - pt
    # the point on the leftVec has a negative z in its cross product with the middle point
    if vecToPt1.cross(vecToMid).z < 0:
        return ptPair[0]
    else:
        return ptPair[1]

