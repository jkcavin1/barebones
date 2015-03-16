__author__ = 'Lab Hatter'

from panda3d.core import Vec3

def HorseShoeCentered():
    """Returns a horseshoe shape, thus behaving like a constructor."""
    hole1 = []
    hole1.append(Vec3(-2, -2, 0))
    hole1.append(Vec3(-1, -2, 0))
    hole1.append(Vec3(-1, .5, 0))
    hole1.append(Vec3(1, .5, 0))
    hole1.append(Vec3(1, -2, 0))
    hole1.append(Vec3(2, -2, 0))
    hole1.append(Vec3(2, 2, 0))
    hole1.append(Vec3(-2, 2, 0))

    return hole1


def SquareOffCenter():
    """Behaves like a constructor by returning a square"""
    hole2 = []
    hole2.append(Vec3(3, 3, 0))
    hole2.append(Vec3(4, 3, 0))
    hole2.append(Vec3(4, 4, 0))
    hole2.append(Vec3(3, 4, 0))
    return hole2


def SquareMap10x10():
    map10 = []
    map10.append(Vec3(-10, -10, 0))
    map10.append(Vec3(10, -10, 0))
    map10.append(Vec3(10, 10, 0))
    map10.append(Vec3(-10, 10, 0))
    return map10

def TheirMap():
    thrMap = []
    thrMap.append(Vec3(-12.0, -12.0, 0.0))
    thrMap.append(Vec3(-3.0, -12.0, 0.0))
    thrMap.append(Vec3(-3.0, -7.0, 0.0))
    thrMap.append(Vec3(3.0, -6.0, 0.0))

    thrMap.append(Vec3(3.0, -12.0, 0.0))

    thrMap.append(Vec3(6.0, -12.0, 0.0))
    thrMap.append(Vec3(6.0, -6.0, 0.0))
    thrMap.append(Vec3(8.0, -7.0, 0.0))

    thrMap.append(Vec3(8.0, -12.0, 0.0))
    thrMap.append(Vec3(12.0, -12.0, 0.0))
    thrMap.append(Vec3(12.0, -4.0, 0.0))
    thrMap.append(Vec3(-3.0, -4.0, 0.0))

    thrMap.append(Vec3(-3.0, -1.0, 0.0))
    thrMap.append(Vec3(12.0, -1.0, 0.0))
    thrMap.append(Vec3(12.0, 12.0, 0.0))
    thrMap.append(Vec3(-12.0, 12.0, 0.0))
    tri1 = []
    tri1.append(Vec3(-5.0, 5.0, 0.0))
    tri1.append(Vec3(1.0, 3.0, 0.0))
    tri1.append(Vec3(-3.0, 9.0, 0.0))
    tri2 = []
    tri2.append(Vec3(4.0, 2.0, 0.0))
    tri2.append(Vec3(8.0, 3.0, 0.0))
    tri2.append(Vec3(8.0, 9.0, 0.0))
    tris = []
    tris.append(tri1)
    tris.append(tri2)

    mapWHoles = []
    mapWHoles.append(thrMap)
    mapWHoles.append(tris)
    #print "mWholes ", mapWHoles
    # for i in mapWHoles:
    #     print "mWholes i", i

    return mapWHoles


if __name__ == '__main__':
    app = TheirMap()