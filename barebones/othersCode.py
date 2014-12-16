__author__ = 'Lab Hatter'

import unittest

    __all__=['SceneGraphBrowser']

    from pandac.PandaModules import *
    from direct.showbase.DirectObject import DirectObject
    from direct.gui.OnscreenText import OnscreenText
    from direct.gui.DirectGui import DirectFrame,DirectButton,DirectScrolledFrame,DGG
    from direct.interval.IntervalGlobal import Sequence
    from direct.task import Task
    from direct.showbase.PythonUtil import clampScalar
    from types import StringType


    class SceneGraphBrowser(DirectObject):
      """
         A class to display a node's selectable children with collapsible & expandable hierarchy tree
      """
      class SceneGraphItem:
            def __init__(self,np,level,editable):
                self.NP=np
                self.level=level
                self.editable=editable
                self.hidden=False
                nameStr=' '.join(np.getName().splitlines())[:25]
                if len(nameStr)==25:
                   nameStr+='....'
                self.nameStr='(%s) %s' %(np.node().getType(), nameStr)

            def remove(self):
                if hasattr(self,'treeButton'):
                   self.treeButton.destroy()
                self.nodeButton.destroy()
                self.holder.removeNode()
                self.NP=None

      def __init__(self, parent=None, root=None, command=None, contextMenu=None,
                   selectTag=[], noSelectTag=[], exclusionTag=[],
                   frameSize=(1,1.2),
                   font=None, titleScale=.05, itemScale=.045, itemTextScale=1, itemTextZ=0,
                   rolloverColor=Vec4(1,.8,.2,1),
                   collapseAll=0, suppressMouseWheel=1, modifier='control'):
          self.root=root
          self.focusSGitem=None
          self.command=command
          self.contextMenu=contextMenu
          self.selectTag=self.__wantSeq(selectTag)
          self.noSelectTag=self.__wantSeq(noSelectTag)
          self.exclusionTag=self.__wantSeq(exclusionTag)
          self.rolloverColor=Vec4(*rolloverColor)
          self.rightClickTextColors=(Vec4(0,1,0,1),Vec4(0,35,100,1))
          self.font=font
          if font:
             self.fontHeight=font.getLineHeight()
          else:
             self.fontHeight=TextNode.getDefaultFont().getLineHeight()
          self.fontHeight*=1.2 # let's enlarge font height a little
          self.xtraSideSpace=.2*self.fontHeight
          self.itemScale=itemScale
          self.itemTextScale=itemTextScale
          self.itemIndent=.07
          self.verticalSpacing=self.fontHeight*self.itemScale
          self.frameWidth,self.frameHeight=frameSize
          self.suppressMouseWheel=suppressMouseWheel
          self.modifier=modifier
          self.childrenList=[]
          self.__eventReceivers={}
          # DirectScrolledFrame to hold items
          # I set canvas' Z size smaller than the frame to avoid the auto-generated vertical slider bar
          self.childrenFrame = DirectScrolledFrame(
                       parent=parent,pos=(-self.frameWidth*.5,0,.5*self.frameHeight), relief=DGG.GROOVE,
                       state=DGG.NORMAL, # to create a mouse watcher region
                       frameSize=(0, self.frameWidth, -self.frameHeight, 0), frameColor=(0,0,0,.7),
                       canvasSize=(0, 0, -self.frameHeight*.5, 0), borderWidth=(0.01,0.01),
                       manageScrollBars=0, enableEdit=0, suppressMouse=0, sortOrder=1000 )
          # the real canvas is "self.childrenFrame.getCanvas()",
          # but if the frame is hidden since the beginning,
          # no matter how I set the canvas Z pos, the transform would be resistant,
          # so just create a new node under the canvas to be my canvas
          self.childrenCanvas=self.childrenFrame.getCanvas().attachNewNode('myCanvas')
          # DirectScrolledFrame title
          self.rootTitle = DirectFrame( parent=self.childrenFrame,
                       frameSize=(-self.frameWidth*.5,self.frameWidth*.5,0,.06),frameColor=(.1,.3,.7,.7),
                       pos=(.5*self.frameWidth,0,.005), text='', text_font=font,
                       text_scale=titleScale, text_pos=(0,.015),
                       text_fg=(1,1,1,1), text_shadow=(0,0,0,1),
                       enableEdit=0, suppressMouse=0)
          # slider background
          SliderBG=DirectFrame( parent=self.childrenFrame,frameSize=(-.025,.025,-self.frameHeight,0),
                       frameColor=(0,0,0,.7), pos=(-.03,0,0),enableEdit=0, suppressMouse=0)
          # slider thumb track
          sliderTrack = DirectFrame( parent=SliderBG, relief=DGG.FLAT, state=DGG.NORMAL,
                       frameColor=(1,1,1,.2), frameSize=(-.015,.015,-self.frameHeight+.01,-.01),
                       enableEdit=0, suppressMouse=0)
          # page up
          self.pageUpRegion=DirectFrame( parent=SliderBG, relief=DGG.FLAT, state=DGG.NORMAL,
                       frameColor=(1,.8,.2,.1), frameSize=(-.015,.015,0,0),
                       enableEdit=0, suppressMouse=1)
          self.pageUpRegion.setAlphaScale(0)
          self.pageUpRegion.bind(DGG.B1PRESS,self.__startScrollPage,[-1])
          self.pageUpRegion.bind(DGG.WITHIN,self.__continueScrollUp)
          self.pageUpRegion.bind(DGG.WITHOUT,self.__suspendScrollUp)
          # page down
          self.pageDnRegion=DirectFrame( parent=SliderBG, relief=DGG.FLAT, state=DGG.NORMAL,
                       frameColor=(1,.8,.2,.1), frameSize=(-.015,.015,0,0),
                       enableEdit=0, suppressMouse=1)
          self.pageDnRegion.setAlphaScale(0)
          self.pageDnRegion.bind(DGG.B1PRESS,self.__startScrollPage,[1])
          self.pageDnRegion.bind(DGG.WITHIN,self.__continueScrollDn)
          self.pageDnRegion.bind(DGG.WITHOUT,self.__suspendScrollDn)
          self.pageUpDnSuspended=[0,0]
          # slider thumb
          self.vertSliderThumb=DirectButton(parent=SliderBG, relief=DGG.FLAT,
                       frameColor=(1,1,1,.6), frameSize=(-.015,.015,0,0),
                       enableEdit=0, suppressMouse=1)
          self.vertSliderThumb.bind(DGG.B1PRESS,self.__startdragSliderThumb)
          self.vertSliderThumb.bind(DGG.WITHIN,self.__enteringThumb)
          self.vertSliderThumb.bind(DGG.WITHOUT,self.__exitingThumb)
          self.childrenFrame.setTag('internal component','')
          self.sliderThumbDragPrefix='draggingvertSliderThumb-'
          # collapse-all button
          DirectButton(parent=self.rootTitle,
                     frameColor=(0,.8,1,1),frameSize=(-.4,.4,-.4,.4),
                     pos=(-.5*self.frameWidth+.03,0,.03), scale=.05,
                     text='-', text_pos=(-.1,-.22), text_scale=(1.8,1), text_fg=(0,0,0,1),
                     enableEdit=0, suppressMouse=0,command=self.collapseAllTree)
          # expand-all button
          DirectButton(parent=self.rootTitle,
                     frameColor=(0,.8,1,1),frameSize=(-.4,.4,-.4,.4),
                     pos=(-.5*self.frameWidth+.075,0,.03), scale=.05,
                     text='+', text_pos=(-.05,-.22), text_scale=(1.2,1.2), text_fg=(0,0,0,1),
                     enableEdit=0, suppressMouse=0,command=self.expandAllTree)
          self.__createTreeLines()
          if self.root:
             self.setRoot(self.root,collapseAll)
          # GOD & I DAMN IT !!!
          # These things below don't work well if the canvas has a lot of buttons.
          # So I end up checking the mouse region every frame by myself using a continuous task.
    #       self.accept(DGG.WITHIN+self.childrenFrame.guiId,self.__enteringFrame)
    #       self.accept(DGG.WITHOUT+self.childrenFrame.guiId,self.__exitingFrame)
          self.isMouseInRegion=False
          self.mouseOutInRegionCommand=(self.__exitingFrame,self.__enteringFrame)
          self.mouseInRegionTaskName='mouseInRegionCheck %s'%id(self)
          self.dragSliderThumbTaskName='dragSliderThumb %s'%id(self)
          taskMgr.doMethodLater(.2,self.__getFrameRegion,'getFrameRegion')

      def __getFrameRegion(self,t):
          for g in range(base.mouseWatcher.node().getNumGroups()):
              region=base.mouseWatcher.node().getGroup(g).findRegion(self.childrenFrame.guiId)
              if region!=None:
                 self.frameRegion=region
                 taskMgr.add(self.__mouseInRegionCheck,self.mouseInRegionTaskName)
                 break

      def __mouseInRegionCheck(self,t):
          """
             checks if the mouse is within or without the scrollable frame, and
             upon within or without, run the provided command
          """
          if not base.mouseWatcher.node().hasMouse(): return Task.cont
          m=base.mouseWatcher.node().getMouse()
          bounds=self.frameRegion.getFrame()
          inRegion=bounds[0]<m[0]<bounds[1] and bounds[2]<m[1]<bounds[3]
          if self.isMouseInRegion==inRegion: return Task.cont
          self.isMouseInRegion=inRegion
          self.mouseOutInRegionCommand[inRegion]()
          return Task.cont

      def __wantSeq(self,obj):
          if type(obj)==StringType:
             return [obj]
          else:
             return obj

      def __startdragSliderThumb(self,m=None):
          mpos=base.mouseWatcherNode.getMouse()
          parentZ=self.vertSliderThumb.getParent().getZ(render2d)
          sliderDragTask=taskMgr.add(self.__dragSliderThumb,self.dragSliderThumbTaskName)
          sliderDragTask.ZposNoffset=mpos[1]-self.vertSliderThumb.getZ(render2d)+parentZ
          sliderDragTask.mouseX=(mpos[0]+1)*.5*base.winList[0].getXSize()
          sliderDragTask.winY=base.winList[0].getYSize()
          self.oldPrefix=base.buttonThrowers[0].node().getPrefix()
          base.buttonThrowers[0].node().setPrefix(self.sliderThumbDragPrefix)
          self.acceptOnce(self.sliderThumbDragPrefix+'mouse1-up',self.__stopdragSliderThumb)

      def __dragSliderThumb(self,t):
          if not base.mouseWatcherNode.hasMouse():
             return
          mpos=base.mouseWatcherNode.getMouse()
          self.__updateChildrenCanvasZpos((t.ZposNoffset-mpos[1])/self.canvasRatio)
          return Task.cont

      def __stopdragSliderThumb(self,m=None):
          taskMgr.remove(self.dragSliderThumbTaskName)
          self.__stopScrollPage()
          base.buttonThrowers[0].node().setPrefix(self.oldPrefix)
          if self.isMouseInRegion:
             self.mouseOutInRegionCommand[self.isMouseInRegion]()

      def __startScrollPage(self,dir,m):
          self.oldPrefix=base.buttonThrowers[0].node().getPrefix()
          base.buttonThrowers[0].node().setPrefix(self.sliderThumbDragPrefix)
          self.acceptOnce(self.sliderThumbDragPrefix+'mouse1-up',self.__stopdragSliderThumb)
          t=taskMgr.add(self.__scrollPage,'scrollPage',extraArgs=[int((dir+1)*.5),dir*.01/self.canvasRatio])
          self.pageUpDnSuspended=[0,0]

      def __scrollPage(self,dir,scroll):
          if not self.pageUpDnSuspended[dir]:
             self.__scrollChildrenCanvas(scroll)
          return Task.cont

      def __stopScrollPage(self,m=None):
          taskMgr.remove('scrollPage')

      def __suspendScrollUp(self,m=None):
          self.pageUpRegion.setAlphaScale(0)
          self.pageUpDnSuspended[0]=1
      def __continueScrollUp(self,m=None):
          if taskMgr.hasTaskNamed(self.dragSliderThumbTaskName):
             return
          self.pageUpRegion.setAlphaScale(1)
          self.pageUpDnSuspended[0]=0

      def __suspendScrollDn(self,m=None):
          self.pageDnRegion.setAlphaScale(0)
          self.pageUpDnSuspended[1]=1
      def __continueScrollDn(self,m=None):
          if taskMgr.hasTaskNamed(self.dragSliderThumbTaskName):
             return
          self.pageDnRegion.setAlphaScale(1)
          self.pageUpDnSuspended[1]=0

      def __suspendScrollPage(self,m=None):
          self.__suspendScrollUp()
          self.__suspendScrollDn()

      def __enteringThumb(self,m=None):
          self.vertSliderThumb['frameColor']=(1,1,1,1)
          self.__suspendScrollPage()

      def __exitingThumb(self,m=None):
          self.vertSliderThumb['frameColor']=(1,1,1,.6)

      def __scrollChildrenCanvas(self,scroll):
          if self.vertSliderThumb.isHidden():
             return
          self.__updateChildrenCanvasZpos(self.childrenCanvas.getZ()+scroll)

      def __updateChildrenCanvasZpos(self,Zpos):
          newZ=clampScalar(Zpos, .0, self.canvasLen-self.frameHeight+.015)
          self.childrenCanvas.setZ(newZ)
          thumbZ=-newZ*self.canvasRatio
          self.vertSliderThumb.setZ(thumbZ)
          self.pageUpRegion['frameSize']=(-.015,.015,thumbZ-.01,-.01)
          self.pageDnRegion['frameSize']=(-.015,.015,-self.frameHeight+.01,thumbZ+self.vertSliderThumb['frameSize'][2])

      def __collapseTree(self,idx):
          self.childrenList[idx].status=1
          self.childrenList[idx].treeButton['text']='+'
          self.childrenList[idx].treeButton['text_scale']=1
          self.childrenList[idx].treeButton['text_pos']=(-.07,-.21)
          self.childrenList[idx].treeButton['command']=self.__expandTreeNupdate
          collapsed=0
          for i in range(idx+1,len(self.childrenList)):
              if self.childrenList[i].level>self.childrenList[idx].level:
                 if not self.childrenList[i].hidden:
                    collapsed+=1
                 self.childrenList[i].holder.hide()
                 self.childrenList[i].hidden=True
              else:
                 break
          Zoffset=collapsed*self.verticalSpacing
          for i in range(idx+collapsed,len(self.childrenList)):
              self.childrenList[i].holder.setZ(self.childrenList[i].holder,Zoffset)
          self.numVisibleItems-=collapsed

      def __expandTree(self,idx):
          self.childrenList[idx].status=-1
          self.childrenList[idx].treeButton['text']='-'
          self.childrenList[idx].treeButton['text_scale']=(1.6,1)
          self.childrenList[idx].treeButton['text_pos']=(-.1,-.22)
          self.childrenList[idx].treeButton['command']=self.__collapseTreeNupdate
          expanded=0
          ignoredLevel=0
          for i in range(idx+1,len(self.childrenList)):
              if self.childrenList[i].level>self.childrenList[idx].level:
                 if self.childrenList[i].level<=ignoredLevel:
                    ignoredLevel=0
                 if not ignoredLevel:
                    expanded+=1
                    self.childrenList[i].holder.show()
                    self.childrenList[i].hidden=False
                    if self.childrenList[i].status==1:
                       ignoredLevel=self.childrenList[i].level
              else:
                 break
          Zoffset=-expanded*self.verticalSpacing
          for i in range(idx+expanded,len(self.childrenList)):
              self.childrenList[i].holder.setZ(self.childrenList[i].holder,Zoffset)
          self.numVisibleItems+=expanded

      def __collapseTreeNupdate(self,idx):
          self.__collapseTree(idx)
          self.__adjustCanvasLength(self.numVisibleItems)
          self.__updateVertTreeLines(idx)
          prevLevel=self.__getchildrenPrevLevel(idx)
          while self.childrenList[prevLevel].level>0 and prevLevel>=0:
                self.__updateVertTreeLines(prevLevel)
                prevLevel=self.__getchildrenPrevLevel(prevLevel)

      def __expandTreeNupdate(self,idx):
          self.__expandTree(idx)
          self.__adjustCanvasLength(self.numVisibleItems)
          self.__updateVertTreeLines(idx)
          prevLevel=self.__getchildrenPrevLevel(idx)
          while self.childrenList[prevLevel].level>0 and prevLevel>=0:
                self.__updateVertTreeLines(prevLevel)
                prevLevel=self.__getchildrenPrevLevel(prevLevel)

      def collapseAllTree(self):
          print '----'
          start=globalClock.getRealTime()
          self.expandAllTree()
          for i in range(len(self.childrenList)-1,-1,-1):
              if self.childrenList[i].status==-1:
                 self.__collapseTree(i)
                 self.__adjustCanvasLength(self.numVisibleItems)
                 self.__updateVertTreeLines(i)
          print globalClock.getRealTime()-start

      def expandAllTree(self):
          print '++++'
          start=globalClock.getRealTime()
          for i in range(len(self.childrenList)):
              if self.childrenList[i].status==1:
                 self.__expandTree(i)
          self.__adjustCanvasLength(self.numVisibleItems)
          for i in range(len(self.childrenList)-1,-1,-1):
              if self.childrenList[i].status!=0:
                 self.__updateVertTreeLines(i)
          print globalClock.getRealTime()-start

      def __updateVertTreeLines(self,idx):
          if idx<0:
             return
          for i in range(idx+1,len(self.childrenList)):
              if self.childrenList[i].level<=self.childrenList[idx].level:
                 break
              if self.childrenList[i].level==self.childrenList[idx].level+1:
                 lastNextLevel=i
          visible=0
          for i in range(idx+1,lastNextLevel+1):
              if not self.childrenList[i].hidden:
                 visible+=1
          if visible:
             vert=self.childrenList[idx].VtreeLines.getChild(0)
             vert.setZ(.25*self.itemScale)
             vert.setSz(visible)
             self.childrenList[idx].VtreeLines.show()
          else:
             self.childrenList[idx].VtreeLines.hide()

      def __getchildrenPrevLevel(self,idx):
          prevLevel=-1
          for i in range(idx,-1,-1):
              if self.childrenList[i].level==self.childrenList[idx].level-1:
                 return i
          return prevLevel

      def __adjustCanvasLength(self,numItem):
          self.canvasLen=float(numItem)*self.verticalSpacing
          self.canvasRatio=(self.frameHeight-.015)/(self.canvasLen+.01)
          if self.canvasLen<self.frameHeight-.015:
             canvasZ=.0
             self.vertSliderThumb.hide()
             self.pageUpRegion.hide()
             self.pageDnRegion.hide()
             self.canvasLen=self.frameHeight-.015
          else:
             canvasZ=self.childrenCanvas.getZ()
             self.vertSliderThumb.show()
             self.pageUpRegion.show()
             self.pageDnRegion.show()
          self.__updateChildrenCanvasZpos(canvasZ)
          self.vertSliderThumb['frameSize']=(-.015,.015,-self.frameHeight*self.canvasRatio,-.01)
          thumbZ=self.vertSliderThumb.getZ()
          self.pageUpRegion['frameSize']=(-.015,.015,thumbZ-.01,-.01)
          self.pageDnRegion['frameSize']=(-.015,.015,-self.frameHeight+.01,thumbZ+self.vertSliderThumb['frameSize'][2])

      def __createTreeLines(self):
          # create horisontal tree line
          color=(1,0,0,.9)
          self.horisontalTreeLine=NodePath(self.__createLine(
               self.itemIndent+self.itemScale*.5,
               color,endColor=(1,1,1,.1),centered=0))
          self.horisontalTreeLine.setTag('internal component','')
          self.horisontalTreeLine.setTwoSided(0,100)
          self.horisontalTreeLine.setTransparency(1)
          # create vertical tree line
          self.verticalTreeLine=NodePath(self.__createLine(self.verticalSpacing,color,centered=0))
          self.verticalTreeLine.setR(90)
          self.verticalTreeLine.setTag('internal component','')
          self.verticalTreeLine.setTwoSided(0,100)
          self.verticalTreeLine.setTransparency(1)

      def __createLine(self, length=1, color=(1,1,1,1), endColor=None, thickness=1, centered=1):
          LS=LineSegs()
          LS.setColor(*color)
          LS.setThickness(thickness)
          LS.moveTo(-length*.5*centered,0,0)
          LS.drawTo(length*(1-.5*centered),0,0)
          node=LS.create()
          if endColor:
             LS.setVertexColor(1,*endColor)
          return node

      def __acceptAndIgnoreWorldEvent(self,event,command,extraArgs=[]):
          receivers=messenger.whoAccepts(event)
          if receivers is None:
             self.__eventReceivers[event]={}
          else:
             self.__eventReceivers[event]=receivers.copy()
          for r in self.__eventReceivers[event].keys():
              r.ignore(event)
          self.accept(event,command,extraArgs)

      def __ignoreAndReAcceptWorldEvent(self,events):
          for event in events:
              self.ignore(event)
              if self.__eventReceivers.has_key(event):
                 for r, method_xtraArgs_persist in self.__eventReceivers[event].items():
                     messenger.accept(event,r,*method_xtraArgs_persist)
              self.__eventReceivers[event]={}

      def __enteringFrame(self,m=None):
          # sometimes the WITHOUT event for page down region doesn't fired,
          # so directly suspend the page scrolling here
          self.__suspendScrollPage()
          BTprefix=base.buttonThrowers[0].node().getPrefix()
          if BTprefix==self.sliderThumbDragPrefix:
             return
          self.inOutBTprefix=BTprefix
          if self.suppressMouseWheel:
             self.__acceptAndIgnoreWorldEvent(self.inOutBTprefix+'wheel_up',
                  command=self.__scrollChildrenCanvas, extraArgs=[-.07])
             self.__acceptAndIgnoreWorldEvent(self.inOutBTprefix+'wheel_down',
                  command=self.__scrollChildrenCanvas, extraArgs=[.07])
          else:
             self.accept(self.inOutBTprefix+self.modifier+'-wheel_up',self.__scrollChildrenCanvas, [-.07])
             self.accept(self.inOutBTprefix+self.modifier+'-wheel_down',self.__scrollChildrenCanvas, [.07])
          print 'enteringFrame'

      def __exitingFrame(self,m=None):
          if not hasattr(self,'inOutBTprefix'):
             return
          if self.suppressMouseWheel:
             self.__ignoreAndReAcceptWorldEvent( (
                                                 self.inOutBTprefix+'wheel_up',
                                                 self.inOutBTprefix+'wheel_down',
                                                 ) )
          else:
             self.ignore(self.inOutBTprefix+self.modifier+'-wheel_up')
             self.ignore(self.inOutBTprefix+self.modifier+'-wheel_down')
          print 'exitingFrame'

      def __listchildren(self,np,level,editable=True):
          status=0
          listIdx=len(self.childrenList)-1
          if np!=self.root:
             self.childrenList[-1].holder=self.childrenCanvas.attachNewNode('')
             self.childrenList[-1].HtreeLines=self.childrenList[-1].holder.attachNewNode('HtreeLines')
             self.childrenList[-1].VtreeLines=self.childrenList[-1].holder.attachNewNode('VtreeLines')
             self.childrenList[-1].VtreeLines.setX(-.5*self.itemIndent)
          for c in np.getChildrenAsList():
              tagExist=False
              for t in self.exclusionTag:
                  tagExist|=c.hasTag(t)
              if not tagExist:
                 noSelectTagExist=not editable
                 if self.selectTag:
                    tagExist=False
                    for t in self.selectTag:
                        tagExist|=c.hasTag(t)
                    self.childrenList.append( self.SceneGraphItem(c,level,tagExist) )
                 elif self.noSelectTag:
                    if editable: # if parent is already not editable, no need to check child's tag(s)
                       for t in self.noSelectTag:
                           noSelectTagExist|=c.hasTag(t)
                    self.childrenList.append( self.SceneGraphItem(c,level,not noSelectTagExist) )
                 else:
                    self.childrenList.append( self.SceneGraphItem(c,level,True) )
                 lastNextLevel=len(self.childrenList)-1
                 self.__listchildren(c,level+1,editable=not noSelectTagExist)
                 if np!=self.root:
                    hor=self.horisontalTreeLine.instanceUnderNode(self.childrenList[lastNextLevel].HtreeLines,'')
                    hor.setPos(-1.5*self.itemIndent,0,self.itemScale*.25)
                 status=-1
          if status!=0:
             if np!=self.root:
                vert=self.verticalTreeLine.instanceUnderNode(self.childrenList[listIdx].VtreeLines,'')
                vert.setZ((listIdx-lastNextLevel+.25)*self.verticalSpacing)
                vert.setSz(listIdx-lastNextLevel)
          if listIdx>=0:
             self.childrenList[listIdx].status=status

      def __rightPressed(self,SGitem,m):
          self.__isRightIn=True
    #       text0 : normal
    #       text1 : pressed
    #       text2 : rollover
    #       text3 : disabled
          SGitem.nodeButton._DirectGuiBase__componentInfo['text2'][0].setColorScale(self.rightClickTextColors[self.focusSGitem==SGitem])
          SGitem.nodeButton.bind(DGG.B3RELEASE,self.__rightReleased,[SGitem])
          SGitem.nodeButton.bind(DGG.WITHIN,self.__rightIn,[SGitem])
          SGitem.nodeButton.bind(DGG.WITHOUT,self.__rightOut,[SGitem])

      def __rightIn(self,SGitem,m):
          self.__isRightIn=True
          SGitem.nodeButton._DirectGuiBase__componentInfo['text2'][0].setColorScale(self.rightClickTextColors[self.focusSGitem==SGitem])
      def __rightOut(self,SGitem,m):
          self.__isRightIn=False
          SGitem.nodeButton._DirectGuiBase__componentInfo['text2'][0].setColorScale(Vec4(1,1,1,1))

      def __rightReleased(self,SGitem,m):
          SGitem.nodeButton.unbind(DGG.B3RELEASE)
          SGitem.nodeButton.unbind(DGG.WITHIN)
          SGitem.nodeButton.unbind(DGG.WITHOUT)
          SGitem.nodeButton._DirectGuiBase__componentInfo['text2'][0].setColorScale(self.rolloverColor)
          if not self.__isRightIn:
             return
          if callable(self.contextMenu):
             self.contextMenu(SGitem.NP) # run user command and pass the selected node

      def __selectSGitem(self,SGitem,runUserCommand=True):
          self.focusSGitem=SGitem
          if self.button:
             self.restoreNodeButton2Normal()
          self.button=SGitem.nodeButton
          self.highlightNodeButton()
          if callable(self.command) and runUserCommand:
             self.command(SGitem.NP) # run user command and pass the selected node

      def selectNode(self,np,runUserCommand=True):
          """
             deselects currently selected node and selects the given one
                 np : the desired nodepath
                 runUserCommand : run user command or not
                                  (in case you call selectNode from the command method itself,
                                  set this to False, so the method won't be called again)
             Returns the node's index.
          """
          for i in self.childrenList:
              if i.NP==np:
                 selectedIdx=self.childrenList.index(i)
                 self.__selectSGitem(i,runUserCommand)
                 selectedIdx=self.childrenList.index(self.focusSGitem)
                 self.__exposeSelectedNode()
                 return selectedIdx
          return None

      def __exposeSelectedNode(self):
          selectedIdx=self.childrenList.index(self.focusSGitem)
          # before counting the visible items until the selected one,
          # expand all collapsed parents until the selected item, if the item is hidden
          if self.focusSGitem.hidden:
             mustBeExpanded=[]
             currentLevel=self.focusSGitem.level
             idx=selectedIdx
             while idx>=0:
                   if self.childrenList[idx].level<currentLevel:
                      if self.childrenList[idx].status==1:
                         # the tree expansion works sequential from the root to the leaves,
                         # so expand it later after get reversed
                         mustBeExpanded.append(idx)
                      currentLevel-=1
                   if self.childrenList[idx].level==1:
                      break
                   idx-=1
             mustBeExpanded.reverse()
             for i in mustBeExpanded:
                 self.__expandTreeNupdate(i)
          # count the visible items until the selected item
          idx=0
          visibleItemIdx=1
          ignoredLevel=0
          while idx!=selectedIdx:
                if self.childrenList[idx].level<=ignoredLevel:
                   ignoredLevel=0
                if not ignoredLevel:
                   visibleItemIdx+=1
                   if self.childrenList[idx].status==1:
                      ignoredLevel=self.childrenList[idx].level
                idx+=1
          # adjust canvas' Z if the selected item is outside the frame
          canvasZ=self.childrenCanvas.getZ()
          newZ=canvasZ
          if canvasZ-(visibleItemIdx+.9)*self.verticalSpacing<-self.frameHeight+.015:
             newZ=(visibleItemIdx+.9)*self.verticalSpacing-self.frameHeight
          elif canvasZ-(visibleItemIdx-1.5)*self.verticalSpacing>.0:
             newZ=(visibleItemIdx-1.5)*self.verticalSpacing
          if newZ!=canvasZ:
             self.__updateChildrenCanvasZpos(newZ)

      def restoreNodeButton2Normal(self):
          """
             removes the highlight from the currently selected node
          """
          self.button['text_fg']=(1,1,1,1)
          self.button['frameColor']=(0,0,0,0)

      def highlightNodeButton(self,idx=None):
          """
             sets highlight on currently selected node, or node which has the given index
          """
          if idx is not None:
             self.button=self.childrenList[idx].nodeButton
          self.button['text_fg']=(.01,.01,.01,1)
          self.button['frameColor']=(1,.8,.2,1)

      def clear(self):
          """
             clears all nodes from the list
          """
          for c in self.childrenList:
              c.remove()
          self.childrenList=[]
          self.root=None
          self.focusSGitem=None
          self.button=None

      def setRoot(self,root,collapseAll=0):
          """
             sets the root node whose children will be displayed
                  collapseAll : initial tree state
          """
          self.clear()
          self.root=root
    #       startT=globalClock.getRealTime()
          self.__listchildren(root,1)
    #       self.SGreadTime=globalClock.getRealTime()-startT
    #       startT=globalClock.getRealTime()
          colors=((.5,.5,.5,1),(1,1,1,1))
          # top & bottom of the buttons' frame are blindly set without knowing
          # where exactly the baseline is, but this ratio fits most fonts
          baseline=-self.fontHeight*.25
          topFrame=baseline+self.fontHeight
          textColors=((.5,.5,.5,1),(1,1,1,1))
          idx=0
          for c in self.childrenList:
              c.holder.setPos(c.level*self.itemIndent,0,(-.7-idx)*self.verticalSpacing)
              c.nodeButton = DirectButton(parent=c.holder,
                  scale=self.itemScale, relief=DGG.FLAT,
                  frameColor=(0,0,0,0),text_scale=self.itemTextScale,
                  text=c.nameStr, text_fg=textColors[c.editable],
                  text_font=self.font, text_align=TextNode.ALeft,
                  command=self.__selectSGitem,extraArgs=[c],
                  enableEdit=0, suppressMouse=0)
              l,r,b,t=c.nodeButton.getBounds()
              c.nodeButton['frameSize']=(l-self.xtraSideSpace,r+self.xtraSideSpace,baseline,topFrame)
              c.nodeButton.node().setActive(c.editable)
              c.nodeButton._DirectGuiBase__componentInfo['text2'][0].setColorScale(self.rolloverColor)
              c.nodeButton.bind(DGG.B3PRESS,self.__rightPressed,[c])
              if c.status==-1:
                 c.treeButton = DirectButton(parent=c.nodeButton,
                     frameColor=(1,1,1,1),frameSize=(-.4,.4,-.4,.4),
                     pos=(-.5*self.itemIndent/self.itemScale,0,.25),
                     text='-', text_pos=(-.1,-.22), text_scale=(1.6,1), text_fg=(0,0,0,1),
                     enableEdit=0, suppressMouse=0,command=self.__collapseTreeNupdate,extraArgs=[idx])
              idx+=1
    #       self.btnGenTime=globalClock.getRealTime()-startT
          self.numVisibleItems=len(self.childrenList)
          self.__adjustCanvasLength(self.numVisibleItems)
          self.rootTitle['text']='CHILDREN  of  '+self.root.getName().upper()
          if collapseAll:
             self.collapseAllTree()
    #       print '===== %s =====' %root.getName().upper()
    #       print 'SGreadTime : %s sec{s}\nbtnGenTime : %s sec{s}\nratio = 1:%f' %(self.SGreadTime,self.btnGenTime,self.btnGenTime/self.SGreadTime)
    #       print '====================='

      def refresh(self):
          """
             refreshes the displayed scenegraph, means re-read (traverse) the scenegraph
             to update any changes
          """
          if self.root:
             self.setRoot(self.root)

      def destroy(self):
          self.clear()
          self.__exitingFrame()
          self.ignoreAll()
          self.childrenFrame.removeNode()
          taskMgr.remove(self.mouseInRegionTaskName)

      def hide(self):
          self.childrenFrame.hide()
          self.isMouseInRegion=False
          self.__exitingFrame()
          taskMgr.remove(self.mouseInRegionTaskName)

      def show(self):
          self.childrenFrame.show()
          if not hasattr(self,'frameRegion'):
             taskMgr.doMethodLater(.2,self.__getFrameRegion,'getFrameRegion')
          elif not taskMgr.hasTaskNamed(self.mouseInRegionTaskName):
             taskMgr.add(self.__mouseInRegionCheck,self.mouseInRegionTaskName)

      def toggleVisibility(self):
          if self.childrenFrame.isHidden():
             self.show()
          else:
             self.hide()




