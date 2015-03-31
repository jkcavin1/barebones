__author__ = 'Lab Hatter'


import math
from Queue import PriorityQueue
from panda3d.core import Vec3, Point3, LineSegs
from PolygonUtils.PolygonUtils import getDistance, getAngleXYVecs, getCenterOfPoint3s, getLeftPt
from PolygonUtils.AdjacencyList import AdjLstElement, copyAdjLstElement, getEdgeStr


class FunVecs(object):
    def __init__(self, start, left, lPt, right, rPt):
        self.startPt = start
        self.leftVec = left
        self.lPt = lPt
        self.rightVec = right
        self.rPt = rPt

    def getCross(self):
        return self.leftVec.cross(self.rightVec)

    def updateLeft(self, newPt):
        self.lPt = newPt
        self.leftVec = Vec3(newPt - self.startPt)

    def updateRight(self, newPt):
        self.rPt = newPt
        self.rightVec = Vec3(newPt - self.startPt)

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
        self.startPt = start
        self.leftVec = left
        self.rightVec = right
        self.rPt = rpt
        self.lPt = lpt
        print "reset", self

    def needNewApex(self):
        return self.getCross().length() <= 0.0


    def area(self, vec1, vec2):
        ax = vec1.x
        ay = self.startPt.y
        bx = vec1.x
        by = vec1.y
        cx = vec2.x
        cy = vec2.y
        return ax * (by - cy) + bx * (cy - ay) + cx * (ay - by)

    def __repr__(self):
        return "< startPt: " + str(self.startPt) +\
               ", leftPt: " + str(self.lPt) +\
               ", rightPt: " + str(self.rPt) #+\
               #", leftVec: " + str(self.leftVec) +\
               #", rightVec: " + str(self.rightVec) +\
               #">"


