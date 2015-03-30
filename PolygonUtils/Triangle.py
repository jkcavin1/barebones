__author__ = 'Lab Hatter'

from PolygonUtils import getCenterOfPoint3s



def getEdgeStr(triA, triB):
    """Returns the edge that B shares w/ A i.e. If B lies on A's 12 edge, returns '12', otherwise returns '' or '1'"""
    if triA is None or triB is None:
        return ''

    pointsA = triA.getPoints()
    pointsB = triB.getPoints()
    # two matching vertices means their neighbours
    found = ''
    for i in range(0, len(pointsA)):
        if pointsA[i] is not None and pointsA[i] == pointsB[0] or pointsA[i] == pointsB[1] or pointsA[i] == pointsB[2]:
            found = str(i + 1)
            break
    # none match
    if found == '':
        return found

    # now that we found one lets see if there's a second match
    if i + 1 <= len(pointsA):
        for j in range(i + 1, len(pointsA)):
            if pointsA[j] is not None:  # and j != i:
                if pointsA[j] == pointsB[0] or pointsA[j] == pointsB[1] or pointsA[j] == pointsB[2]:
                    found += str(j + 1)
                    return found

    return found


class Triangle(object):
    def __init__(self, pt1, pt2, pt3):
        self.tri = [pt1, pt2, pt3]
        # print "triangle = ", self.tri
        self.pt1 = pt1
        self.pt2 = pt2
        self.pt3 = pt3

    def getTri(self):
        return tuple((self.pt1, self.pt2, self.pt3))

    def getPt1(self):
        return self.tri[0]

    def getPt2(self):
        return self.tri[1]

    def getPt3(self):
        return self.tri[2]

    def getEdge12(self):
        return tuple((self.pt1, self.pt2))

    def getEdge23(self):
        return tuple((self.pt2, self.pt3))

    def getEdge13(self):
        return tuple((self.pt1, self.pt2))

    def getPoints(self):
        return [self.pt1, self.pt2, self.pt3]

    def getCenter(self):
        return getCenterOfPoint3s(self.getPoints())

    # def __str__(self):
    #     return "dmflksdj;fklj"
    #
    # def __repr__(self):
    #     sr = "Tri: < " + self.pt1 + ", " + self.pt2 + ", " + self.pt3 + " >"
    #     return "dmflksdj;fklj"



if __name__ == '__main__':
    app = Triangle()