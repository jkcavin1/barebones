__author__ = 'Lab Hatter'

##-------------  panda3d core imports
from panda3d.core import Filename, CollisionTraverser, CollisionHandlerQueue, CollisionNode, GeomNode, PlaneNode, CollisionRay
from panda3d.core import Point3, Point4, Vec3, Mat4, Plane
from panda3d.core import TransparencyAttrib, CullFaceAttrib, BitMask32, Filename

##-------------- Panda direct imports
from direct.showbase.ShowBase import ShowBase, ConfigVariableString, NodePath
from direct.showbase.PythonUtil import Enum
from direct.showbase.MessengerGlobal import messenger
from direct.task.TaskManagerGlobal import taskMgr
from direct.directnotify.DirectNotify import DirectNotify

import inspect, ntpath  ## this gives the current modules directory via inspect.stack()[i][j]
#print inspect.stack()[0][1]

##-------------- barebones imports

from barebones.commands.commandAssign import UndoCommandOneFuncCall
from barebones.utilities.pandaHelperFuncs import PanditorDisableMouseFunc, PanditorEnableMouseFunc, TranslateWrtNPFunc
import barebones.BBVariables as BBGlobalVars
from barebones.BBConstants import COLLISIONMASKS

# links--
# https://www.panda3d.org/manual/index.php/Clicking_on_3D_Objects ****
# https://www.panda3d.org/manual/index.php/Tasks
# https://www.panda3d.org/manual/index.php/Collision_Traversers
# https://www.panda3d.org/manual/index.php/Collision_Handlers
# https://www.panda3d.org/manual/index.php/Collision_Solids
# http://www.panda3d.org/forums/viewtopic.php?t=10494 ****




