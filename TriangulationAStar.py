__author__ = 'Lab Hatter'


from Queue import PriorityQueue
from panda3d.core import Vec3, Point3
from PolygonUtils.PolygonUtils import getDistance, getAngleXYVecs, getCenterOfPointsXY
from PolygonUtils.AdjacencyList import AdjLstElement, copyAdjLstElement


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
        return "< start: " + str(self.start) +\
               ", leftPt: " + str(self.lPt) +\
               ", rightPt: " + str(self.rPt) #+\
               #", left: " + str(self.left) +\
               #", right: " + str(self.right) +\
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

        chnl = self.makeChannel(self.goal, self.adjLst[self.goal.par])

        return self.funnel(chnl)

    def calculateG(self, chld, n):

        print ("calculateG not implemented")


    def makeChannel(self, end, nextN, start=None):
        if start is None:
            start = self.start
        for nayb in end.getNaybs():
            if nayb in nextN.getNaybs():
                p = end.getSharedPoints(nextN)
                return [end, nextN]

        # remake end to we can steer it to the nextN node
        end = AdjLstElement(tuple((end.tri[0], end.tri[1], end.tri[2]))
                            , end.selfInd, end.n12, end.n23, end.n13)
        end.par = nextN.selfInd
        path = [end]
        pts = []
        lastShared = end.getSharedPoints(nextN)
        pts.extend(lastShared)
        curr = nextN

        while curr != start:
            cpy = copyAdjLstElement(self.closed[str(curr.selfInd)])
            path.append(cpy)
            currKey = str(curr.selfInd)
            parKey = str(self.closed[currKey].par)
            shrdPts = self.closed[currKey].getSharedPoints(self.closed[parKey])
            pts.append(shrdPts)
            curr = self.closed[parKey]
        cpy = copyAdjLstElement(self.closed[str(self.start.selfInd)])
        path.append(cpy)
        # make not references to triangles outside the channel
        for i in range(0, len(path)):
            if not self.isIn(path[i].n12, path):
                path[i].n12 = None
            if not self.isIn(path[i].n23, path):
                path[i].n23 = None
            if not self.isIn(path[i].n13, path):
                path[i].n13 = None
        path = list(reversed(path))
        pts = list(reversed(pts))

        return path

    def funnel(self, channel):
        # pick the starting point and the starting left and right
        start = channel[0]
        second = channel[1]
        funnler = self.makeFunVecs(start, second)
        apexTriangles = []
        pathPts = [funnler.start]
        i = 0
        while channel[i] != self.goal:
            # [leftOrRightFailed, i, funVecs]
            pack = self.funnelIter(i, channel, funnler)

            print "############## after iter #####################"
            if channel[i] == self.goal:
                break
            i = pack[1]  # get the updated index
            apexTriangles.append(channel[i])  # record this as a triangle where we turned a corner
            funnler = pack[2]
            if channel[i] != self.goal:
                if pack[0] == 'left':  # if it's right make left the new apex
                    print "rPt", funnler.rPt
                    pathPts.append(funnler.rPt)  # record the next path point
                    funnler.start = funnler.rPt
                    pts = channel[i].getSharedPoints(channel[i + 1])
                    print "Shared pts", pts
                    # pick the not equal to left point on the shared edge
                    for k in channel[i + 1].tri:
                        if k not in pts:
                            funnler.updateRight(k)
                    # if funnler.lPt == pts[0]:
                    #     funnler.updateRight(pts[1])
                    # else:
                    #     funnler.updateRight(pts[0])
                elif pack[0] == 'right':
                    print "lPt", funnler.lPt
                    pathPts.append(funnler.lPt)  # record the next path point
                    funnler.start = funnler.lPt
                    pts = channel[i].getSharedPoints(channel[i + 1])
                    print "Shared pts", pts
                    for k in channel[i + 1].tri:
                        if k not in pts:
                            funnler.updateLeft(k)

                    # if funnler.rPt == pts[0]:
                    #     funnler.updateLeft(pts[1])
                    # else:
                    #     funnler.updateLeft(pts[0])
                else:
                    print "ERRROR??? funnel() defaulted left or right = ", pack[0]
                    break


            print "######################## new funnler", funnler

        print "path", pathPts

        return channel


    def funnelIter(self, startInd, channel, funVecs):
        # http://digestingduck.blogspot.com/2010/03/simple-stupid-funnel-algorithm.html
        # http://gamedev.stackexchange.com/questions/68302/how-does-the-simple-stupid-funnel-algorithm-work

        i = startInd + 1  # need to compare points in the nex triangle to decide which  gets updated
        leftOrRightFailed = "none"
        while leftOrRightFailed == "none" and i < len(channel):
            neitherUpdated = True
            shrd = channel[i].getSharedPoints(channel[i - 1])
            nxtTri = channel[i]
            print "nxtTri", nxtTri
            if nxtTri.isConstrained(funVecs.rPt):  # comments are where the left is handled (below the right's code)
                for p in nxtTri.tri:
                    if p not in shrd:
                        print "r check p =", p
                        newVec = Vec3(p - funVecs.start)
                        if funVecs.right.cross(newVec).z >= 0:  #### 1
                            # if funVecs.left.cross(newVec).z <= 0:
                            print "right good"
                            if funVecs.left.cross(newVec).z <= 0:  #### 2 crossed over left
                                # if funVecs.right.cross(newVec).z >= 0:
                                neitherUpdated = False
                                funVecs.updateRight(p)
                                # print channel[i - 1]
                                print funVecs, " RR  cross  ", funVecs.getCross(), "    i ", i
                            else:  # we've crossed the other side and need a new apex (start)
                                print "fail crossed L R=", funVecs.right.cross(newVec), " L ", funVecs.left.cross(newVec).z
                                leftOrRightFailed = "right"  # if we've crossed the other side STOP
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
                            print "left good"
                            if funVecs.right.cross(newVec).z >= 0:  # 2
                                # if funVecs.left.cross(newVec).z <= 0:  # if the next left makes is outside, get new apex
                                neitherUpdated = False
                                funVecs.updateLeft(p)
                                # print channel[i - 1]
                                print funVecs, " LL  cross ", funVecs.getCross(), "    i ", i
                            else:  # if we've crossed the right we need a new point for start (apex)
                                print "fail cross R", funVecs.right.cross(newVec), " L ", funVecs.left.cross(newVec).z
                                leftOrRightFailed = "left"  # if we've crossed the other side STOP
                                break


            if leftOrRightFailed != "none":  # if we've crossed the other side STOP
                print "break l i = ", i
                break

            if neitherUpdated:  # if we didn't update one side or the other STOP
                print "neither updated"
                lookAheadTri = channel[i + 1]
                edgeOut = nxtTri.getSharedPoints(lookAheadTri)
                # if neither updated, the point that's not in the next triangle
                # needs to become the next apex (funVec.start).
                # we change the funVec in funnel()
                if funVecs.rPt not in edgeOut:
                    leftOrRightFailed = "left"
                else:
                    leftOrRightFailed = "right"
                break

            print "i end", i
            i += 1

        print "end Iter leftOrRight", leftOrRightFailed + "\n"
        print "i", i, "len", len(channel), "chan i", channel[i], "\nfunVecs ", funVecs
        return [leftOrRightFailed, i, funVecs]

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
        # print "start", start  #, " mid - start ", getCenterOfPointsXY(shared)
        midP = getCenterOfPointsXY(shared)
        mid = getCenterOfPointsXY(shared) - startPt
        print "mid", mid, midP, " left - mid ", lpt-mid, shared, left
        if (lpt - mid).y >= 0.0:  #(left - mid).y >= 0.0:
            print "swap"
            tmp = left
            left = right
            right = tmp

            tmp = lpt
            lpt = rpt
            rpt = tmp
        funVec = FunVecs(startPt, left, lpt, right, rpt)
        print "make funner ", funVec
        print "  continued", funVec.start, funVec.left, funVec.right
        return funVec

    def isIn(self, ind, lst):
        for p in lst:
            if p.selfInd == ind:
                return True

        return False

    def __str__(self):
        sr = "TAStar:\nstart: " + str(self.start.selfInd) +\
            "\ngoal: " + str(self.goal.selfInd) +\
            "\ncurr: " + str(self.curr) +\
            "\nopen: " + str(self.open) +\
            "\nclosed: " + str(self.closed)
        return sr


if __name__ == '__main__':
    app = TriangulationAStar()