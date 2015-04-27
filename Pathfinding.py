__author__ = 'Lab Hatter'

# from panda3d.core import ConfigVariablString
import exceptions
# from panda3d.core import GeomVertexFormat, GeomVertexData, GeomLines
# from panda3d.core import Geom, GeomNode, GeomTriangles, GeomVertexWriter, ModelNode, NodePath
from panda3d.core import Vec3, Vec4, Point3
from panda3d.core import RenderModeAttrib, LineSegs
from BareBonesEditor import BareBonesEditor
import math
from PolygonUtils.AdjacencyList import AdjacencyList, makeTriMesh
from PolygonUtils.PolygonUtils import getCenterOfPoint3s
from PolygonUtils.PolygonUtils import getNearestPointOnLine, isPointInWedge
from TriangulationAStar import TriangulationAStar
from TriangulationAStarR import TriangulationAStarR
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

        # aStar = TriangulationAStar(aLst.adjLst, Point3(-11, -11, 0), Point3(11, 11, 0))aLst.adjLst[11].getCenter()
        aStar = TriangulationAStarR(aLst.adjLst, Point3(-11, 11, 0), aLst.adjLst[17].getCenter(), radius=.55)
        path = aStar.AStar()
        print "\n\nEND PATH\n", path
        # https://www.panda3d.org/manual/index.php?title=Putting_your_new_geometry_in_the_scene_graph&diff=prev&oldid=6303
        linesegs = LineSegs("lines")
        linesegs.setColor(0, 0, 1, 1)
        linesegs.setThickness(5)
        for p in path:
            linesegs.drawTo(p)
        node = linesegs.create(False)
        nodePath = render.attachNewNode(node)
        nodePath.setZ(.15)


        # tests
        # pt = Point3(6.01, -12.0, 0)
        # p1 = Point3(3, -12, 0)
        # p2 = Point3(3, -6, 0)
        # p3 = Point3(6, -12, 0)
        # print isPointInWedge(pt, [p1, p2], [p1, p3])
        # nearest point on line test
        # line = [p1, p2]
        # nearest = getNearestPointOnLine(pt, line, True)
        # linesegs2 = LineSegs("lines2")
        # linesegs2.setColor(0, 1, 1, 1)
        # linesegs2.setThickness(5)
        # linesegs2.drawTo(p1)
        # linesegs2.drawTo(nearest)
        # linesegs2.setThickness(2)
        # linesegs2.drawTo(p2)
        # node2 = linesegs2.create(False)
        # nodePath = render.attachNewNode(node2)
        # nodePath.setZ(.25)
        # print nearest



if __name__ == '__main__':
    app = Pathfinding()
    app.run()
