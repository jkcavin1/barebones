__author__ = 'Lab Hatter'

# from panda3d.core import Filename
# import sys
# import os
# absPath = os.path.abspath(sys.path[0])
# # #print absPath
# absPath = Filename.fromOsSpecific(absPath).getFullpath()
# # #print absPath
# sys.path.append(absPath)
# # sys.path.append(absPath + '/levitor')
# # sys.path.append(absPath + '/utilities')

# from panda3d.core import NodePath, PandaNode, GeomNode, BitMask32
# from direct.showbase.ShowBase import ShowBase
from panda3d.core import PandaNode, NodePath
from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotify import DirectNotify
import BBVariables as BBGlobalVars
from levitor.levitor import Levitor
from TwoDeeGui import TwoDeeGui



class BareBones(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        BBGlobalVars.initialise(self, render)  # set render as current coordinate system (NOT CURRENTLY IMPLEMENTED)
        #super(DirectObject, self).__init__() # I'd like to do this init
        self.notify = DirectNotify()
        self.notify.newCategory('bareBonesErr')
        self.bareBonesNP = render.attachNewNode('bareBonesNode')
        self.levitorNP = self.bareBonesNP.attachNewNode('levitorNode')
        self.levitor = Levitor(self.bareBonesNP, self.levitorNP)
        self.bbDummyNP = None  # should always be None, save for during file ops


        self.twoDGui = TwoDeeGui()


    def prepareForSave(self):
        self.bbDummyNP = NodePath(PandaNode("bbDummyNP"))
        self.bareBonesNP.reparentTo(self.bbDummyNP)


    def recoverFromSave(self):
        self.bareBonesNP.reparentTo(render)
        self.bbDummyNP.removeNode()
        self.bbDummyNP = None


    def prepareForLoad(self):
        self.prepareForSave()


    def recoverFromLoad(self):
        assert(render is not None)
        global BBGlobalVars
        BBGlobalVars.initialise(self, render)  # set render as current coord sys
        self.levitor.grabber.grabModelNP.hide()  # HACK REMOVE this line barebones shouldn't know about grabber
        self.recoverFromSave()
        # for i in range(0, len(BBGlobalVars.recoverFromPickleLst)):
        #     BBGlobalVars.recoverFromPickleLst[i].recoverFromPickle()