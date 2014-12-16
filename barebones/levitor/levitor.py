__author__ = 'Lab Hatter'

from symbol import decorator

# from panda3d.core import NodePath, Loader
# from direct.showbase.ShowBase import ShowBase
from direct.showbase import DirectObject
from direct.directnotify.DirectNotify import DirectNotify
import barebones.BBVariables as BBGlobalVars
from Grabber import Grabber


class Levitor(DirectObject.DirectObject):
    def __init__(self, panditNP, levitNP):
        """ Main level editor class which runs the level editor
        """
        #DirectObject().__init__(self)
        super(Levitor, self).__init__()
        self.notify = DirectNotify().newCategory('levitorErr')
        self.panditorNP = panditNP
        self.levitorNP = levitNP
        self.grabber = Grabber(levitNP)




# TODO: NEXT wrap the loader funcs
"""
@decorator
def ModelLoaderDecorator(loaderFunc):
    def decoratedFunc(*args, **kwargs):
        retVal = loaderFunc(*args, **kwargs)
        retVal.appendTag('levitorGrabbable')
"""