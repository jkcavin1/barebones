__author__ = 'Lab Hatter'

from direct.actor.Actor import Actor
from BareBonesEditor import BareBonesEditor

class ProtoCode(BareBonesEditor):
    def __init__(self):
        BareBonesEditor.__init__(self)
        camera.setPos( 15.0, 15.0, 15.0)
        camera.lookAt(0)
        # """
        # # Load the environment model.
        # self.environ = self.loader.loadModel("models/environment")
        # # tag recommended by https://www.panda3d.org/manual/index.php/Clicking_on_3d_objects
        # self.environ.setTag( 'pickable', '1' )
        # self.environ.setCollideMask(COLLISIONMASKS['default'])
        # # TODO: See chessboard for collision testing
        # # Reparent the model to render.
        # self.environ.reparentTo(self.render)
        # # Apply scale and position transforms on the model.
        # self.environ.setScale(0.25, 0.25, 0.25)
        # self.environ.setPos(-8, 42, 0)
        # # tag recommended by https://www.panda3d.org/manual/index.php/Clicking_on_3d_objects
        # #self.environ.setTag( 'Blah', '1' )
        # """
        # self.jack = self.loader.loadModel("models/jack")
        # self.jack.setColor( 1.0, 1.0, 1.0)
        #
        # # TODO: See chessboard for collision testing
        # self.dummy = self.render.attachNewNode("dummy")
        # self.dummy.setPos( -1.0, 1.0, -1.0)
        # self.dummy.setHpr( 10.0, 0.0, 0.0)
        # self.dummy.setTag('pickable', '1')
        # print " is dummy empty?", self.dummy.isEmpty()
        # # Reparent the model to render.
        # self.jack.reparentTo(self.dummy)
        # # Apply scale and position transforms on the model
        # self.jack.setScale(1.0, 1.0, 1.0)
        # self.jack.setHpr( -45.0, 0.0, 0.0)
        # self.jack.setPos(0.0, 1.0, 0.0)
        # self.jack.setTag('pickable', '1')
        # #self.jack.getParent().ls()
        # print " jack has tag??", self.jack.hasTag('pickable'), self.jack.findNetTag('pickable')

        # # Add the spinCameraTask procedure to the task manager
        # #self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

        # self.axis = self.loader.loadModel("zup-axis")
        # self.axis.reparentTo(render)
        # self.axis.setScale(1.0)
        # self.axis.setPos(0.0)
        #
        self.ali = Actor("GameModels/Fem.egg", {"Walk": "GameModels/Fem-Walk.egg"})
        #self.ali.setScale( 1)
        self.ali.clearColor()
        self.ali.setPos( 0.0, 0.0, 0.0)
        self.ali.setTag('pickable', '1')
        self.ali.reparentTo(render)
        self.ali.loop("Walk")
        #self.ali.ls()
        #
        # # Load and transform the panda
        # self.pandaActor = Actor("models/panda-model"
        #                         , {"walk": "models/panda-walk4"})
        # self.pandaActor.setScale(0.005, 0.005, 0.005)
        # self.pandaActor.setPos(5.0, 5.0, 0.0)
        # self.pandaActor.reparentTo(self.render)
        # self.pandaActor.setTag('pickable', '2')
        # #print " panda has tag?? child??", self.pandaActor.hasTag('pickable'), self.pandaActor.getChildren()[0].hasTag('pickable')
        # # Loop its animation.
        # self.pandaActor.loop("walk")
        # #self.pandaActor.ls()



if __name__ == '__main__':
    app = ProtoCode()
    app.run()