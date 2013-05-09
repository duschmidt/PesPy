from Colormap import colorMap


class statusEnum:
    NotOpen = 0
    IOError = 1
    ParseError = 2
    Ready = 3
class Point:
    def __init__(self,x=0,y=0):
        self.x = x
        self.y = y
class stitchBlock:
    def __init__(self):
        self.color = (0,0,0);
        self.colorIndex = 0
        self.stitchesTotal = 0
        self.stitches = []

    def __str__(self):
        s = "StichBlock \n\tcolor:%s\n\tstitchCount:%d\n\t"%(str(self.color),self.stitchesTotal)
        return s

    def getPoints(self, translate=Point()):
        pts = []
        for s in self.stitches:
            pts.append(s.x+translate.x)
            pts.append(s.y+translate.y)
        return pts


class intPair:
    def __init__(self,a=0,b=0):
        self.a = a
        self.b = b



def readInt(bytes, fileIn):
    return int.from_bytes(fileIn.read(bytes), 'little')

def validateFile(fileIn):
    fileIn.seek(0)
    startFileSig = fileIn.read(8).decode()

    if not startFileSig[0:4] == "#PES": #can't read
        print("Missing #PES")
        return False
    else:
        return True

def getColors(fileIn,pecstart):
    fileIn.seek(pecstart+48) #go to num colors
    colorCount = int.from_bytes(fileIn.read(1),'little') +1
    colorList = []
    for i in range(colorCount):
        colorList.append(int.from_bytes(fileIn.read(1),'little'))
    return colorList

def getStitchBlocks(fileIn, pecstart):
    colorList = getColors(fileIn, pecstart)
    fileIn.seek(pecstart + 532)
    thisPartDone = False
    curBlock = stitchBlock()
    prevX = 0
    prevY = 0
    maxX = 0
    minX = 0
    maxY = 0
    minY = 0
    colorNum = -1
    colorindex = 0
    tempStitches = []
    blocks = []
    translateStart = Point()
    while not thisPartDone:
        val1 = readInt(1,fileIn)
        val2 = readInt(1,fileIn)
        if val1 == 255 and val2 == 0:
            #print("end of stiches")
            thisPartDone = True
            curBlock = stitchBlock()
            curBlock.stitches = list(tempStitches)
            curBlock.stitchesTotal = len(tempStitches)
            colorNum += 1
            colorIndex = colorList[colorNum]
            curBlock.colorIndex = colorIndex
            curBlock.color = colorMap[colorIndex]
            blocks.append(curBlock)
        elif val1 == 254 and val2 == 176:
            #print("color switch")
            curBlock = stitchBlock()
            curBlock.stitches = list(tempStitches)
            curBlock.stitchesTotal = len(tempStitches)
            colorNum += 1
            colorIndex = colorList[colorNum]
            curBlock.colorIndex = colorIndex
            curBlock.color = colorMap[colorIndex]
            blocks.append(curBlock)
            tempStitches = []
            fileIn.read(1)
        else:
            #print("regular")
            deltaX = 0
            deltaY = 0
            if (val1 & 128) == 128:
                #print("jump stitch")
                deltaX = ((val1 & 15) * 256) + val2
                if ((deltaX & 2048) == 2048) :
                    deltaX = deltaX - 4096
                val2 = readInt(1,fileIn)
            else:
                #print("normal stitch")
                deltaX = val1
                if (deltaX > 63):
                    deltaX = deltaX - 128

            if ((val2 & 128) == 128):
                #print("jump stitch")
                val3 = readInt(1,fileIn)
                deltaY = ((val2 & 15) * 256) + val3
                if ((deltaY & 2048) == 2048):
                    deltaY = deltaY - 4096
            else:
                #print("normal stitch")
                deltaY = val2
                if (deltaY > 63):
                    deltaY = deltaY - 128
            tempStitches.append(Point(prevX+deltaX,prevY+deltaY))
            prevX = prevX + deltaX
            prevY = prevY + deltaY
            maxX = max(maxX, prevX)
            minX = min(minX, prevX)
            maxY = max(maxY, prevY)
            minY = min(minY, prevY)
            imageWidth = maxX - minX
            imageHeight = maxY - minY
            translateStart.x = -minX
            translateStart.y = -minY
    return {'blocks':blocks,'minX':minX,'maxX':maxX,'minY':minY,'maxY':maxY,'translateStart':translateStart}

def loadPESFile(filename):
    _fileName = filename
    fileIn = open(_fileName,'rb')

    if not validateFile(fileIn):
        print("Invalid File")

    else:
        print("Valid file")

    pecstart =readInt(4,fileIn)
    colors = getColors(fileIn,pecstart)
    blocks = getStitchBlocks(fileIn,pecstart)
    return {'colors':colors, 'blockData':blocks}

