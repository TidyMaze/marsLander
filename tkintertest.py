import tkinter
import tkinter.messagebox
import math
import random

width = 1200
height = 700
GRAV = 3.711
POD_RADIUS = 25

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
        return 'position : ' + str(self.position) + ', speed : ' + str(self.speed) + ', angle : ' + str(self.angle)

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
    return inRange(val, min(val1,val2), max(val1,val2))

def inRange(val, min, max):
    return val >= min and val <= max

def intersectionSegments(s1, s2):
    pInter = intersectionLines(s1,s2)
    if pInter is None:
        return False
    return inRangeSorted(pInter[0], s1.p1.x, s1.p2.x) and inRangeSorted(pInter[0], s2.p1.x, s2.p2.x) and inRangeSorted(pInter[1], s1.p1.y, s1.p2.y) and inRangeSorted(pInter[1], s2.p1.y, s2.p2.y)

def updateGame(state, angle, power):
    vectorThrust = Vector(math.cos(math.radians(angle))*power, math.sin(math.radians(angle))*power)
    print('thrust acc : ', vectorThrust)
    acceleration = Vector(0, -GRAV).add(vectorThrust)
    newState = State()
    newState.pod = Pod()
    newState.pod.angle = angle
    newState.pod.power = power
    newState.pod.speed = state.pod.speed.add(acceleration)
    newState.pod.position = state.pod.position.apply(newState.pod.speed)
    newState.history = list(state.history)
    newState.history.append((angle,power))
    return newState

def isFlat(line):
    return line.p1.y == line.p2.x

def lastMoveInCollisionWithNotFlatLine(state, line):
    #print('checking collision between ', state, ' and ', line)
    pod = state.pod
    lastMove = Segment(pod.position,  pod.position.apply(Vector(-pod.speed.x, -pod.speed.y)))
    inter = intersectionSegments(lastMove,line)
    coliNotFlat = inter and not isFlat(line)
    if coliNotFlat:
        print('collision entre ', lastMove, ' and ', line)
    return coliNotFlat

def empty(list):
    return len(list) == 0

def collisionWithNotFlatMountain(state, mountainLines):
    functionLastMoveCollision = lambda line : lastMoveInCollisionWithNotFlatLine(state, line)
    return not empty(list(filter(functionLastMoveCollision, mountainLines)))

def inBoundaries(point):
    return inRangeSorted(point.x, 0, width) \
        and inRangeSorted(point.y, 0, height)

def lost(state, mountainLines):
    return not inBoundaries(state.pod.position) \
        or collisionWithNotFlatMountain(state, mountainLines)

def win(state):
    return False

def showMove(canvas, state, pod, mountainLines):
    canvas.delete("moving")
    sTemp = State()
    sTemp.pod = pod
    path = []
    index = 0
    while not lost(sTemp, mountainLines) and not win(sTemp) :
        print('index:',index,', history:', state.history)
        sTemp = updateGame(sTemp, state.history[index][0], state.history[index][1])
        path.append((sTemp.pod.position.x, sTemp.pod.position.y))

        if abs(sTemp.pod.speed.y) <= 40 and abs(sTemp.pod.speed.x) <= 20:
            drawPod(canvas,sTemp.pod, 'green')
        else:
            drawPod(canvas,sTemp.pod, 'red')
        index += 1

    drawPod(canvas,state.pod, 'white')
    drawMultiLines(canvas, coordsToLines(path), 'blue')

def startSimu(pod, mountainLines):
    s = State()
    copy = s
    s.pod = pod

    while not lost(s, mountainLines) and not win(s):
        power = random.randint(max(3,s.pod.power-1),min(s.pod.power+1,4))
        angle = random.randint(s.pod.angle-15,s.pod.angle+15)
        s = updateGame(s, angle, power)

    return s

def computeCoordinates(relief):
    nbPoints = len(relief)
    widthOfALine = width / (nbPoints-1)
    return list(map(lambda x, y : (x,y), map(lambda x: widthOfALine * x, range(nbPoints)), relief))

def main():
    relief = [600,160,100,60,60,200,600]
    coordinates = computeCoordinates(relief)
    createWindow(coordinates)

def createWindow(coordinates):
    top = tkinter.Tk()
    canvas = tkinter.Canvas(top, bg="black", height=height, width=width)
    drawLandscape(canvas, coordinates)
    canvas.pack()
    p = Pod()
    p.position = Point(300, 300)
    p.speed = Vector(0, 0)
    p.angle = 90
    p.fuel = 2000
    p.power = 2
    mountainLines = coordsToLines(coordinates)
    s = startSimu(p, mountainLines)
    showMove(canvas, s, p, mountainLines)
    print('final state : ', s)
    top.mainloop()

main()
