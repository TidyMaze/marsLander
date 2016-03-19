import tkinter
import tkinter.messagebox
import math
import random
import time
import cProfile

width = 1200
height = 700
GRAV = 3.711
POD_RADIUS = 5
MAX_VSPEED_LANDING = 40
MAX_HSPEED_LANDING = 20

class State:
    def __init__(self):
        self.pod = None
        self.history = []

    def __str__(self):
        return 'state [ pod : ' + str(self.pod) +', history : ' + str(self.history) + ' ]'

class TurnAction:
    def __init__(self, rotate, power):
        self.rotate = rotate
        self.power = power

class Pod:
    """ un acteur d'un joueur """
    def __init__(self):
        self.position = None
        self.speed = Vector(0,0)
        self.angle = 0
        self.power = 0
        self.fuel = 0
    def __str__(self):
        return 'position : ' + str(self.position) + ', speed : ' + str(self.speed) + ', angle : ' + str(self.angle) + ', fuel : ' + str(self.fuel)

class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    def __str__(self):
        return '('+str("%.2f" % self.x)+','+str("%.2f" % self.y)+')'
    def add(self, obj2D):
        return Vector(self.x + obj2D.x, self.y + obj2D.y)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __str__(self):
        return '('+str("%.0f" % self.x)+','+str("%.0f" % self.y)+')'
    def apply(self, vector):
        return Point(self.x + vector.x, self.y + vector.y)

class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __str__(self):
        return 'Line('+str(self.p1) + ' - ' + str(self.p2)+')'
    def __repr__(self):
        return str(self)

class Segment:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
    def __str__(self):
        return 'Line('+str(self.p1) + ' - ' + str(self.p2)+')'
    def __repr__(self):
        return str(self)

def drawCircle(canvas, x, y, radius, color):
    canvas.create_oval(x-radius, y-radius, x+radius, y+radius, outline=color, tag='moving')

def drawPod(canvas, pod, color):
    drawCircle(canvas, pod.position.x, pod.position.y, POD_RADIUS, color)
    canvas.create_line(pod.position.x, pod.position.y, pod.position.x + math.cos(math.radians(pod.angle))*POD_RADIUS, pod.position.y + math.sin(math.radians(pod.angle))*POD_RADIUS, fill=color, tag='moving')

def coordsToLines(listCoords):
    res = []
    for i in range(len(listCoords))[1:]:
        res.append(Line(Point(listCoords[i-1][0], listCoords[i-1][1]), Point(listCoords[i][0], listCoords[i][1])))
    return res

def drawLandscape(canvas, reliefCoords):
    print('relief : ', reliefCoords)
    lines = coordsToLines(reliefCoords)
    drawMultiLines(canvas, lines, 'brown')

def drawMultiLines(canvas, lines, color):
    for line in lines:
        canvas.create_line(line.p1.x, line.p1.y, line.p2.x, line.p2.y, fill = color)

def intersectionLines(l1, l2):
    x1 = l1.p1.x; y1 = l1.p1.y
    x2 = l1.p2.x; y2 = l1.p2.y
    x3 = l2.p1.x; y3 = l2.p1.y
    x4 = l2.p2.x; y4 = l2.p2.y
    if (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) == 0:
        return None
    return (((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4 - y3*x4))/((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)),
    ((x1*y2-y1*x2)*(y3-y4) - (y1-y2)*(x3*y4 - y3*x4))/((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)))

def inRangeSorted(val, val1, val2):
    if val1 <= val2:
        return inRange(val, val1, val2)
    else:
        return inRange(val, val2, val1)

def inRange(val, min, max):
    return val >= min and val <= max

def intersectionSegments(s1, s2):
    pInter = intersectionLines(s1,s2)
    if pInter is None:
        return False
    return inRangeSorted(pInter[0], s1.p1.x, s1.p2.x) and inRangeSorted(pInter[0], s2.p1.x, s2.p2.x) and inRangeSorted(pInter[1], s1.p1.y, s1.p2.y) and inRangeSorted(pInter[1], s2.p1.y, s2.p2.y)

def updateGame(state, angle, power):
    vectorThrust = Vector(math.cos(math.radians(angle))*power, math.sin(math.radians(angle))*power)
    #print('thrust acc : ', vectorThrust)
    acceleration = Vector(0, -GRAV).add(vectorThrust)
    newState = State()
    newState.pod = Pod()
    newState.pod.angle = angle
    newState.pod.power = power
    newState.pod.speed = state.pod.speed.add(acceleration)
    newState.pod.position = state.pod.position.apply(newState.pod.speed)
    newState.pod.fuel = state.pod.fuel - power
    newState.history = list(state.history)
    newState.history.append((angle,power))
    return newState

