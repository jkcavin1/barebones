__author__ = 'Lab Hatter'

from commands.undoHandler import UndoHandler

undoHandler = None
currCoordSysNP = None
currPickleFileName = ""
#currPickleFilePath = ""
#recoverFromPickleLst = []  # TODO move this into the pickle file
bareBonesObj = None

def initialise(bbObj, curr_coordNP):
    assert(curr_coordNP is not None)
    global undoHandler
    undoHandler = UndoHandler()
    global currCoordSysNP
    currCoordSysNP = curr_coordNP
    global bareBonesObj
    bareBonesObj = bbObj