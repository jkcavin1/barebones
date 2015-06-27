__author__ = 'Lab Hatter'

from direct.showbase.ShowBase import messenger
from collections import deque

class UndoHandler(object):
    maxUndoLimit = 50
    def __init__(self):
        """
            A queue of (targetObj, command) pairs. Also allows observers to subscribe to the effective command stream.
            - observers must pass observing object to subscribe i.e. undoHandler.subscribe(observerSelf, callbackFunc)
            - observing object's callback:
              * must handle arguments trgObj & command i.e. callback(trgObj, command)
              * must return None or list of commands which contains original command i.e [observersComm, origCommand]
            - observing object's returned command list will be executed in listed order upon undo/redo operations
            - observing object cannot change target object
        """
        # http://blog.wolfire.com/2009/02/how-we-implement-undo/

        # Undo() calls UnExecute() on the pointed to command and then moves the pointer back one step;
        # Redo() moves the pointer forward one step and then calls Execute() on the newly pointed to item.
        # As is usual, the redo side of the list is cleared whenever any new actions are recorded.

        # TODO: handle observers in record(), if workable.
        # td If smaller operations need observed, this will be a pure Undo/Redo and observers will be handled elsewhere
        self._observers = []
        ##########################################################
        # deque append and pop from the right side by default
        ##########################################################
        self._undoQueue = deque(maxlen=UndoHandler.maxUndoLimit)
        self._redoQueue = deque(maxlen=UndoHandler.maxUndoLimit)
        self._trgObjInd = 0
        self._commandInd = 1

        messenger.accept('control-z', self, self._undo, persistent=1)
        messenger.accept('control-y', self, self._redo, persistent=1)

    def subscribe(self):
        raise NotImplementedError('Make UndoHandler subscribable.')


    def unsubscribe(self):
        raise NotImplementedError('Make UndoHandler subscribable.')


    def record(self, targetObject, commandObj):
        """ Pushes a command and the target of the command onto the undo stack.
            UndoHandler does nothing to the target. It is only kept for observers.
        """
        # TODO: handle observers
        # region  FOLD: Unemplemented observer code. Only runs whe observer added.
        # needs to handle multiple of observers adding to the command
        if len(self._observers) > 0:
            raise NotImplementedError('The undo observer code needs thoroughly tested. Including multiple observers of the same command')
            for obsv in self._observers:
                returnVal = obsv.observe(targetObject, commandObj)
                if returnVal is None:
                    # observer does nothing with the command
                    pass
                else:
                    if commandObj not in returnVal or not hasattr(returnVal, '__iter__'):
                        raise AssertionError('When observing UndoHandler, the observer must '
                                             'return None or the original command in an iterable sequence of commands.')
                    commandObj = returnVal  # add the list of commands to the command part of the element
        # endregion

        # appends to the right
        self._undoQueue.append((targetObject, commandObj))
        self._redoQueue.clear()


    def _undo(self):
        try:
            # pops right
            com = self._undoQueue.pop()
        except IndexError:
            pass

        try:
            com[self._commandInd].undo()
            # appends right
            self._redoQueue.append(com)
        except UnboundLocalError:
            pass


    def _redo(self):
        try:
            # pops right
            com = self._redoQueue.pop()

        except IndexError:
            pass

        try:
            com[self._commandInd].execute()
            # appends right
            self._undoQueue.append(com)
        except UnboundLocalError:
            pass


if __name__ == '__main__':
    app = UndoHandler()