__author__ = 'Lab Hatter'


import math
from Queue import PriorityQueue
from panda3d.core import Vec3, Point3, LineSegs
from PolygonUtils.PolygonUtils import getDistance, getCenterOfPoint3s, getLeftPt
from PolygonUtils.AdjacencyList import AdjLstElement, copyAdjLstElement, getSharedEdgeStr


class FunVecs(object):
    def __init__(self, start, left, lPt, right, rPt):
        self.start = start
        self.left = left
        self.lPt = lPt
        self.right = right
        self.rPt = rPt

    def getCross(self):
        return self.left.cross(self.right)

    def updateLeft(self, newPt):
        self.lPt = newPt
        self.left = Vec3(newPt - self.start)

    def updateRight(self, newPt):
        self.rPt = newPt
        self.right = Vec3(newPt - self.start)

    def reset(self, start, proposedLeft, proposedRight):
        left = Vec3(proposedLeft - start)
        lpt = proposedLeft
        right = Vec3(proposedRight - start)
        rpt = proposedRight
        # if these are on the wrong side switch them
        # print "startPt", startPt  #, " mid - startPt ", getCenterOfPoint3s(shared)
        mid = getCenterOfPoint3s([proposedLeft, proposedRight]) - start
        # print "mid", mid, midP, " leftVec - mid ", lpt-mid, shared, leftVec
        if left.cross(mid).z > 0.0:
            print "swap"
            tmp = left
            left = right
            right = tmp

            tmp = lpt
            lpt = rpt
            rpt = tmp
        self.start = start
        self.left = left
        self.right = right
        self.rPt = rpt
        self.lPt = lpt
        print "reset", self

    def needNewApex(self):
        return self.getCross().length() <= 0.0


    def area(self, vec1, vec2):
        ax = vec1.x
        ay = self.start.y
        bx = vec1.x
        by = vec1.y
        cx = vec2.x
        cy = vec2.y
        return ax * (by - cy) + bx * (cy - ay) + cx * (ay - by)

    def __repr__(self):
        return "< startPt: " + str(self.start) +\
               ", leftPt: " + str(self.lPt) +\
               ", rightPt: " + str(self.rPt) #+\
               #", leftVec: " + str(self.leftVec) +\
               #", rightVec: " + str(self.rightVec) +\
               #">"


