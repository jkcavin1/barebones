__author__ = 'Lab Hatter'

# from barebones.commands.commandBase import CommandBase
from commandBase import CommandBase
# <editor-fold desc="Command Attribute assignemnt not implemented">
# class CommandObjAttribAssignment(CommandBase):
#     def __init__(self, targetObj, attrib, newValue):
#         """A command that assigns newValue to targetObj's attribute or indexed value (e.g. uses [] for assignment)"""
#         super(CommandObjAttribAssignment, self).__init__()
#         self.targetObj = targetObj
#         self.value = newValue
#         self.targetObjAttrib = attrib
#
#     def execute(self):
#         """Assigns cmd.value to targetVar and retains previous value in cmd.value"""
#         tmp = self.value
#         raise NotImplementedError("CommandObjAttribAssignment is not correctly implemented (see comment)")
#         # this possibly conjoins the targetObj with whatever is in the mro() call
#         # separate these i.e. if attr in target assign elif attr in mro() assign else: raise TypeError exception
#         try:
#             for obj in [self.targetObj]+self.targetObj.__class__.mro():
#                 if self.targetObjAttrib in obj.__dict__:
#                     obj.__dict__[self.targetObjAttrib] = self.value
#         except AttributeError:
#             for obj in [self.targetObj]:
#                 if self.targetObjAttrib in obj.__dict__:
#                     obj.__dict__[self.targetObjAttrib] = self.value
#         self.value = tmp
# </editor-fold>


class CommandFuncCall(CommandBase):
    def __init__(self, func, *args, **kwargs):
        """Operates with func via a call to func(*args, **kwargs)"""
        super(CommandFuncCall, self).__init__()
        self.actingFunc = func
        self.args = args
        self.kwargs = kwargs

    def execute(self):
        """Executes func using the arguments supplied to the constructor."""
        # print "args then kwargs"
        # print self.args
        # print self.kwargs
        self.actingFunc(*self.args, **self.kwargs)



class UndoCommandOneFuncCall(CommandFuncCall):
    def __init__(self, undoArgLst, doFunc, *doArgs, **doKwargs):
        """Command execute() executes doFunc(*doArgs, **doKwargs)
        Command undo() executes undoFunc(undoArgLst).
        - undoArgLst lists all arguments to undo execute().
          The first n or n-1 elements will be past as *undoArgLst and/or *undoArgLst[0:-1]
          When the last element is a dict it will be past as **undoArgs[-1]
            i.e. self.actingFunc(*self.undoArgs[:-1], **self.undoArgs[-1])"""
        super(UndoCommandOneFuncCall, self).__init__(doFunc, *doArgs, **doKwargs)
        self.undoArgs = undoArgLst

    def undo(self):
        """Undoes the effects of execute()"""
        if isinstance(self.undoArgs[-1], dict):
            self.actingFunc(*self.undoArgs[:-1], **self.undoArgs[-1])
        else:
            self.actingFunc(*self.undoArgs)



#--------------------------------------------------------------
#--------------------------------------------------------------
if __name__ == '__main__':
    """
    class B(list):
        def __init__(self, val):
            list().__init__(self)
            #super(B, self).__init__()
            self.var = val
    trg2 = B(10)
    cmd2 = CommandObjAttribAssignment(trg2, 'var', 20)
    print trg2.var
    cmd2.execute()
    print trg2.var
    print(trg2.__dict__)
    """


    from direct.actor.Actor import Actor
    from direct.showbase.ShowBase import ShowBase
    from panda3d.core import Point3
    from inspect import getmembers

    class App(ShowBase):
        def __init__(self):
            ShowBase.__init__(self)
            self.act = Actor("models/panda-model"
                            , {"walk": "models/panda-walk4"})

            self.dummy = render.attachNewNode("dummy")
            self.dummy.setPos( Point3(-60.0, 60.0, -60.0))


            self.act.reparentTo(self.dummy)
            self.act.setPos(Point3(-60.0, -60.0, -60.0))
            print "original pos wrt dummy ", self.act.getPos(self.dummy)
            print self.act.getParent(), " << parent|||wrt render>>>", self.act.getPos(render)
            self.act.setScale(.05)
            self.command = UndoCommandOneFuncCall([self.act.getPos()],
                                                  self.act.setPos, render, Point3(-60.0, -60.0, -60.0))
            base.disableMouse()
            camera.setPos( 60.0, 60.0, 60.0)
            camera.lookAt(self.act)
            from direct.task.Task import Task

            # can remove task from extraArgs below
            # THEN SHOULD pass func2 to taskMgr as the callback instead of task
            def func2(task, comm):
                comm.execute()
                print task.time
                return task.done

            task = Task(func2)
            # to do without passing task to func2 remove task from extraArgs and func2's signature
            # THEN SHOULD pass func2 to taskMgr as the callback instead of task
            taskMgr.doMethodLater(1.0, task, 'taskinator', extraArgs=[task, self.command])

            def funcUndo(task, comm):
                comm.undo()
                return task.done
            self.undoTask = Task(funcUndo)
            # def printPosWrt(act, dummy):
            #     print "Pos wrt render then dummy"
            #     print act.getPos(render)
            #     print act.getPos(dummy)


            # printTask = Task(printPosWrt)
            taskMgr.doMethodLater(3.0, self.undoTask, 'taskUndo', extraArgs=[self.undoTask, self.command])

    ap = App()
    #print ap.act.pos
    ap.run()


