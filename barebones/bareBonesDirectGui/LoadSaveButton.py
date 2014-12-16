__author__ = 'Lab Hatter'

from direct.gui.DirectEntry import DirectEntry
import direct.gui.DirectGuiGlobals as DGG
from panda3d.core import Vec3, NodePath
from BBButton import BBButton
import barebones.BBVariables as BBGlobalVars
import pickle


class LoadSaveButton(object):
    def __init__(self):
        self.loadButt = BBButton('Load', Vec3(1.145, 1, 0.851667),
                                 command=self.createLoaderEntryBox,
                                 )
        self.saveButt = BBButton('Save', Vec3(0.796667, 1, 0.853333),
                                 command=self.createSaverEntryBox)

    # MOVE to UI handler
    def createLoaderEntryBox(self):
        # creates a DirectEntry that lives only long enough to save the file
        # Disable mouse response so the user can't create another button
        LoadSaveTextEntry(self.loadButt, isLoader=True)

    def createSaverEntryBox(self):
        # creates a DirectEntry that lives only long enough to load the file
        # Disable mouse response so the user can't create another button
        LoadSaveTextEntry(self.saveButt, isLoader=False)

# KEYWORDS
# initialText	String	    Initial text to load in the field
# entryFont 	Font        object	Font to use for text entry
# width	        Number	    Width of field in screen units
# numLines	    Integer	    Number of lines in the field
# cursorKeys	0 or 1  	True to enable the use of cursor keys (arrow keys)
# obscured  	0 or 1	    True to hide passwords, etc.
# focus     	0 or 1	    Whether or not the field begins with focus (focusInCommand is called if true)
# command   	Function	Function to call when enter is pressed(the text in the field is passed to the function)
# extraArgs 	    [Extra Arguments]	Extra arguments to the function specified in command
# backgroundFocus	0 or 1	If true, field begins with focus but with hidden cursor, and focusInCommand is not called
# focusInCommand	Function	        Function called when the field gains focus
# focusInExtraArgs	[Extra Arguments]	Extra arguments to the function specified in focusInCommand
# focusOutCommand	Function            Function called when the field loses focus
# focusOutExtraArgs	[Extra Arguments]	Extra arguments to the function specified in focusOutCommand
class LoadSaveTextEntry(DirectEntry):
    def __init__(self, originator, isLoader=True, parent=None, **kwargs):
        if isLoader:
            kwargs['command'] = self.loadGraph
        else:
            kwargs['command'] = self.saveGraph

        self.originator = originator

        #kwargs['width'] = 10
        kwargs['scale'] = .1
        kwargs['numLines'] = 1
        kwargs['cursorKeys'] = 1  # arrow keys enabled
        kwargs['focus'] = 1  # starts with focus
        kwargs['focusInCommand'] = self.disableButton
        kwargs['focusInExtraArgs'] = [self.originator]
        kwargs['focusOutCommand'] = self.enableButton
        kwargs['focusOutExtraArgs'] = [self.originator]

        DirectEntry.__init__(self, parent, **kwargs)
        self.initialiseoptions(LoadSaveTextEntry)  # needed for subclassing DirectGui
        self.set(BBGlobalVars.currPickleFileName)


    def disableButton(self, button):
        button['state'] = DGG.DISABLED

    def enableButton(self, button):
        button['state'] = DGG.NORMAL

    def destroy(self):
        self.originator['state'] = DGG.NORMAL
        DirectEntry.destroy(self)

    def saveGraph(self, text):
        """save the file then destroy self"""
        if text == "":
            self.destroy()
            return

        global BBGlobalVars
        BBGlobalVars.bareBonesObj.prepareForSave()
        # TODO move this to a file handler to allow user to register a callback saver/loader
        with open(text + '.pkl', 'w') as fle:
            # TODO handle full path AND handle list of none graph objects
            BBGlobalVars.currPickleFileName = text
            pickle.dump(render, fle, 0)

        BBGlobalVars.bareBonesObj.recoverFromSave()
        self.destroy()


    def loadGraph(self, text):
        """clear the current graph, load the file, and then destroy self"""
        if text == "":
            self.destroy()
            return

        global BBGlobalVars
        global render  # for some reason Python isn't finding this in builtins w/o declaring scope
        BBGlobalVars.bareBonesObj.prepareForLoad()
        self.set(BBGlobalVars.currPickleFileName)

        # TODO move this to a file handler to allow user to register a callback saver/loader
        with open(text + '.pkl', 'r') as fle:
            successful = False
            # 1st try to get a NodePath
            ren = pickle.load(fle)

            if isinstance(ren, NodePath):
                successful = True
            else:
                # TODO handle list of non-graph objects HERE
                # May pass 'ren' to the user's call back or iter over a list with a predefined attr i.e. ren[i].attr()
                # 2nd try to get a NodePath
                ren = pickle.load(fle)
                if isinstance(ren, NodePath):
                    successful = True
                else:
                    raise IOError("File %s did not have a graph in the 1st or 2nd load call" % fle.name)

            if successful:
                # clear the current graph
                for rendChild in render.getChildren():
                    if not rendChild.getName() == 'camera':
                        # remove every child of render that's not the camera
                        rendChild.node().removeAllChildren()
                        rendChild.removeNode()
                    else:
                        # remove all children of the camera without mangling the lens etc
                        # TODO handle removing/resetting the children of the camera without mangling the lens etc
                        pass

                # reparent the save graph to the current graph
                for child in ren.getChildren():
                    if not child.getName() == 'camera':
                        child.reparentTo(render)
                    else:
                        # TODO handle setting up camera
                        pass

        BBGlobalVars.bareBonesObj.recoverFromLoad()
        if not fle.closed:
            raise IOError("File %s did not close." % fle.name)
        self.destroy()