def isFlat(line):
    return line.p1.y == line.p2.y

def lastMove(pod):
    return Segment(pod.position,  pod.position.apply(Vector(-pod.speed.x, -pod.speed.y)))

def lastMoveInCollisionWithNotFlatLine(state, line):
    pod = state.pod
    last = lastMove(pod)
    inter = intersectionSegments(last,line)
    coliNotFlat = inter and not isFlat(line)
    """
    if coliNotFlat:
        print('collision entre ', lastMove, ' and ', line)
    """
    return coliNotFlat

def lastMoveInCollisionWithFlatLine(state, line):
    pod = state.pod
    last = lastMove(pod)
    inter = intersectionSegments(last,line)
    coliFlat = inter and isFlat(line)
    if coliFlat:
        print('.',end='')
        #print('collision flat entre ', lastMove, ' and ', line)
    return coliFlat

def empty(list):
    return len(list) == 0

def collisionWithNotFlatMountain(state, mountainLines):
    functionLastMoveCollision = lambda line : lastMoveInCollisionWithNotFlatLine(state, line)
    for line in mountainLines:
        if functionLastMoveCollision(line):
            return True
    return False

def collisionWithFlatMountain(state, mountainLines):
    functionLastMoveCollision = lambda line : lastMoveInCollisionWithFlatLine(state, line)
    for line in mountainLines:
        if functionLastMoveCollision(line):
            return True
    return False

def inBoundaries(point):
    return inRangeSorted(point.x, 0, width) \
        and inRangeSorted(point.y, 0, height)

def lost(state, mountainLines):
    return not inBoundaries(state.pod.position) \
        or collisionWithNotFlatMountain(state, mountainLines)

def podSpeedCanLand(pod):
    return abs(pod.speed.y) <= MAX_VSPEED_LANDING \
        and abs(pod.speed.x) <= MAX_HSPEED_LANDING

def win(state, mountainLines):
    return podSpeedCanLand(state.pod) and \
        collisionWithFlatMountain(state, mountainLines)# \
        #and round(state.pod.angle) == 90

def showMove(canvas, state, pod, mountainLines):
    #canvas.delete("moving")
    sTemp = State()
    sTemp.pod = pod
    path = []
    index = 0
    while True :
        #print('index:',index,', history:', state.history)
        sTemp = updateGame(sTemp, state.history[index][0], state.history[index][1])
        path.append((sTemp.pod.position.x, sTemp.pod.position.y))

        if podSpeedCanLand(sTemp.pod):
            drawPod(canvas,sTemp.pod, 'green')
        else:
            """drawPod(canvas,sTemp.pod, 'red')"""
        index += 1
        if lost(sTemp, mountainLines) or win(sTemp, mountainLines):
            break;

    drawPod(canvas,state.pod, 'white')
    drawMultiLines(canvas, coordsToLines(path), 'blue')

def startSimu(pod, mountainLines):
    s = State()
    s.pod = pod

    while not lost(s, mountainLines) and not win(s, mountainLines):
        power = min(s.pod.fuel,random.randint(max(0,s.pod.power-1),min(s.pod.power+1,4)))
        angle = min(180,max(0, random.randint(s.pod.angle-15,s.pod.angle+15)))
        s = updateGame(s, angle, power)

    return (s, win(s, mountainLines))

def computeCoordinates(relief):
    nbPoints = len(relief)
    widthOfALine = width / (nbPoints-1)
    return list(map(lambda x, y : (x,y), map(lambda x: widthOfALine * x, range(nbPoints)), relief))

def main():
    relief = [600,100,200,300,300,600]
    coordinates = computeCoordinates(relief)
    createWindow(coordinates)

def findAndShow(mountainLines, canvas):
    found=0
    pod = Pod()
    pod.position = Point(300, 300)
    pod.speed = Vector(0,0)
    pod.angle = 90
    pod.fuel = 500
    pod.power = 3
    while found<1:
        res = startSimu(pod, mountainLines)
        s = res[0]
        if res[1]:
            found += 1
            print('final state : ', s)
            showMove(canvas, s, pod, mountainLines)


def createWindow(coordinates):
    top = tkinter.Tk()
    canvas = tkinter.Canvas(top, bg="black", height=height, width=width)
    drawLandscape(canvas, coordinates)
    canvas.pack()
    mountainLines = coordsToLines(coordinates)
    start_time = time.time()
    findAndShow(mountainLines, canvas)
    print('')
    print('time : ', time.time() - start_time)
    top.mainloop()

main()