class TriangulationAStar2(object):
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
        goalPoint = end.getCenter()
        end = copyAdjLstElement(end)
        for ii in range(0, 3):
            if end.tri[ii] not in end.getSharedPoints(nextN):
                end.tri[ii] = end.getCenter()  # set the center as the goal point
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

        print channel[0], "\n", channel[1]
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
        ################################# PUT THE ABOVE IN A FUNCTION
        path = self.funnelNew(channel, goalPoint)
        # return channel
        return path

    def funnelNew(self, channel, goalPt):
        """creates a true path out of the given funnel and returns the points and length"""
        def isDistSmall(a, b):
            tol = 0.0001*0.0001
            cX = a.x - b.x
            cY = a.y - b.y
            return math.sqrt(cX*cX + cY*cY) < tol
        print "\n\n\n\n"
        # pick the starting point and the starting leftVec and rightVec
        start = channel[0]
        second = channel[1]
        funVecs = self.makeFunVecs(start, second)
        apexTriangles = []
        pathPts = [funVecs.startPt]
        # run funnel algorithm
        nxtL = nxtR = Point3(0)
        leftInd = rightInd = i = 0  # TOCHECK: may need to restart using leftVec and rightVec verts
        while i < len(channel) - 1:
            # ERROR have to look at the vertices on the entry edge. Check both of them against the funnel
            sharedPts = channel[i].getSharedPoints(channel[i + 1])
            # if mid cross the fist point is poss then the first pt is on the leftVec
            # if midVec.cross(sharedPts[0] - funVecs.startPt).z >= 0:
            if getLeftPt(channel[i].getCenter(), sharedPts) == sharedPts[0]:
                nxtL = sharedPts[0]
                vecToNxtL = nxtL - funVecs.startPt
                nxtR = sharedPts[1]
                vecToNxtR = nxtR - funVecs.startPt
            else:  # its the other way around
                nxtL = sharedPts[1]
                vecToNxtL = nxtL - funVecs.startPt
                nxtR = sharedPts[0]
                vecToNxtR = nxtR - funVecs.startPt

            print "NEXT TRI", channel[i], "\n", "next L", nxtL, "next R", nxtR

            # if the point is outside on the leftVec hold, else the next point is to the rightVec of the leftVec side
            if funVecs.leftVec.cross(vecToNxtL).z <= 0:  # 1 don't update if the next vert is outside the funnel
                print "leftVec good"
                # if the next point is to the leftVec of the rightVec side
                # it's still inside the funnel, update the leftVec vector
                if isDistSmall(funVecs.startPt, nxtL) or funVecs.rightVec.cross(vecToNxtL).z >= 0:  # 2
                    print "leftVec still good"
                    funVecs.updateLeft(nxtL)
                    leftInd = i
                else:  # if we've crossed the rightVec we need a new point for startPt (apex)
                    print "fail cross R", funVecs.rightVec.cross(vecToNxtL), " L ", funVecs.leftVec.cross(vecToNxtL).z
                    # set the rightVec point as the new startPt
                    funVecs.startPt = funVecs.rPt
                    pathPts.append(funVecs.rPt)
                    print "append***** rPt", funVecs.rPt
                    i = rightInd
                    sharedPts = channel[i].getSharedPoints(channel[i + 1])
                    # if mid cross the fist point is poss then the first pt is on the leftVec
                    # if midVec.cross(sharedPts[0] - funVecs.startPt).z >= 0:
                    if getLeftPt(channel[i].getCenter(), sharedPts) == sharedPts[0]:
                        funVecs.updateLeft(sharedPts[0])
                        funVecs.updateRight(sharedPts[1])
                    else:  # its the other way around
                        funVecs.updateLeft(sharedPts[1])
                        funVecs.updateRight(sharedPts[0])

            print "funVecs1", funVecs, "   i", i

            # 1 don't update if the next vert is outside the funnel on the rightVec
            #if funVecs.leftVec.cross(vecToNxtL).z <= 0:
            if funVecs.rightVec.cross(vecToNxtR).z >= 0:
                print "rightVec good"
                # make sure it didn't cross the leftVec side
                if isDistSmall(funVecs.startPt, nxtR) or funVecs.leftVec.cross(vecToNxtR).z <= 0:  # 2
                    funVecs.updateRight(nxtR)
                    rightInd = i
                    print "still good"#, funVecs, " LL  cross ", funVecs.getCross(), "    i ", i
                else:  # if we've crossed the leftVec we need a new point for startPt (apex)
                    print "fail cross R", funVecs.rightVec.cross(vecToNxtR), " L ", funVecs.leftVec.cross(vecToNxtR)
                    # do the same as above but for the leftVec
                    funVecs.startPt = funVecs.lPt
                    pathPts.append(funVecs.lPt)
                    i = leftInd
                    sharedPts = channel[i].getSharedPoints(channel[i + 1])
                    # if mid cross the fist point is poss then the first pt is on the leftVec
                    # if midVec.cross(sharedPts[0] - funVecs.startPt).z >= 0:
                    if getLeftPt(channel[i].getCenter(), sharedPts) == sharedPts[0]:
                        funVecs.updateLeft(sharedPts[0])
                        funVecs.updateRight(sharedPts[1])
                    else:  # its the other way around
                        funVecs.updateLeft(sharedPts[1])
                        funVecs.updateRight(sharedPts[0])

            print "funVecs2", funVecs, "   i", i
            print "path", pathPts, "\n"
            i += 1

        # ################# AFTER WHILE
        # region Calc last left and rightVec. Shouldn't be needed.
        # sharedPts = channel[i].getSharedPoints(channel[i + 1])
        # # if mid cross the fist point is poss then the first pt is on the leftVec
        # # if midVec.cross(sharedPts[0] - funVecs.startPt).z >= 0:
        # if getLeftPt(channel[i].getCenter(), sharedPts) == sharedPts[0]:
        #     nxtL = sharedPts[0]
        #     vecToNxtL = nxtL - funVecs.startPt
        #     nxtR = sharedPts[1]
        #     vecToNxtR = nxtR - funVecs.startPt
        # else:  # its the other way around
        #     nxtL = sharedPts[1]
        #     vecToNxtL = nxtL - funVecs.startPt
        #     nxtR = sharedPts[0]
        #     vecToNxtR = nxtR - funVecs.startPt
        # endregion

        vecToGoal = goalPt - funVecs.startPt

        print "\n\n############################################\n######################################################"
        print "last rightVec", funVecs.rPt, "last left", funVecs.lPt
        if funVecs.leftVec.cross(vecToGoal).z >= 0:
            print "if goal outside left"
            # if the goal is to the left of the left side, it needs added as a corner.
            # Check the next point on the.
            # if the next point is to the rightVec of the vector pointing from the left to the goal,
            # it needs added as another corner.
            pathPts.append(funVecs.lPt)
            funVecs.startPt = funVecs.lPt
            if leftInd + 2 < len(channel):
                print "if ind check OK"
                # I should check the remaining left side points in a loop, but the map is not jagged so I'll forgo that
                i = leftInd + 1
                sharedPts = channel[i].getSharedPoints(channel[i + 1])
                # if mid cross the fist point is poss then the first pt is on the leftVec
                # if midVec.cross(sharedPts[0] - funVecs.startPt).z >= 0:
                if getLeftPt(channel[i].getCenter(), sharedPts) == sharedPts[0]:
                    funVecs.updateLeft(sharedPts[0])
                else:  # its the other way around
                    funVecs.updateLeft(sharedPts[1])
                vecToGoal = goalPt - funVecs.startPt
                if funVecs.leftVec.cross(vecToGoal).z >= 0:
                    pathPts.append(funVecs.lPt)


        elif funVecs.rightVec.cross(vecToGoal).z <= 0:
            pathPts.append(funVecs.rPt)  # #############  check if the goal is rightVec of the rightVec side
            funVecs.startPt = funVecs.rPt
            print "goal outside right"
            if rightInd + 2 < len(channel):
                print "if ind check ok rightInd = ", rightInd
                # I should check the remaining left side points in a loop, but the map is not jagged so I'll forgo that
                i = rightInd + 1
                sharedPts = channel[i].getSharedPoints(channel[i + 1])
                # if mid cross the fist point is poss then the first pt is on the leftVec
                # if midVec.cross(sharedPts[0] - funVecs.startPt).z >= 0:
                if getLeftPt(channel[i].getCenter(), sharedPts) == sharedPts[0]:
                    funVecs.updateRight(sharedPts[1])
                    print "next rPt", sharedPts[1], " new rPt", funVecs.rPt
                else:  # its the other way around
                    print "next rPt", sharedPts[0], " new rPt", funVecs.rPt
                    funVecs.updateRight(sharedPts[0])
                vecToGoal = goalPt - funVecs.startPt
                if funVecs.rightVec.cross(vecToGoal).z <= 0:
                    print "goal right of new rPt"
                    pathPts.append(funVecs.rPt)

        pathPts.append(goalPt)

        print pathPts
        return pathPts

    def getNextVec(self, i, channel):
        # the edge is the edge on channel[i + 1] NOT i
        edge = getEdgeStr(channel[i + 1], channel[i])
        # find which point in the next triangle isn't also in this triangle
        # then get it's vector and a vector to the edge's mid point so we can figure out what side the pt is on
        # print "getNextVec\n", channel[i + 1], "\n", channel[i]
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