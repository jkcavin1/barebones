__author__ = 'Lab Hatter'

from direct.actor.Actor import Actor
from BareBonesEditor import BareBonesEditor
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Geom, GeomNode, GeomTriangles, GeomVertexWriter
from panda3d.core import Vec3, Vec4, Point3
from panda3d.core import Triangulator


def makeTriMesh( verts, holeVerts=[]):
    frmt = GeomVertexFormat.getV3n3cp()
    vdata = GeomVertexData('triangle', frmt, Geom.UHDynamic)

    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')


    """
    vertex.addData3f(loL)
    vertex.addData3f(upL)
    vertex.addData3f(loR)
    vertex.addData3f(upR)
    """
    inds = []
    trilator = Triangulator()
    for i in pts:
        ind = trilator.addPolygonVertex( trilator.addVertex(i.x, i.y) )
        inds.append(ind)
    print trilator.getNumVertices()

    trilator.triangulate()

    for j in range(0, trilator.getNumTriangles()):
        print trilator.getTriangleV0(j),\
              trilator.getTriangleV1(j),\
              trilator.getTriangleV2(j)

    print trilator.isLeftWinding()
    zUp = Vec3(0, 0, 1)
    normal.addData3f(zUp)
    normal.addData3f(zUp)
    normal.addData3f(zUp)
    normal.addData3f(zUp)

    bl = Vec4(0, 0, 0, 255)
    gr = Vec4(256/2 - 1, 256/2 - 1, 256/2 - 1, 255)
    color.addData4f(bl)
    color.addData4f(gr)
    color.addData4f(bl)
    color.addData4f(gr)

    tri1 = GeomTriangles(Geom.UHDynamic)
    tri2 = GeomTriangles(Geom.UHDynamic)

    tri1.addVertex(0)
    tri1.addVertex(1)
    tri1.addVertex(3)

    tri2.addConsecutiveVertices(1,3)

    tri1.closePrimitive()
    tri2.closePrimitive()

    square = Geom(vdata)
    square.addPrimitive(tri1)
    square.addPrimitive(tri2)

    sqrNode = GeomNode('square')
    sqrNode.addGeom(square)

    return


class Pathfinding(BareBonesEditor):
    def __init__(self):
        BareBonesEditor.__init__(self)
        camera.setPos( 15.0, 15.0, 15.0)
        camera.lookAt(0)

        loL = Vec3(-2, -2, 0)
        upL = Vec3(-2, 2, 0)
        loR = Vec3(2, -2, 0)
        upR = Vec3(2, 2, 0)
        pts = [upL, loL, loR, upR]

        mesh, trilator = makeTriMesh(pts)

    # def makeNode(self, pointmap=(lambda x, y: (x, y, 0))):
    #         vt = tuple(self.vertices)
    #         t = Triangulator()
    #         fmt = GeomVertexFormat.getV3()
    #         vdata = GeomVertexData('name', fmt, Geom.UHStatic)
    #         vertex = GeomVertexWriter(vdata, 'vertex')
    #         for x, y in vt:
    #             t.addPolygonVertex(t.addVertex(x, y))
    #             vertex.addData3f(pointmap(x, y))
    #         t.triangulate()
    #         prim = GeomTriangles(Geom.UHStatic)
    #         for n in xrange(t.getNumTriangles()):
    #             prim.addVertices(t.getTriangleV0(n),t.getTriangleV1(n),t.getTriangleV2(n))
    #         prim.closePrimitive()
    #         geom = Geom(vdata)
    #         geom.addPrimitive(prim)
    #         node = GeomNode('gnode')
    #         node.addGeom(geom)
    #         return node

        """

        render.attachNewNode(sqrNode)
        """






if __name__ == '__main__':
    app = Pathfinding()
    app.run()
