__author__ = 'Lab Hatter'

from direct.gui.DirectScrolledList import DirectScrolledList, DirectScrolledListItem

# look at the code for DirectScrolledList, add hierarchy to display children properly like a tree view (or look for tree view)
# http://www.panda3d.org/forums/viewtopic.php?t=3474  <<<< EXAMPLE
class GraphViewer(DirectScrolledList):
    def __init__(self, parent=None, **kw):
        DirectScrolledList.__init__(self, parent, **kw)



if __name__ == '__main__':
    app = GraphViewer()