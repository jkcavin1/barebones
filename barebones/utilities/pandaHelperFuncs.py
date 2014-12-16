__author__ = 'Lab Hatter'
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Mat4, Mat3, Vec3, Point3, NodePath, NodePathCollection
"""
TODO: add functions for initializing Panda objects such as
loading Models, Actors
setting up GUI objects (later make 2D editor)
setting up/(maybe)switching input i.e. keystrokes
setting up collision nodes w/ solids
including tasks???
"""

def PanditorDisableMouseFunc():
    base.disableMouse()


def PanditorEnableMouseFunc():
    mat = Mat4(camera.getMat())
    mat.invertInPlace()
    base.mouseInterfaceNode.setMat(mat)
    base.enableMouse()


def TranslateWrtNPFunc( wrtNP, translatingNP, directVec, velocity, time, normalize=True):
    if normalize is True:
        directVec.normalize()

    toPoint = directVec * velocity * time

    translatingNP.setPos(wrtNP, toPoint.getX(), toPoint.getY(), toPoint.getZ())


def TraverserLevelFirst(startNP, funcOpOnNP, *args, **kwargs):
    npCollection = NodePathCollection()
    currNP = startNP
    npCollection.addPath(currNP)
    notEmtpy = True
    while notEmtpy:
            if currNP.countNumDescendants() == 0:
                # no descendants to add to the stack
                pass
            else:
                # add the currNP's children to stack
                currChildColl = currNP.getChildren()
                npCollection.extend(currChildColl)

            if npCollection.getNumPaths() > 0:
                # operate on the current node
                funcOpOnNP(currNP, *args, **kwargs)
                npCollection.removePath(currNP)
                # get currNP's sister
                if npCollection.getNumPaths() > 0:
                    currNP = npCollection.getPath(0)
            else:
                notEmtpy = False  # scene has been walked in level order
                currNP = None



"""
if __name__ == '__main__':
    class HelperTester(ShowBase):
        def __init__(self):
            ShowBase.__init__(self)
            PanditorDisableMouseFunc()
            # Load the environment model.
            self.environ = self.loader.loadModel("models/environment")
            # tag recommended by https://www.panda3d.org/manual/index.php/Clicking_on_3d_objects
            #self.environ.setTag( 'Blah', '1' )
            # TODO: See chessboard for collision testing
            # Reparent the model to render.
            self.environ.reparentTo(self.render)
            # Apply scale and position transforms on the model.
            self.environ.setScale(0.25, 0.25, 0.25)
            self.environ.setPos(-8, 42, 0)

        def EnableMouse(self):
            PanditorEnableMouseFunc()

    tst = HelperTester()
    tst.run()
"""
