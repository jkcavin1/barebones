__author__ = 'Lab Hatter'

# from panda3d.core import ConfigVariablString
import exceptions
# from panda3d.core import GeomVertexFormat, GeomVertexData, GeomLines
# from panda3d.core import Geom, GeomNode, GeomTriangles, GeomVertexWriter, ModelNode, NodePath
from panda3d.core import Vec3, Vec4, Point3
from panda3d.core import RenderModeAttrib
from BareBonesEditor import BareBonesEditor
import math
from PolygonUtils.AdjacencyList import AdjacencyList
from PolygonUtils.PolygonUtils import getCenterOfPoint3s, makeTriMesh
from TriangulationAStar import TriangulationAStar
from CcwShapes import HorseShoeCentered, SquareOffCenter, SquareMap10x10, TheirMap


def drawInds(adjLst):
    from direct.gui.OnscreenText import OnscreenText
    indNP = render.attachNewNode('indsgroup')
    for i in range(0, len(adjLst)):
        center = getCenterOfPoint3s(adjLst[i].tri)
        dummy = indNP.attachNewNode(str(i))
        txt = OnscreenText(text=str(i), pos=center, scale=1)
        txt.reparentTo(dummy)
        dummy.setP(dummy.getP() - 90)

    return indNP

# def makeLines(adjLst):
#     frmt = GeomVertexFormat.getV3n3cp()
#     vdata = GeomVertexData('triangle', frmt, Geom.UHDynamic)
#
#     vertex = GeomVertexWriter(vdata, 'vertex')
#     normal = GeomVertexWriter(vdata, 'normal')
#     color = GeomVertexWriter(vdata, 'color')
#
#     prim = GeomLines(Geom.UHStatic)
#     for i in range(0, len(adjLst)):
#         center = getCenterOfPoint3s(adjLst[i].tri)
#         vertex.addData3f(center)  # adjLst[i].pt1, i.y, i.z)
#         normal.addData3f(Point3(0, 0, 1))
#         color.addData4f(256/2, 0, 0, 1)
#         inds = [i]
#         from direct.gui.OnscreenText import OnscreenText
#         dummy = render.attachNewNode('dummy')
#         txt = OnscreenText(text=str(i), pos=center, scale=1)
#         txt.reparentTo(dummy)
#         dummy.setP(dummy.getP() - 90)
#         if adjLst[i].n12 is not None:
#             inds.append(adjLst[i].n12)
#         if adjLst[i].n23 is not None:
#             inds.append(adjLst[i].n23)
#         if adjLst[i].n13 is not None:
#             inds.append(adjLst[i].n13)
#         print inds  # ######################################
#         if len(inds) < 3:
#             inds.append(i)
#             # j = 0
#             # while len(inds) < 3:
#             #     j += 1
#             #     for k in range(j, len(inds)-1):
#             #         if inds[k] != inds[0]:
#             #             inds.insert(k+1, i)  # .addVertices() takes 3-5 args. So add redundant verts. Hoping beginning = end of line.
#
#         prim.addVertices(*inds)
#     #for n in xrange(trilator.getNumTriangles()):
#
#     prim.closePrimitive()
#     geom = Geom(vdata)
#     geom.addPrimitive(prim)
#     node = GeomNode('lineNode')
#     node.addGeom(geom)
#     return node# makeLines not working

class Pathfinding(BareBonesEditor):
    def __init__(self):
        BareBonesEditor.__init__(self)
        camera.setPos( 0.0, 0.0, 50.0)
        camera.lookAt(0)

        # hole1 = HorseShoeCentered()
        # hole2 = SquareOffCenter()
        # holes = []
        # holes.append(hole1)
        # holes.append(hole2)
        #
        # map10 = SquareMap10x10()
        # mapWholes = []
        # mapWholes.append(map10)
        # mapWholes.append(holes)
        # for i in mapWholes:
        #     print "mapWholes", i
        #
        # mesh_trilator = makeTriMesh(mapWholes[0], mapWholes[1])  # , holes) ############
        mapThrs = TheirMap()
        # for i in mapThrs:
        #     print "mapThrs", i
        mesh_trilator = makeTriMesh(mapThrs[0], mapThrs[1])  # , holes) ###########

        aLst = AdjacencyList(mesh_trilator[1])
        # for i in aLst.aLst:
        #     print i
        indsNP = drawInds(aLst.adjLst)  # put text on each triangle
        indsNP.setPos(0, 0, .2)
        indsNP.setColor(0, 1, 1, 1)
        mapNP = render.attachNewNode(mesh_trilator[0])
        wireNP = render.attachNewNode('wire')
        wireNP.setPos(0, 0, .1)
        wireNP.setColor(1, 0, 0, 1)
        wireNP.setRenderMode(RenderModeAttrib.MWireframe, .5, 0)
        mapNP.instanceTo(wireNP)

        # aStar = TriangulationAStar(aLst.adjLst, Point3(-11, -11, 0), Point3(11, 11, 0))
        aStar = TriangulationAStar(aLst.adjLst, aLst.adjLst[23].getCenter(), aLst.adjLst[18].getCenter())
        path = aStar.AStar()
        # lst = [7, 18, 19, 20]
        # for i in path:  #range(0, len(path)):
        #     #if i.selfInd in lst:
        #     print "path i", i # path[i]

        # for j in pts:
        #     print "prs ", j






if __name__ == '__main__':
    app = Pathfinding()
    app.run()