class TriangulationAStar(object):
    def __init__(self, adjLst, startPt, goalPt):
        self.adjLst = adjLst
        closest = adjLst[0].selfInd
        closestG = adjLst[0].selfInd
        for i in adjLst:
            dist = getDistance(startPt, i.getCenter())
            distG = getDistance(goalPt, i.getCenter())

            if dist < getDistance(adjLst[closest].getCenter(), startPt):
                closest = i.selfInd

            if distG < getDistance(adjLst[closestG].getCenter(), goalPt):
                closestG = i.selfInd

        self.start = adjLst[closest]
        self.start.g = 0
        self.start.f = 0
        self.goal = adjLst[closestG]
        self.open = PriorityQueue()
        self.open.put(self.start, 0)
        self.closed = dict()
        self.closed[str(self.start.selfInd)] = self.start
        self.curr = self.start
        self.bestPath = None
        self.bestPathDist = 10000

    def AStar(self):
        while not self.open.empty():
            n = self.open.get()

            if n == self.goal:
                break

            for chld in n.getNaybs():
                sChl = str(chld)
                h = self.adjLst[chld].getDistanceToCentersOrPoint(self.goal)
                g = n.g + self.adjLst[chld].getDistanceToCentersOrPoint(n)  # self.calculateG(chld)
                f = h + g
                if sChl not in self.closed or f < self.closed[sChl].f:
                    self.closed[sChl] = self.adjLst[chld]
                    self.closed[sChl].f = f
                    self.closed[sChl].g = g
                    self.closed[sChl].par = n.selfInd
                    self.open.put(self.adjLst[chld], f)

        path = self.makeChannel(self.goal, self.adjLst[self.goal.par])

        return path

    def calculateG(self, chld, n):

        print ("calculateG not implemented")


    def makeChannel(self, end, nextN, start=None):
        """Takes the end of a channel of triangles and creates lists of Right and Left points that lead through the channel"""
        if start is None:
            start = self.start  # TODO: handle and arbitrary point as the startPt
        for nayb in end.getNaybs():
            if nayb in nextN.getNaybs():
                p = end.getSharedPoints(nextN)
                return [end, nextN]
        print "make channel"
        # TODO: handle an arbitrary point as the goal
        # remake end to we can steer it to the nextN node
        # end = AdjLstElement(tuple((end.tri[0], end.tri[1], end.tri[2]))
        #                     , end.selfInd, end.n12, end.n23, end.n13)
        end = copyAdjLstElement(end)
        for ii in range(0, 3):
            if end.tri[ii] not in end.getSharedPoints(nextN):
                end.tri[ii] = end.getCenter()  # set the center as the goal point
                goalPt = end.tri[ii]  # used to put the goal at the end of both rightVec and leftVec point lists
        end.par = nextN.selfInd
        channel = [end]

        curr = nextN
        # TODO: create special triangles for the goal and startPt
        # make a channel out of the list of adjacency indexes
        while curr != start:
            # copy the adj triangles out so we can strip references to non-channel triangle without messing of the map
            cpy = copyAdjLstElement(self.closed[str(curr.selfInd)])
            channel.append(cpy)
            currKey = str(curr.selfInd)
            parKey = str(self.closed[currKey].par)
            curr = self.closed[parKey]

        # cpy is a copy of the startPt
        # make the special case triangle for the startPt
        cpyInd = str(self.start.selfInd)
        cpy = copyAdjLstElement(self.closed[cpyInd])
        channel.append(cpy)
        channel = list(reversed(channel))
        shrdPts = channel[0].getSharedPoints(channel[1])

        print "\n"
        for c in channel:
            print c
        print "\n"
        ################### PUT THIS IN A FUNCTION
        # get the starting point so we can figure out which shared point goes on the Right and which the leftVec
        for p in range(0, 3):
            # the point not shared between the first two triangles is the starting point
            if channel[0].tri[p] not in shrdPts:
                stPt = channel[0].tri[p]
                l = getLeftPt(stPt, shrdPts)
                # get the rightVec point
                for z in shrdPts:
                    if z != l:
                        r = z
                        break
                break
        leftPts = [l]
        rightPts = [r]
        # make the list of leftVec and rightVec points
        for i in range(0, len(channel) - 1):
            side, vecToNxt, nxtPt = self.getNextVec(i, channel)
            if side == "rightVec":
                rightPts.append(nxtPt)
            else:
                leftPts.append(nxtPt)

        if rightPts[len(rightPts) - 1] != goalPt:
            rightPts.append(goalPt)
        if leftPts[len(leftPts) - 1] != goalPt:
            leftPts.append(goalPt)

        print "\nLEFT", leftPts
        print "RIGHT", rightPts, "\n"
        ################################# PUT THE ABOVE IN A FUNCTION
        path = self.newFunnel2(stPt, goalPt, leftPts, rightPts)
        print path, "startPt goal", stPt, goalPt
        # return channel
        return path

    def newFunnel2(self, startPt, goalPt, leftPts, rightPts):
        """creates a true path out of the given funnel and returns the points and length"""
        def isDistSmall(a, b):
            tol = 0.0001*0.0001
            cX = a.x - b.x
            cY = a.y - b.y
            return math.sqrt(cX*cX + cY*cY) < tol
        print "\n\n\n\n"  # ###################################### PRINT PRINT PRINT
        pathPts = []
        lInd = 0
        rInd = 0
        funnVec = FunVecs(startPt,
                          leftPts[0] - startPt, leftPts[0],
                          rightPts[0] - startPt, rightPts[0])
        print "LEFT", leftPts
        print "RIGHT", rightPts
        print funnVec
        lPoint = rPoint = None

        while lPoint != goalPt and rPoint != goalPt:  # lInd < len(leftPts) - 1 or rInd < len(rightPts) - 1:
            neitherUpdated = True
            rPoint = rightPts[rInd]
            lPoint = leftPts[lInd]
            print "\n\nrPoint", rPoint, "  lPoint", lPoint
            # hold if the next point on the rightVec is outside the funnel but not crossing the leftVec
            if funnVec.right.cross(rPoint - funnVec.start).z >= 0:
                print " rightVec good"
                # update if we didn't cross the leftVec. If we did cross the leftVec, restart the funnel
                if isDistSmall(funnVec.rPt, rPoint) or funnVec.left.cross(rPoint - funnVec.start).z <= 0:
                    print " rightVec still good", rPoint
                    # the next rightVec is still in the funnel
                    funnVec.updateRight(rPoint)
                    rInd += 1
                    neitherUpdated = False
                else:  # we've crossed the leftVec side. Restart the funnel
                    # the leftVec side is a corner
                    print "rightVec not good"
                    # update only if the leftVec side is as tight as it can be
                    if funnVec.left.cross(lPoint - funnVec.start).z <= 0:
                        pathPts.append(funnVec.lPt)
                        funnVec.start = funnVec.lPt
                        funnVec.updateLeft(lPoint)
                        lPoint = lPoint
                        lInd += 1
                        neitherUpdated = False

            print "funVecs1", funnVec

            if funnVec.left.cross(lPoint - funnVec.start).z <= 0:
                print " leftVec good"
                # update if we didn't cross the rightVec. If we did cross the rightVec, restart the funnel
                if isDistSmall(funnVec.lPt, lPoint) or funnVec.right.cross(lPoint - funnVec.start).z >= 0:
                    print " leftVec still good", lPoint
                    # the next rightVec is still in the funnel
                    funnVec.updateLeft(lPoint)
                    lInd += 1
                    neitherUpdated = False
                else:  # we've crossed the rightVec side. Restart the funnel
                    # the rightVec side is a corner
                    print " leftVec not good"
                    # update only if the other side is as tight as it can be
                    if funnVec.right.cross(rPoint - funnVec.start).z >= 0:
                        pathPts.append(funnVec.rPt)
                        funnVec.start = funnVec.rPt
                        funnVec.updateRight(rightPts[rInd])
                        rInd += 1
                        neitherUpdated = False
            print "funVecs2", funnVec
            print "PATH", pathPts
            if neitherUpdated:
                # process both sides until one crosses the other or the goal is reached
                leftCrossed = rightCrossed = False
                for r in range(rInd, len(rightPts)):
                    rSeekVec = rightPts[r] - funnVec.start
                    if funnVec.left.cross(rSeekVec).z > 0:
                        print "r found", rightPts[r]
                        rightCrossed = True
                        break

                for l in range(lInd, len(leftPts)):
                    lSeekVec = leftPts[l] - funnVec.start
                    if funnVec.right.cross(lSeekVec).z < 0:
                        print "l found", leftPts[l]
                        leftCrossed = True
                        break




                if leftCrossed and rightCrossed:
                    # take the with either the least difference in indexes (lSeekInd - lInd)
                    # or the one that traveled the least distance (not sure which one yet)
                    print "\nRIGHT AND LEFT CROSSED ######################################\n"
                elif rightCrossed:
                    # reset the rightVec side to the one that crossed the leftVec sid
                    print "rightCrossed append", funnVec.lPt
                    rInd = r
                    funnVec.updateRight(rightPts[rInd])
                    pathPts.append(funnVec.lPt)  # reset startPt and leftVec normally
                    funnVec.start = funnVec.lPt
                    funnVec.updateLeft(leftPts[lInd])
                    #lPoint = leftPts[lInd]
                    #lInd += 1
                elif leftCrossed:
                    print "leftCrossed append", funnVec.rPt
                    lInd = l
                    funnVec.updateLeft(leftPts[lInd])
                    pathPts.append(funnVec.rPt)
                    funnVec.start = funnVec.rPt
                    funnVec.updateRight(rightPts[rInd])
                    #rPoint = rightPts[rInd]
                    #rInd += 1
                print "updated", funnVec

        if rInd + 1 < len(rightPts):
            rInd += 1
        if lInd + 1 < len(leftPts):
            lInd += 1
        print "\n\n\nlast stab"
        print "###############################end funVecs1\n", funnVec
        print "PATH", pathPts
        if rPoint == goalPt:
            print " rightVec = goal"
            # update if we didn't cross the leftVec. If we did cross the leftVec, restart the funnel
            if isDistSmall(funnVec.rPt, rPoint) or funnVec.left.cross(rPoint - funnVec.start).z <= 0:
                print " rightVec still good", rPoint
                pathPts.append(rPoint)  # append the goal
                return pathPts
            else:  # we've crossed the leftVec side. add leftVec
                # the leftVec side is a corner
                print "rightVec not good"
                pathPts.append(funnVec.lPt)
                pathPts.append(goalPt)
                return pathPts
        else:  # leftVec == goal
            if isDistSmall(funnVec.rPt, lPoint) or funnVec.right.cross(lPoint - funnVec.start).z >= 0:
                print " leftVec = goal", lPoint
                pathPts.append(lPoint)  # append the goal
                return pathPts
            else:  # we've crossed the leftVec side. add leftVec
                # the rightVec side is a corner
                print "leftVec not good"
                pathPts.append(funnVec.rPt)
                pathPts.append(lPoint)
                return pathPts

        # if funnVec.leftVec.cross(lPoint - funnVec.startPt).z <= 0:
        #     print " leftVec good"
        #     # update if we didn't cross the rightVec. If we did cross the rightVec, restart the funnel
        #     if isDistSmall(funnVec.lPt, lPoint) or funnVec.rightVec.cross(lPoint - funnVec.startPt).z >= 0:
        #         print " leftVec still good", lPoint
        #         pass
        #     else:  # we've crossed the rightVec side. Restart the funnel
        #         # the rightVec side is a corner
        #         print " leftVec not good"
        #         pathPts.append(funnVec.rPt)
        #
        # print "end funVecs2", funnVec


    def funnelNew(self, channel):
        """creates a true path out of the given funnel and returns the points and length"""
        def isDistSmall(a, b):
            tol = 0.0001*0.0001
            cX = a.x - b.x
            cY = a.y - b.y
            return math.sqrt(cX*cX + cY*cY) < tol

        # pick the starting point and the starting leftVec and rightVec
        start = channel[0]
        second = channel[1]
        funVecs = self.makeFunVecs(start, second)
        apexTriangles = []
        pathPts = [funVecs.start]
        # run funnel algorithm
        i = 0
        while i < len(channel) - 1:

            side, vecToNxt, nxtPt = self.getNextVec(i, channel)
            if side == "leftVec":
                # if the point is outside on the leftVec hold, else the next point is to the rightVec of the leftVec side
                #if funVecs.rightVec.cross(vecToNxt).z >= 0:
                if funVecs.left.cross(vecToNxt).z <= 0:  # 1 don't update if the next vert is outside the funnel
                    print "leftVec good"
                    # if the next point is to the leftVec of the rightVec side
                    # it's still inside the funnel, update the leftVec vector
                    #if isDistSmall(funVecs.startPt, nxtPt) or funVecs.leftVec.cross(vecToNxt).z <= 0:
                    if isDistSmall(funVecs.start, nxtPt) or funVecs.right.cross(vecToNxt).z >= 0:  # 2
                        print "leftVec still good"
                        funVecs.updateLeft(nxtPt)
                    else:  # if we've crossed the rightVec we need a new point for startPt (apex)
                        print "fail cross R", funVecs.right.cross(vecToNxt), " L ", funVecs.left.cross(vecToNxt).z
                        # set the rightVec point as the new startPt
                        funVecs.start = funVecs.rPt
                        pathPts.append(funVecs.rPt)
                        # set the rightVec vec to point to the rightVec point in this triangle and the leftVec to the leftVec
                        sharedPts = channel[i].getSharedPoints(channel[i + 1])
                        print "append***** rPt", funVecs.rPt, "shared", sharedPts, "\ni", channel[i], "\ni+1", channel[i + 1]
                        midPt = getCenterOfPoint3s(sharedPts)
                        midVec = midPt - funVecs.start
                        # if mid cross the fist point is poss then the first pt is on the leftVec
                        # if midVec.cross(sharedPts[0] - funVecs.startPt).z >= 0:
                        if getLeftPt(funVecs.start, sharedPts) == sharedPts[0]:
                            funVecs.updateLeft(sharedPts[0])
                            funVecs.updateRight(sharedPts[1])
                        else:  # its the other way around
                            funVecs.updateLeft(sharedPts[1])
                            funVecs.updateRight(sharedPts[0])

                        #i -= 1  # restart at this triangle
            else:  # side == "rightVec
                # 1 don't update if the next vert is outside the funnel on the rightVec
                #if funVecs.leftVec.cross(vecToNxt).z <= 0:
                if funVecs.right.cross(vecToNxt).z >= 0:
                    print "rightVec good"
                    # make sure it didn't cross the leftVec side
                    #if isDistSmall(funVecs.startPt, nxtPt) or funVecs.rightVec.cross(vecToNxt).z >= 0:
                    if isDistSmall(funVecs.start, nxtPt) or funVecs.left.cross(vecToNxt).z <= 0:  # 2
                        funVecs.updateRight(nxtPt)
                        print "still good"#, funVecs, " LL  cross ", funVecs.getCross(), "    i ", i
                    else:  # if we've crossed the leftVec we need a new point for startPt (apex)
                        print "fail cross R", funVecs.right.cross(vecToNxt), " L ", funVecs.left.cross(vecToNxt)
                        # do the same as above but for the leftVec
                        funVecs.start = funVecs.lPt
                        pathPts.append(funVecs.lPt)
                        # set the rightVec vec to point to the rightVec point in this triangle and the leftVec to the leftVec
                        sharedPts = channel[i].getSharedPoints(channel[i + 1])
                        print "append***** ", funVecs.lPt, "shared", sharedPts, "\ni", channel[i], "\ni+1", channel[i + 1]
                        midPt = getCenterOfPoint3s(sharedPts)
                        midVec = midPt - funVecs.start
                        # if mid cross the fist point is poss then the first pt is on the leftVec
                        # if midVec.cross(sharedPts[0] - funVecs.startPt).z >= 0:
                        if getLeftPt(funVecs.start, sharedPts) == sharedPts[0]:
                            funVecs.updateLeft(sharedPts[0])
                            funVecs.updateRight(sharedPts[1])
                        else:  # its the other way around
                            funVecs.updateLeft(sharedPts[1])
                            funVecs.updateRight(sharedPts[0])

                        #i -= 1  # restart at this triangle
            print "funVecs", funVecs, "\n"
            i += 1

        print pathPts
        return None

    def getNextVec(self, i, channel):
        # the edge is the edge on channel[i + 1] NOT i
        edge = getSharedEdgeStr(channel[i + 1], channel[i])
        # find which point in the next triangle isn't also in this triangle
        # then get it's vector and a vector to the edge's mid point so we can figure out what side the pt is on
        print "getNextVec\n", channel[i + 1], "\n", channel[i]
        if edge == "12":  # the new point is either the 1st or second point in the triangle
            # check the other edges to get the one that leads out of i + 1
            # get the vec to it's midpoint
            if channel[i + 1].n23 is not None and self.adjLst[channel[i + 1].n23] in channel:
                vecToMid = getCenterOfPoint3s([channel[i + 1].tri[1], channel[i + 1].tri[2]])\
                            - channel[i].getCenter()
            else:  # it's the other edge
                vecToMid = getCenterOfPoint3s([channel[i + 1].tri[0], channel[i + 1].tri[2]])\
                            - channel[i].getCenter()
            vecToNxt = channel[i + 1].tri[2] - channel[i].getCenter()

        elif edge == "23":  # check the second edge in like fashion
            if channel[i + 1].n12 is not None and self.adjLst[channel[i + 1].n12] in channel:
                vecToMid = getCenterOfPoint3s([channel[i + 1].tri[0], channel[i + 1].tri[1]])\
                            - channel[i].getCenter()
            else:  # it's the other edge
                vecToMid = getCenterOfPoint3s([channel[i + 1].tri[0], channel[i + 1].tri[2]])\
                            - channel[i].getCenter()
            vecToNxt = channel[i + 1].tri[0] - channel[i].getCenter()
        else:  # edge == "13" the new point must be in this edge
            if channel[i + 1].n12 is not None and self.adjLst[channel[i + 1].n12] in channel:
                vecToMid = getCenterOfPoint3s([channel[i + 1].tri[0], channel[i + 1].tri[1]])\
                            - channel[i].getCenter()
            else:  # it's the other edge
                vecToMid = getCenterOfPoint3s([channel[i + 1].tri[1], channel[i + 1].tri[2]])\
                            - channel[i].getCenter()

            vecToNxt = channel[i + 1].tri[1] - channel[i].getCenter()

        if vecToNxt.cross(vecToMid).z >= 0:
            # print "rightVec", channel[i].selfInd, vecToMid, vecToNxt, "next",\
            #     channel[i].getCenter().x + vecToNxt.x, channel[i].getCenter().y + vecToNxt.y
            return ["rightVec", vecToNxt, Point3( channel[i].getCenter().x + vecToNxt.x,
                                              channel[i].getCenter().y + vecToNxt.y,
                                              channel[i].getCenter().z + vecToNxt.z)]
        else:
            # print "leftVec", channel[i].selfInd, vecToMid, vecToNxt, "next",\
            #     channel[i].getCenter().x + vecToNxt.x, channel[i].getCenter().y + vecToNxt.y
            return ["leftVec", vecToNxt, Point3( channel[i].getCenter().x + vecToNxt.x,
                                              channel[i].getCenter().y + vecToNxt.y,
                                              channel[i].getCenter().z + vecToNxt.z)]

    def funnelIter(self, startInd, channel, funVecs, pathPts):
        # http://digestingduck.blogspot.com/2010/03/simple-stupid-funnel-algorithm.html
        # http://gamedev.stackexchange.com/questions/68302/how-does-the-simple-stupid-funnel-algorithm-work
        # http://paper.ijcsns.org/07_book/201212/20121208.pdf
        def isDistSmall(a, b):
            tol = 0.0001*0.0001
            cX = a.x - b.x
            cY = a.y - b.y
            return math.sqrt(cX*cX + cY*cY) < tol

        i = startInd + 1  # need to compare points in the nex triangle to decide which  gets updated
        leftOrRightFailed = "none"
        while leftOrRightFailed == "none" and i < len(channel) - 1:
            neitherUpdated = True
            shrd = channel[i].getSharedPoints(channel[i - 1])
            nxtTri = channel[i]
            print "nxtTri", nxtTri
            if nxtTri.isConstrained(funVecs.rPt):  # comments are where the leftVec is handled (below the rightVec's code)
                for p in nxtTri.tri:
                    if p not in shrd:
                        print "r check p =", p
                        newVec = Vec3(p - funVecs.start)
                        if funVecs.right.cross(newVec).z >= 0:  # ### 1
                            print "rightVec good"
                            if isDistSmall(funVecs.start, p) or funVecs.left.cross(newVec).z <= 0:  # ### 2 crossed over leftVec

                                neitherUpdated = False
                                funVecs.updateRight(p)
                                # print channel[i - 1]
                                print "still good", funVecs, " RR  cross  ", funVecs.getCross(), "    i ", i
                            else:  # we've crossed the other side and need a new apex (startPt)
                                print "fail crossed L R=", funVecs.right.cross(newVec), " L ", funVecs.left.cross(newVec).z
                                leftOrRightFailed = "rightVec"  # if we've crossed the other side STOP
                                pathPts.append(funVecs.lPt)
                                funVecs.start = funVecs.lPt
                                funVecs.updateRight(p)
                                funVecs.left = Vec3(0.0)
                                # otherPts = nxtTri.getOppositePoints(funVecs.lPt)
                                #funVecs.reset(funVecs.lPt, otherPts[0], otherPts[1])

                                print "append **** lNormal", funVecs.lPt
                                break

            if leftOrRightFailed != "none":  # if we've crossed the other side STOP
                print "break r i=", i
                break

            if nxtTri.isConstrained(funVecs.lPt):
                for p in nxtTri.tri:
                    if p not in shrd:
                        print "l check p =", p
                        newVec = Vec3(p - funVecs.start)
                        if funVecs.left.cross(newVec).z <= 0:  # 1 don't update if the next vert is outside the funnel
                            print "leftVec good"
                            if isDistSmall(funVecs.start, p) or funVecs.right.cross(newVec).z >= 0:  # 2

                                neitherUpdated = False
                                funVecs.updateLeft(p)
                                # print channel[i - 1]
                                print "still good", funVecs, " LL  cross ", funVecs.getCross(), "    i ", i
                            else:  # if we've crossed the rightVec we need a new point for startPt (apex)
                                print "fail cross R", funVecs.right.cross(newVec), " L ", funVecs.left.cross(newVec).z
                                leftOrRightFailed = "leftVec"  # if we've crossed the other side STOP
                                pathPts.append(funVecs.rPt)
                                funVecs.start = funVecs.rPt
                                funVecs.updateLeft(p)
                                funVecs.right = Vec3(0.0)
                                # otherPts = nxtTri.getOppositePoints(funVecs.rPt)
                                # funVecs.reset(funVecs.rPt, otherPts[0], otherPts[1])
                                print "append***** rNormal", funVecs.rPt
                                break


            if leftOrRightFailed != "none":  # if we've crossed the other side STOP
                print "break l i = ", i
                break

            # on one side the next point is outside the funnel and the other side is constrained
            if neitherUpdated:  # if we didn't update one side or the other STOP
                print "neither updated", funVecs.left.cross(newVec).z, funVecs.right.cross(newVec).z
                lookAheadTri = channel[i + 1]
                edgeOut = nxtTri.getSharedPoints(lookAheadTri)
                for laPt in lookAheadTri.tri:
                    if laPt not in edgeOut:
                        oppositePt = laPt
                        newVec = oppositePt - funVecs.start
                # rightVec side is constrained see if it opposing pt crosses the leftVec
                if nxtTri.isConstrained(funVecs.rPt):
                    print "r constrained"
                    # we're turning rightVec. So, we need this corner.
                    # They don't update whenever the constrained side is outside of the funnel
                    if not lookAheadTri.isConstrained(funVecs.lPt):
                        print "append***** r", funVecs.rPt
                        pathPts.append(funVecs.rPt)
                        otherPts = nxtTri.getOppositePoints(funVecs.rPt)
                        funVecs.reset(funVecs.rPt, otherPts[0], otherPts[1])
                    else:  # we aren't going to turn this direction so we can widen the funnel (toss this point out)
                        funVecs.updateRight(oppositePt)
                        print "update r oppPt=", oppositePt, "fun vec", funVecs

                elif nxtTri.isConstrained(funVecs.lPt):
                    print "l constrained"
                    if not lookAheadTri.isConstrained(funVecs.rPt):
                        pathPts.append(funVecs.lPt)
                        otherPts = nxtTri.getOppositePoints(funVecs.lPt)
                        funVecs.reset(funVecs.lPt, otherPts[0], otherPts[1])
                        print "append***** l", funVecs.rPt
                    else:  # we aren't going to turn this direction so we can widen the funnel (toss this point out)
                        funVecs.updateLeft(oppositePt)
                        print "update r oppPt=", oppositePt, "fun vec", funVecs
                # print

                # Region Used when the calling function puts in the pathPts. (not working)
                # # if neither updated, the point that's not in the next triangle
                # # needs to become the next apex (funVec.startPt).
                # # we change the funVec in funnel()
                # if funVecs.rPt not in edgeOut:
                #     leftOrRightFailed = "rightVec"
                # else:
                #     leftOrRightFailed = "leftVec"
                # break
                # Endregion

            print "i end", i, "funVecs", funVecs, "\n__________________________________________"
            i += 1

        print "end Iter leftOrRight", leftOrRightFailed + "\n"
        print "i", i, "len", len(channel), "chan i", channel[i], "\nfunVecs ", funVecs

        return [leftOrRightFailed, i, funVecs, pathPts]

    def makeFunVecs(self, start, second):
        shared = start.getSharedPoints(second)
        for i in start.tri:
            if i not in shared:
                startPt = i
        left = Vec3(shared[0] - startPt)
        lpt = shared[0]
        right = Vec3(shared[1] - startPt)
        rpt = shared[1]
        # if these are on the wrong side switch them
        # print "startPt", startPt  #, " mid - startPt ", getCenterOfPoint3s(shared)
        mid = getCenterOfPoint3s(shared) - startPt
        # print "mid", mid, midP, " leftVec - mid ", lpt-mid, shared, leftVec
        if left.cross(mid).z > 0.0:  #(leftVec - mid).y >= 0.0:
            print "swap"
            tmp = left
            left = right
            right = tmp

            tmp = lpt
            lpt = rpt
            rpt = tmp
        funVec = FunVecs(startPt, left, lpt, right, rpt)
        print "make funner ", funVec
        return funVec

    def isIn(self, ind, lst):
        for p in lst:
            if p.selfInd == ind:
                return True

        return False

    def __str__(self):
        sr = "TAStar:\nstartPt: " + str(self.start.selfInd) +\
            "\ngoal: " + str(self.goal.selfInd) +\
            "\ncurr: " + str(self.curr) +\
            "\nopen: " + str(self.open) +\
            "\nclosed: " + str(self.closed)
        return sr


if __name__ == '__main__':
    app = TriangulationAStar()