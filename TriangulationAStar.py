__author__ = 'Lab Hatter'


from Queue import PriorityQueue
from panda3d.core import Vec3, Point3
from PolygonUtils.PolygonUtils import getDistance, getAngleXYVecs
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
        funler = self.makeFunVecs(start, second)
        self.funnelIter(0, channel, funler)

        return channel


    def funnelIter(self, startInd, channel, funVecs):
        # http://digestingduck.blogspot.com/2010/03/simple-stupid-funnel-algorithm.html
        # http://gamedev.stackexchange.com/questions/68302/how-does-the-simple-stupid-funnel-algorithm-work

        lstCross = funVecs.getCross()
        i = startInd + 1  # need to compare points in the nex triangle to decide which  gets updated
        needBreak = False
        while not needBreak and i < len(channel) and not funVecs.needNewApex():
            shrd = channel[i].getSharedPoints(channel[i - 1])
            nxtTri = channel[i]
            if funVecs.rPt in nxtTri.tri and nxtTri.isConstrained(funVecs.rPt):

                for p in nxtTri.tri:
                    if p not in shrd:
                        print "r check"
                        #if funVecs.area(funVecs.rPt, p)
                        newVec = Vec3(p - funVecs.start)
                        ang = getAngleXYVecs(newVec, funVecs.right)
                        # print "angle", ang
                        # print " vecs ", funVecs.right, newVec, newVec.angleDeg(funVecs.right)
                        # if funVecs.right.cross(newVec).z >= 0:# or\
                        if funVecs.left.cross(newVec).z <= 0:
                            # ang < 2:
                            print "right cross new", funVecs.right.cross(newVec)
                            # if funVecs.left.cross(newVec).z <= 0:
                            if funVecs.right.cross(newVec).z >= 0:
                                funVecs.updateRight(p)
                                print channel[i - 1]
                                print funVecs, " RR  cross  ", funVecs.getCross(), "    i ", i
                            else:  # we've crossed the other side and need a new apex (start)
                                print "fail cross R", funVecs.right.cross(newVec), " L ", funVecs.left.cross(newVec).z
                                needBreak = True
                                break

            if needBreak:
                print "break r"
                break

            if funVecs.lPt in nxtTri.tri and nxtTri.isConstrained(funVecs.lPt):
                for p in nxtTri.tri:
                    if p not in shrd:
                        print "l check"
                        newVec = Vec3(p - funVecs.start)
                        ang = getAngleXYVecs(funVecs.left, newVec)
                        # print "angle", ang
                        # print " vecs ", funVecs.left, newVec
                        # if funVecs.left.cross(newVec).z <= 0:# or\
                        if funVecs.right.cross(newVec).z >= 0:

                                # ang < 2:
                            # if funVecs.right.cross(newVec).z >= 0:
                            if funVecs.left.cross(newVec).z <= 0:
                                # if the next left makes a wider funnel hold this point
                                print "old cross ", lstCross, "left cross new", funVecs.left.cross(newVec)
                                funVecs.updateLeft(p)
                                print channel[i - 1]
                                print funVecs, " LL  cross ", funVecs.getCross(), "    i ", i
                            else:# if we've crossed the right we need a new point for start (apex)
                                print "fail cross R", funVecs.right.cross(newVec), " L ", funVecs.left.cross(newVec).z
                                needBreak = True
                                break

            if needBreak:
                print "break l i = ", i
                break

            print i, needBreak
            lstCross = funVecs.getCross()
            i += 1

        print "end Iter\n"
        print "i", i, len(channel), channel[i], "\nfunVecs ", funVecs
        return [i, funVecs]


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
        if left.cross(right) <= 0.0:
            tmp = left
            left = right
            right = tmp

            tmp = lpt
            lpt = rpt
            rpt = tmp
        print "make funner ", FunVecs(startPt, left, lpt, right, rpt)
        return FunVecs(startPt, left, lpt, right, rpt)

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