if __name__=='__main__':
   import direct.directbase.DirectStart
   from random import uniform
   import sys
   selected=None

   def nodeSelected(np): # don't forget to receive the selected node (np)
       global selected
       selected=np
       np.hprInterval(1,Vec3(0,0,np.getR()+360)).start()
       print np.getName(),'SELECTED'

   def nodeRightClicked(np): # don't forget to receive the selected node (np)
       np.hprInterval(1.2,Vec3(0,0,np.getR()-360)).start()
       origScale=np.getScale()
       Sequence(
                np.scaleInterval(.6,origScale*1.2,origScale),
                np.scaleInterval(.6,origScale),
                ).start()
       print np.getName(),'RIGHT CLICKED, DO SOMETHING !'

   def putNewSmiley():
       if not selected:
          return
       lilSmiley=loader.loadModel('misc/lilsmiley').find('**/poly')
       lilSmiley.reparentTo(selected,sort=-100)
       lilSmiley.clearColor()
       lilSmiley.setScale(.2,.2,.1)
       lilSmiley.setPos(selected.getBounds().getCenter()+Point3(uniform(-1,1),0,uniform(-1,1)))
       lilSmiley.setName('newSmiley_'+str(id(lilSmiley)))

   def createNestedSmileys(parent,depth,branch,color):
       parent.setColor(color,1000-depth)
       for d in range(depth):
           scale=.55
           kidSmileys=lilsmileyGeom.instanceUnderNode(parent,'kid_Smileys_'+str(id(parent)))
           kidSmileys.setX(d+1)
           kidSmileys.setScale(scale)
           kidSmileys.setR(60*((d%2)*2-1))
           color=color*.8
           color.setW(1)
           for b in range(branch):
               z=b-(branch-1)*.5
               kidSmiley=lilsmileyGeom.instanceUnderNode(kidSmileys,'smileyBranch_%i-%i' %(id(kidSmileys),b))
               kidSmiley.setPos(1,0,z*scale)
               kidSmiley.setScale(scale)
               kidSmiley.setR(-z*30)
               createNestedSmileys(kidSmiley,depth-1,branch,color)
   # some 3d nodes
   teapot=loader.loadModel('teapot')
   teapot.reparentTo(render)
   panda=loader.loadModel('zup-axis')
   panda.reparentTo(render)
   panda.setScale(.22)
   panda.setPos(4.5,-5,0)

   # some 2d nodes
   lilsmiley1=loader.loadModelCopy('misc/lilsmiley')
   lilsmiley1.reparentTo(aspect2d)
   lilsmileyGeom=lilsmiley1.find('**/poly')
   createNestedSmileys(lilsmiley1,3,2,Vec4(0,1,0,1))
   lilsmiley1.setX(render2d,-.7)
   lilsmiley1.setScale(.5)

   OnscreenText(text='''[ 1 ] : display render's children       [ 2 ] : display aspect2d's children       [ 3 ] : display render2d's children
[ H ] : hide browser        [ S ] : show browser        [ SPACE ] : toggle visibility
[ R ] : refresh browser        [ DEL ] : destroy browser
[ MOUSE WHEEL ] inside scrollable window : scroll window
[ MOUSE WHEEL ] outside scrollable window : change teapot scale
hold [ ENTER ] : attach new smiley on selected node
''', scale=.045, fg=(1,1,1,1), shadow=(0,0,0,1)).setZ(.96)

