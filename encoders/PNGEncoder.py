import math
from constants import PNGConstants
import zlib

class PNGEncoder():
    #Need to try every filter option per line of the image 
    #ONLY SUPPORTS RGBA RIGHT NOW
    def _filterData(self, data, pixelWidth, pixelHeight, bytesPerPixel = 4):
        maxX = pixelWidth * bytesPerPixel
        maxY = pixelHeight

        filteredData = []

        for y in range(maxY):
            rowIndex = (y * maxX)

            #Want a score for each filter
            scores = [0,0,0,0,0]
            for i in range(len(scores)):
                for x in range(maxX):
                    match(i):
                        #filter type None
                        case 0:
                            val = data[rowIndex + x]
                        #filter type Sub
                        case 1:
                            val = PNGConstants.filterSub(x, (rowIndex + x), data)
                        #filter type Up
                        case 2:
                            val = PNGConstants.filterUp(x,y,maxX,data)
                        #filter type Average
                        case 3:
                            val = PNGConstants.filterAverage(x,y,(rowIndex + x),maxX,data)
                        #filter type Paeth
                        case 4:
                            val = PNGConstants.filterPaeth(x,y,(rowIndex + x),maxX,data)
                    #want to keep values between -128 and 128
                    if(val >= 128):
                        val = (-128) + (val % 128)
                    scores[i] += abs(val)
            #after getting scored decide best filter type for the row
            lowest = scores[0]
            index = 0
            for j in range(scores):
                if(lowest > scores[j]):
                    lowest = scores[j]
                    index = j
            filteredData.append(index)
            for x in range(maxX):
                match(index):
                    #filter type None
                    case 0:
                        filteredData.append(data[rowIndex + x])
                    #filter type Sub
                    case 1:
                        filteredData.append(PNGConstants.filterSub(x, (rowIndex + x), data))
                    #filter type Up
                    case 2:
                        filteredData.append(PNGConstants.filterUp(x,y,maxX,data))
                    #filter type Average
                    case 3:
                        filteredData.append(PNGConstants.filterAverage(x,y,(rowIndex + x),maxX,data))
                    #filter type Paeth
                    case 4:
                        filteredData.append(PNGConstants.filterPaeth(x,y,(rowIndex + x),maxX,data))
        return filteredData

    def _encodeImage(self, data):
        #* would like to do this myself without zlib
        encodedData = zlib.compress(data)
        return encodedData

    def _buildChunks(self, width, height):
        #Need to begin by building the header chunk
        chunkedData = []
        chunkedData.append(PNGConstants.Header(None, -1, width, height))
        #Skipping palette since we only support truecolor
        #chunkedData.append(PNGConstants.Palette())
        chunkedData.append(PNGConstants.ImageData())
        pass

    def __init__(self, filename, width, height, numColorChannels, rawData):
        #If we are encoding we want to create a PNG file
        self.pngFile = open(f"{filename}.png", 'wb')
        if self.bmpFile == None:
            print(f"Error! Cannot create png file with name {filename}")
            exit(0)
        
        filteredData = self._filterData(rawData, width, height)
        encodedData = self._encodeImage(filteredData)
        self._buildChunks(encodedData)