class Grabber(object):
    def __init__( self, levitNP):
        """ A widget to position, rotate, and scale Panda 3D Models and Actors
            * handleM1 decides what to do with a mouse1 click
            -- object selection by calling handleSelection when the grabModel is inactive (hidden)
            -- object manipulation by calling handleManipulationSetup (sets the stage for and launches the dragTask)

            isHidden() when nothing is selected
            isDragging means not running collision checks for selection setup and LMB is pressed

            call handleM1 from another class to push control up
            in the program hierarchy (remove inner class calls)
        """
        # TODO remove selection functionality from grabber and put it in a selector class
        self.levitorNP = levitNP  # TODO remove this and use barebonesNP
        self.selected = None
        self.initialize()

    def initialize(self):
        """Reset everything except LevitorNP and selected, also called inside __init__"""
        self.notify = DirectNotify().newCategory('grabberErr')
        self.currPlaneColNorm = Vec3(0.0)
        self.isCameraControlOn = False
        self.isDragging = False
        self.isMultiselect = False
        self.grabScaleFactor = .075
        self.currTransformDir = Point3(0.0)
        self.interFrameMousePosition = Point3(0.0)
        self.init3DemVal = Point3(0.0)
        # initCommVal holds the value before a command operation has taken place
        self.initialCommandTrgVal = None
        # To load the grabber model, this climbs up the absolute path to /barebones/ to gain access to the model folder
        self.grabModelNP = loader.loadModel(Filename.fromOsSpecific(
                                            ntpath.split( ntpath.split(inspect.stack()[0][1])[0] )[0])
                                            + '/EditorModels/widget')
        self.grabModelNP.setPos(0.0, 0.0, 0.0)
        self.grabModelNP.setBin("fixed", 40)
        self.grabModelNP.setDepthTest(False)
        self.grabModelNP.setDepthWrite(False)
        self.transformOpEnum = Enum('rot, scale, trans')
        self.currTransformOperation = None
        # TODO For readability, use this enum in the nested if/else as was the original intent.
        self.grabInd = Enum('xRot, yRot, zRot, xScaler, yScaler, zScaler, xTrans, yTrans, zTrans, xyTrans, xzTrans, zyTrans, grabCore')
        grbrNodLst = [self.grabModelNP.find("**/XRotator;+h-s-i"),       # 0
                       self.grabModelNP.find("**/YRotator;+h-s-i"),      # 1
                       self.grabModelNP.find("**/ZRotator;+h-s-i"),      # 2 end rotate
                       self.grabModelNP.find("**/XScaler;+h-s-i"),       # 3
                       self.grabModelNP.find("**/YScaler;+h-s-i"),       # 4
                       self.grabModelNP.find("**/ZScaler;+h-s-i"),       # 5 end scale
                       self.grabModelNP.find("**/XTranslator;+h-s-i"),   # 6
                       self.grabModelNP.find("**/YTranslator;+h-s-i"),   # 7
                       self.grabModelNP.find("**/ZTranslator;+h-s-i"),   # 8 end translate / end single dir operations
                       self.grabModelNP.find("**/XYTranslator;+h-s-i"),  # 9
                       self.grabModelNP.find("**/XZTranslator;+h-s-i"),  # 10
                       self.grabModelNP.find("**/ZYTranslator;+h-s-i"),  # 11 end bi-directional operations
                       self.grabModelNP.find("**/WidgetCore;+h-s-i")]    # 12
        #Mat4.yToZUpMat()  # change coordinate to z up
        grbrNodLst[12].getParent().setHprScale(0, 0, 0, 1, 1, -1)
        self.grabModelNP.setPythonTag('grabberRoot', grbrNodLst)
        self.grabModelNP.reparentTo(BBGlobalVars.bareBonesObj.levitorNP)
        self.grabModelNP.hide()
        #self.grabIntoBitMask = COLLISIONMASKS
        self.grabModelNP.setCollideMask(COLLISIONMASKS['default'])
        self.grabModelNP.setPythonTag('grabber', self)

        ##############################################################################
        # This whole section is the basics for setting up mouse selection
        # --The mouse events are added in the events section (next)

        # Create the collision node for the picker ray to add traverser as a 'from' collider
        self.grabberColNode = CollisionNode('grabberMouseRay')
        # Set the collision bitmask
        # TODO: define collision bitmask (let user define thiers? likely not)
        self.defaultBitMask = GeomNode.getDefaultCollideMask()
        self.grabberColNode.setFromCollideMask(self.defaultBitMask)
        self.grabberRayColNP = camera.attachNewNode(self.grabberColNode)
        # Create the grabberRay and add it to the picker CollisionNode
        self.grabberRay = CollisionRay(0.0, 0.0, 0.0,
                                       0.0, 1.0, 0.0)
        self.grabberRayNP = self.grabberColNode.addSolid(self.grabberRay)
        # create a collision queue for the traverser
        self.colHandlerQueue = CollisionHandlerQueue()
        # Create collision traverser
        self.colTraverser = CollisionTraverser('grabberTraverser')
        # Set the collision traverser's 'fromObj' and handler
        # e.g. trav.addCollider( fromObj, handler )
        self.colTraverser.addCollider(self.grabberRayColNP, self.colHandlerQueue)


        ############################################################
        # setup event handling with the messenger
        # URGENT remove all of this messenger code throughout Grabber, especially the camera control
        # disable the mouse when the ~ is pressed (w/o shift)
        self.disableCamera()                            # disable camera control by the mouse
        messenger.accept('`', self, self.enableCamera)  # enable camera control when the ~ key is pressed w/o shift
        messenger.accept('`-up', self, self.disableCamera)  # disable camera control when the ~ key is released

        # handle mouse selection/deselection & manipulating the scene
        messenger.accept('mouse1', self, self.handleM1, persistent=1)  # deselect in event handler

        taskMgr.add(self.scaleGrabber, 'scaleGrabber')
        # ////////////////////////////////////////////////////////////////////
        # comment out: good for debug info
        #taskMgr.add(self.watchMouseColl, name='grabberDebug')
        #this is only good for seeing types and hierarchy
        #self.grabModelNP.ls()
        #render.ls()
        # self.frames = 0  #remove
        # self.axis = loader.loadModel("zup-axis")
        # self.axis.reparentTo(self.grabModelNP)
        # self.axis.setScale(.15)
        # self.axis.setPos(0.0)
        # self.grabModelNP.append( 'newAttrib', self)
        # setattr( self.grabModelNP, 'newAttrib', self)


    def prepareForPickle(self):
        self.colTraverser = None     # Traversers are not picklable
        self.defaultBitMask = None   # BitMasks "..."
        # self.grabIntoBitMask = None  # "..."
        self.colHandlerQueue = None  # CollisonHandlerQueue "..."
        self.grabModelNP.removeNode()
        self.grabModelNP = None
        taskMgr.remove('scaleGrabber')


    def recoverFromPickle(self):
        self.initialize()
        if self.selected is not None:
            self.grabModelNP.setPos(render, self.selected.getPos(render))
            self.grabModelNP.show()
        print "grabber sel ", self.selected, " isHidden() ", self.grabModelNP.isHidden(), '\n'
        taskMgr.add(self.scaleGrabber, 'scaleGrabber')

    #### May use to gain control over pickling.
    # def __repr__(self): # for pickling purposes
    #     if self.colTraverser:
    #         self.colTraverser = None
    #
    #     dictrepr = dict.__repr__(self.__dict__)
    #     dictrepr = '%r(%r)' % (type(self).__name__, dictrepr)
    #     print dictrepr  # REMOVE
    #     return dictrepr


    def watchMouseColl(self, task):
        """ This exists for debugging purposes to perpetually watch mouse collisions.
        """
        # TODO make this highlight objects under the mouse for predictable object selection/grabber operations
        self.colTraverser.showCollisions(render)
        if base.mouseWatcherNode.hasMouse() and False == self.isCameraControlOn:
            # This gives the screen coordinates of the mouse.
            mPos = base.mouseWatcherNode.getMouse()
            # This makes the ray's origin the camera and makes the ray point
            # to the screen coordinates of the mouse.
            self.grabberRay.setFromLens(base.camNode, mPos.getX(), mPos.getY())
            # traverses the graph for collisions
            self.colTraverser.traverse(render)
        return task.cont


    def scaleGrabber(self, task):
        if self.grabModelNP.isHidden():
            return task.cont
        coreLst = self.grabModelNP.getPythonTag('grabberRoot')
        camPos = self.grabModelNP.getRelativePoint(self.grabModelNP, camera.getPos())

        if camPos.z >= 0:        # 1-4
            if camPos.x > 0.0 <= camPos.y:    # quad 1
                coreLst[12].getParent().setScale( 1, 1, -1)

            elif camPos.x < 0.0 <= camPos.y:  # quad 2
                coreLst[12].getParent().setScale( -1, 1, -1)

            elif camPos.x < 0.0 >= camPos.y:  # quad 3
                coreLst[12].getParent().setScale( -1, -1, -1)

            elif camPos.x > 0.0 >= camPos.y:  # quad 4
                coreLst[12].getParent().setScale( 1, -1, -1)

            else:
                self.notify.warning("if-else default, scaleGrabber cam.z > 0")

        else:      # 5-8
            if camPos.x > 0.0 <= camPos.y:    # quad 5
                coreLst[12].getParent().setScale( 1, 1, 1)

            elif camPos.x < 0.0 <= camPos.y:  # quad 6
                coreLst[12].getParent().setScale( -1, 1, 1)

            elif camPos.x < 0.0 >= camPos.y:  # quad 7
                coreLst[12].getParent().setScale( -1, -1, 1)

            elif camPos.x > 0.0 >= camPos.y:  # quad 8
                coreLst[12].getParent().setScale( 1, -1, 1)

            else:
                self.notify.warning("if-else default, scaleGrabber cam.z z < 0")


        distToCam = (camera.getPos() - render.getRelativePoint(BBGlobalVars.currCoordSysNP, self.grabModelNP.getPos())).length()
        self.grabModelNP.setScale(self.grabScaleFactor * distToCam,
                                  self.grabScaleFactor * distToCam,
                                  self.grabScaleFactor * distToCam)
        # keep the position identical to the selection
        # for when outside objects like undo/redo move selected
        self.grabModelNP.setPos(render, self.selected.getPos(render))
        return task.cont

    # TODO find a way to move camera control to a proper camera handler, perhaps move these to a global
    def enableCamera(self):
        self.isCameraControlOn = True
        PanditorEnableMouseFunc()

    def disableCamera(self):
        self.isCameraControlOn = False
        PanditorDisableMouseFunc()


    def handleM3(self):
        """Deselect the selected object."""
        if not self.grabModelNP.isHidden() and not self.isCameraControlOn:
            # if the grab model is in the scene and the camera is not in control
            if base.mouseWatcherNode.hasMouse() and not self.isDragging:
                # we're ignoring accidental mouse3 clicks while dragging here with not isDragging
                self.selected = None              # empty the selected, will be turned back on once something's selected
                messenger.ignore('mouse3', self)  # turn the deselect event off
                self.grabModelNP.hide()           # hide the grab model and set it back to render's pos
                self.grabModelNP.setPos(0.0)


    def handleM1Up(self):
        """Stop dragging the selected object."""
        taskMgr.remove('mouse1Dragging')
        self.isDragging = False
        self.currTransformOperation = None  # NOTE other references have been added, but no other object references them
        # record the mouse1 operation
        BBGlobalVars.undoHandler.record(self.selected, UndoCommandOneFuncCall([self.initialCommandTrgVal],
                                                                    self.selected.setMat, self.selected.getMat(render)))
        messenger.ignore('mouse1-up', self)


    def handleM1(self):
        """Decides how to handle a mouse1 click."""
        if self.isCameraControlOn:
            return

        if base.mouseWatcherNode.hasMouse():
            # give the grabber first chance
            if self.grabModelNP.isHidden():
                # no collisions w/ grabber or nothing selected
                # handle selection with scene objects
                self.handleSelection()

            elif not self.isDragging:
                # The grabber is in place but not dragging. Get ready to drag.
                self.handleManipulationSetup()  # it'll call self.handleSelection() if no collision w/ grabber
                # TODO (if warranted) make self.handleManipulationSetup() return false if no col w/ grabber, call selection here instead


    def handleManipulationSetup(self):
        """Sets up all the attributes needed for the mouse dragging task."""
        # This makes the ray's origin the camera and makes the ray point
        # to the screen coordinates of the mouse.
        if self.isDragging:
            return
        camVec = self.grabModelNP.getRelativeVector(self.grabModelNP, camera.getPos())
        mPos = base.mouseWatcherNode.getMouse()
        self.grabberRay.setFromLens(base.camNode, mPos.getX(), mPos.getY())
        self.colTraverser.traverse(self.grabModelNP)  # look for collisions on the grabber

        if not self.isCameraControlOn and self.colHandlerQueue.getNumEntries() > 0 and not self.grabModelNP.isHidden():
            # see if collided with the grabber if not handle re or multi selection
            self.colHandlerQueue.sortEntries()
            grabberObj = self.colHandlerQueue.getEntry(0).getIntoNodePath()
            grabberLst = self.grabModelNP.getPythonTag('grabberRoot')  # see __init__

            # the index gives the operations rot < 3 scale < 6 trans < 9 trans2D < 12
            # mod index gives axis 0 == x, 1 == y, 2 == z
            ind = -1
            for i in range(0, 13):
                if grabberObj == grabberLst[i]:
                    ind = i
                    grabberObj = grabberLst[i]
            # ensure we are not picking ourselves, ahem, the grabber
            assert(not self.grabModelNP.isAncestorOf(self.selected))
            mPos3D = Point3(0.0)
            xVec = Vec3(1, 0, 0)
            yVec = Vec3(0, 1, 0)
            zVec = Vec3(0, 0, 1)
            # TODO: ??? break this up into translate rotate and scale function to make it readable
            if -1 < ind < 3:             # rotate
                if ind % 3 == 0:    # x
                    self.initializeManipVars(Point3(1.0, 0.0, 0.0), self.transformOpEnum.rot,
                                             Point3(mPos.getX(), mPos.getY(), 0.0))
                elif ind % 3 == 1:  # y
                    self.initializeManipVars(Point3(0.0, 1.0, 0.0), self.transformOpEnum.rot,
                                             Point3(mPos.getX(), mPos.getY(), 0.0))
                else:               # z
                    self.initializeManipVars(Point3(0.0, 0.0, 1.0), self.transformOpEnum.rot,
                                             Point3(mPos.getX(), mPos.getY(), 0.0))

            elif ind < 6:                 # scale
                if ind % 3 == 0:    # x
                    self.initializeManipVars(Point3(1.0, 0.0, 0.0), self.transformOpEnum.scale,
                                             Point3(mPos.getX(), mPos.getY(), 0.0))
                elif ind % 3 == 1:  # y
                    # self.currTransformDir = Point3( 0.0, 1.0, 0.0)
                    self.initializeManipVars(Point3(0.0, 1.0, 0.0), self.transformOpEnum.scale,
                                             Point3(mPos.getX(), mPos.getY(), 0.0))
                else:               # z
                    # self.currTransformDir = Point3( 0.0, 0.0, 1.0)
                    self.initializeManipVars(Point3(0.0, 0.0, 1.0), self.transformOpEnum.scale,
                                             Point3(mPos.getX(), mPos.getY(), 0.0))

            elif ind < 9:                 # translate
                if ind % 3 == 0:    # x
                    # if the camera's too flat to the collision plane bad things happen
                    if camVec.angleDeg( zVec) < 89.0 and self.getMousePlaneIntersect(mPos3D, zVec):
                        self.initializeManipVars(Point3(1.0, 0.0, 0.0), self.transformOpEnum.trans, mPos3D, zVec)

                    elif self.getMousePlaneIntersect(mPos3D, yVec):
                        self.initializeManipVars(Point3(1.0, 0.0, 0.0), self.transformOpEnum.trans, mPos3D, yVec)

                elif ind % 3 == 1:  # y
                    if camVec.angleDeg( zVec) < 89.0 and self.getMousePlaneIntersect(mPos3D, zVec):
                        self.initializeManipVars(Point3(0.0, 1.0, 0.0), self.transformOpEnum.trans, mPos3D, zVec)

                    elif self.getMousePlaneIntersect(mPos3D, xVec):
                        self.initializeManipVars(Point3(0.0, 1.0, 0.0), self.transformOpEnum.trans, mPos3D, xVec)

                else:               # z
                    if camVec.angleDeg( yVec) < 89.0 and self.getMousePlaneIntersect(mPos3D, yVec):
                        self.initializeManipVars(Point3(0.0, 0.0, 1.0), self.transformOpEnum.trans, mPos3D, yVec)

                    elif self.getMousePlaneIntersect(mPos3D, xVec):
                        self.initializeManipVars(Point3(0.0, 0.0, 1.0), self.transformOpEnum.trans, mPos3D, xVec)

            elif ind < 12:            # translate 2D
                if ind % 3 == 0:    # xy
                    if self.getMousePlaneIntersect(mPos3D, zVec):
                        self.initializeManipVars(Point3(1.0, 1.0, 0.0), self.transformOpEnum.trans, mPos3D, zVec)

                elif ind % 3 == 1:  # xz
                    if self.getMousePlaneIntersect(mPos3D, yVec):
                        self.initializeManipVars(Point3(1.0, 0.0, 1.0), self.transformOpEnum.trans, mPos3D, yVec)
                else:               # zy
                    if self.getMousePlaneIntersect(mPos3D, xVec):
                        self.initializeManipVars(Point3(0.0, 1.0, 1.0), self.transformOpEnum.trans, mPos3D, xVec)

            elif ind == 12:  # scale in three directions
                self.initializeManipVars(Point3(1.0, 1.0, 1.0), self.transformOpEnum.scale,
                                         Point3(mPos.getX(), mPos.getY(), 0.0))

            else:
                self.notify.warning("Grabber Err: no grabber collision when col entries > 0 AND grabber not hidden")

            # Save initial value for save/undo.
            # The end result of the operation is sent to the undo handler on mouse up event.
            if self.selected:
                self.initialCommandTrgVal = self.selected.getMat(render)
        else:
            # no collisions w/ grabber or nothing selected
            # handle reselection or multi-selection (not yet implemented) with other scene obj
            self.handleSelection()


    def handleSelection(self):
        if self.isDragging:
            return

        # First check that the mouse is not outside the screen.
        if base.mouseWatcherNode.hasMouse() and False == self.isCameraControlOn:

            self.grabberColNode.setFromCollideMask(self.defaultBitMask)
            # This gives the screen coordinates of the mouse.
            mPos = base.mouseWatcherNode.getMouse()

            # This makes the ray's origin the camera and makes the ray point
            # to the screen coordinates of the mouse.
            self.colHandlerQueue.clearEntries()
            self.grabberRay.setFromLens(base.camNode, mPos.getX(), mPos.getY())
            self.colTraverser.traverse(render)  # look for collisions

            if self.colHandlerQueue.getNumEntries() > 0:
                self.colHandlerQueue.sortEntries()
                grabbedObj = self.colHandlerQueue.getEntry(0).getIntoNodePath()
                if not grabbedObj.findNetTag('pickable').isEmpty():
                    grabbedObj = grabbedObj.findNetTag('pickable')
                    self.selected = grabbedObj
                    self.grabModelNP.setPos(render,
                                            grabbedObj.getPos(render).x,
                                            grabbedObj.getPos(render).y,
                                            grabbedObj.getPos(render).z)
                    self.grabModelNP.show()
                    messenger.accept('mouse3', self, self.handleM3)

    def handleDragging(self, task):
        """ Does the actual work of manipulating objects,
            once the needed attributes have been setup by handleManipulationSetup().
        """

        if not self.isDragging:
            return task.done
        mPos3D = Point3(0.0)
        #
        # This section handles the actual translating rotating or scale after it's been set up in mouse1SetupManip...()
        # ONLY one operation is preformed per frame
        if self.currTransformOperation == self.transformOpEnum.trans:
            # 1st translation, rotation's section is at next elif
            if self.getMousePlaneIntersect(mPos3D, self.currPlaneColNorm):

                # get the difference between the last mouse and this frames mouse
                selectedNewPos = mPos3D - self.interFrameMousePosition
                # store this frames mouse
                self.interFrameMousePosition = mPos3D
                # add the difference to the selected object's pos
                self.selected.setPos(render, self.selected.getPos(render).x + self.currTransformDir.x * selectedNewPos.x,
                                             self.selected.getPos(render).y + self.currTransformDir.y * selectedNewPos.y,
                                             self.selected.getPos(render).z + self.currTransformDir.z * selectedNewPos.z)

                self.grabModelNP.setPos(render, self.selected.getPos(render))

        elif self.currTransformOperation == self.transformOpEnum.rot:
            # 2nd rotation, followed finally by scaling
            # if operating on the z-axis, use the y (vertical screen coordinates otherwise use x (horizontal)
            mPos = base.mouseWatcherNode.getMouse()
            #rotMag = 0.0
            if self.currTransformDir == Vec3( 0.0, 0.0, 1.0):
                rotMag = (mPos.x - self.interFrameMousePosition.x) * 1000
            else:
                rotMag = (self.interFrameMousePosition.y - mPos.y) * 1000

            initPos = self.selected.getPos()
            initPar = self.selected.getParent()
            self.selected.wrtReparentTo(render)
            self.selected.setMat(self.selected.getMat() * Mat4.rotateMat(rotMag, self.currTransformDir))
            self.selected.wrtReparentTo(initPar)
            self.selected.setPos(initPos)

            self.interFrameMousePosition = Point3(mPos.x, mPos.y, 0.0)

        elif self.currTransformOperation == self.transformOpEnum.scale:
            # 3rd and final is scaling
            mPos = base.mouseWatcherNode.getMouse()
            # TODO: make dragging away from the object larger and to the object smaller (not simply left right up down)
            # td The problem with this MAY come if negative, mirrored, scaling is implemented.

            # if operating on the z-axis, use the y (vertical screen coordinates otherwise use x (horizontal)
            if self.currTransformDir == Point3( 0.0, 0.0, 1.0):
                sclMag = (mPos.y - self.interFrameMousePosition.y) * 5.5
            elif self.currTransformDir == Point3( 0.0, 1.0, 0.0):
                sclMag = (mPos.x - self.interFrameMousePosition.x) * 5.5
            else:
                sclMag = (self.interFrameMousePosition.x - mPos.x) * 5.5

            # This is the line that prevents scaling past the origin. Flipping the faces doesn't seem to work.
            if -0.0001 < sclMag < 0.0001:
                sclMag = 0.000001

            # create a dummy node to parent to and position such that applying scale to it will scale selected properly
            dummy = self.levitorNP.attachNewNode('dummy')
            initScl = dummy.getScale()
            # Don't forget the parent. Selected needs put back in place
            initPar = self.selected.getParent()
            initPos = self.selected.getPos()
            self.selected.wrtReparentTo(dummy)

            dummy.setScale(initScl.x + sclMag * self.currTransformDir.x,
                           initScl.y + sclMag * self.currTransformDir.y,
                           initScl.z + sclMag * self.currTransformDir.z)

            # reset selected's parent then destroy dummy
            self.selected.wrtReparentTo(initPar)
            self.selected.setPos(initPos)
            dummy.removeNode()
            dummy = None

            self.interFrameMousePosition = Point3( mPos.x, mPos.y, 0.0)
        else:
            self.notify.error("Err: Dragging with invalid curTransformOperation enum in handleDragging")

        return task.cont  # ended by handleM1Up(), the mouse1-up event handler


    def initializeManipVars(self, transformDir, transformOp, mPos3D, planeNormVec=None):
        self.currTransformDir = transformDir
        self.currPlaneColNorm = planeNormVec  # set the norm for the collision plane to be used in mouse1Dragging
        self.interFrameMousePosition = mPos3D
        self.currTransformOperation = transformOp
        self.isDragging = True
        taskMgr.add(self.handleDragging, 'mouse1Dragging')
        messenger.accept('mouse1-up', self, self.handleM1Up)


    def getMousePlaneIntersect(self, mPos3Dref, normVec):
        mPos = base.mouseWatcherNode.getMouse()
        plane = Plane(normVec, self.grabModelNP.getPos())
        nearPoint = Point3()
        farPoint = Point3()
        base.camLens.extrude(mPos, nearPoint, farPoint)
        if plane.intersectsLine(mPos3Dref,
            render.getRelativePoint(camera, nearPoint),
            render.getRelativePoint(camera, farPoint)):
            return True
        return False



    def destroy(self):
        raise NotImplementedError('Make sure messenger etc are cleared of refs and the model node is deleted')
        self.grabModelNP.clearPythonTag('grabberRoot')
        self.grabModelNP.clearPythonTag('grabber')
        self.grabModelNP = None
        messenger.ignoreAll(self)