#    # load other font
#    transMtl=loader.loadFont('Transmetals.ttf')
#    transMtl.setLineHeight(.9)

   # create SceneGraphBrowser and point it on aspect2d
   treeList=SceneGraphBrowser(
               parent=None, # where to attach SceneGraphBrowser frame
               root=aspect2d, # display children under this root node
               command=nodeSelected, # user defined method, executed when a node get selected,
                                     # with the selected node passed to it
               contextMenu=nodeRightClicked,
               # selectTag and noSelectTag are used to filter the selectable nodes.
               # The unselectable nodes will be grayed.
               # You should use only selectTag or noSelectTag at a time. Don't use both at the same time.
               #selectTag=['select'],   # only nodes which have the tag(s) are selectable. You could use multiple tags.
               noSelectTag=['noSelect','dontSelectMe'], # only nodes which DO NOT have the tag(s) are selectable. You could use multiple tags.
               # nodes which have exclusionTag wouldn't be displayed at all
               exclusionTag=['internal component'],
               frameSize=(1,1.2),
               font=None, titleScale=.05, itemScale=.035, itemTextScale=1.2, itemTextZ=0,
#                font=transMtl, titleScale=.055, itemScale=.043, itemTextScale=1, itemTextZ=0,
               rolloverColor=(1,.8,.2,1),
               collapseAll=0, # initial tree state
               suppressMouseWheel=1,  # 1 : blocks mouse wheel events from being sent to all other objects.
                                      #     You can scroll the window by putting mouse cursor
                                      #     inside the scrollable window.
                                      # 0 : does not block mouse wheel events from being sent to all other objects.
                                      #     You can scroll the window by holding down the modifier key
                                      #     (defined below) while scrolling your wheel.
               modifier='control'  # shift/control/alt
               )
   # You could change selectTag, noSelectTag, or exclusionTag any time,
   # in case you need different filter for different root, or at a special moment.
   # They are instance attributes, you can change them directly :
   #    treeList.selectTag
   #    treeList.noSelectTag
   #    treeList.exclusionTag
   # If you have multiple tags, pack them in a sequence.

   # The top node of treeList's scrollable frame is childrenFrame,
   # you could do any nodepath (or DirectScrolledFrame) operation on it,
   # except hide, show, and destroy.
   # If you need to use them, use treeList's hide, show, and destroy instead
   # (see events accepting below), because they do some additional stuff
   # in order to work properly.
   treeListFrame=treeList.childrenFrame

   DO=DirectObject()
   # events for treeList
   DO.accept('1',treeList.setRoot,[render])
   DO.accept('2',treeList.setRoot,[aspect2d])
   DO.accept('3',treeList.setRoot,[render2d])
   DO.accept('r',treeList.refresh)
   DO.accept('h',treeList.hide)
   DO.accept('s',treeList.show)
   DO.accept('space',treeList.toggleVisibility)
   DO.accept('delete',treeList.destroy)
   # events for the world
   DO.accept('wheel_up',teapot.setScale,[teapot,1.2])
   DO.accept('wheel_down',teapot.setScale,[teapot,.8])
   DO.accept('enter',putNewSmiley)
   DO.accept('enter-repeat',putNewSmiley)
   DO.accept('escape',sys.exit)

   camera.setPos(11.06, -16.65, 8.73)
   camera.setHpr(42.23, -25.43, -0.05)
   camera.setTag('noSelect','')
#    base.cam.setTag('dontSelectMe','')
   base.setBackgroundColor(.2,.2,.2,1)
   base.disableMouse()
#    messenger.toggleVerbose()
   # to visualize the mouse regions, uncomment the next line
#    base.mouseWatcherNode.showRegions(render2d,'gui-popup',0)
