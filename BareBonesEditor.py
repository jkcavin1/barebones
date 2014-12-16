__author__ = 'Lab Hatter'

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor

from barebones.barebones import BareBones
from barebones.BBConstants import COLLISIONMASKS


"""
An inheritable editor
"""

class BareBonesEditor(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.editor = BareBones()



if __name__ == "__main__":
    app = BareBonesEditor()
    app.run()