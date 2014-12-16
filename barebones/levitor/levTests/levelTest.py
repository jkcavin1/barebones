__author__ = 'Lab Hatter'

from direct.showbase.ShowBase import ShowBase
from barebones.levitor.levitor import Levitor


class BonesLevel(object):
    """ A class containing all of the level specific data
            level name
            file paths terrain, scene (with file names???) (TODO: match models to nodes)
            inhabitant states (TODO: (grabber works as is) match characters with nodes)
            list of entry points
    """
    def __init__(self):
        pass

class LevitorLevelMemberDev(Levitor):
    """ a standing for levitor BonesLevel will be a member of Levitor
        only one level can be edited at a time thus Levitor's level will be only level member of Levitor
    """
    def __init__(self):
        Levitor.__init__(self, render, render, render)
        self.level = BonesLevel()


class LevelTestSB(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.levitor = LevitorLevelMemberDev()


test = LevelTestSB()
test.run()