__author__ = 'Lab Hatter'
# LINK to keywords
# https://www.panda3d.org/manual/index.php/DirectGUI

# LINK to coordinate system
# https://www.panda3d.org/manual/index.php/Positioning_DirectGUI_Elements

from direct.gui.DirectButton import DirectButton

# command - Function
# extraArgs - [Extra Arguments]
# commandButtons - LMB, MMB, or RMB
# rolloverSound - AudioSound instance
# clickSound - AudioSound instance
# pressEffect - <0 or 1>                (Whether or not the button sinks in when clicked)
# state - DGG.NORMAL or DGG.DISABLED
class BBButton(DirectButton):
    def __init__(self, text, pos, parent=None, **kwargs):
        kwargs['text'] = text
        kwargs['pressEffect'] = 1  # Button appears to press when clicked
        kwargs['pos'] = pos
        kwargs['scale'] = .1
        kwargs['pad'] = (.5, .5)
        DirectButton.__init__(self, parent, **kwargs)
        self.initialiseoptions(BBButton)  # needed for subclassing DirectGui
