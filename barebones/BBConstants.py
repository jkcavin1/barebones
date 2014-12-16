__author__ = 'Lab Hatter'
from panda3d.core import BitMask32, GeomNode


COLLISIONMASKS = {'grabber': BitMask32(1<<31), 'default': GeomNode.getDefaultCollideMask()}