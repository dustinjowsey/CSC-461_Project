from struct import unpack
from struct import pack
from typing import Any
import math
import zlib

#PNG signature
PNGSIG = 0x89504E470D0A1A0A

#Chunk types
#Critical Chunks
#Header
IHDR = 0x49484452
#Palette
PLTE = 0x504C5445
#Image data
IDAT = 0x49444154
#End of image
IEND = 0x49454E44

#Ancillary Chunks
#Default Background Color
BKGD = 0x624B4744
#Chromaticity Coordinates
CHRM = 0x6348524D
#Digital Signatures
DSIG = 0
#Exif Metadata
EXIF = 0
#Gamma
GAMA = 0x67414D41
#Histogram/Total Amount of Each Color in the Image
HIST = 0x67414D41
#ICC Color Profile
ICCP = 0
#Compression Encodings
ITXT = 0
#Pixel Size/Pixel Aspect Ratio
PHYS = 0x70485973
#Color Accuracy of Source Data
SBIT = 0x73424954
#Palette to Use if Full Range of Colors is Unavailable
SPLT = 0
#Indicates RGB is Being Used
SRGB = 0
#Stero Image Indicator
STER = 0
#Text
TEXT = 0x74455874
#Time Image Was Last Changed
TIME = 0x74494D45
#Transparency Information
TRNS = 0x74524E53
#Compressed Text
ZTXT = 0x7A545874

#PNG format types for unpack
#Unsigned Char
UCHAR = "B"
#Unsigned Short
USHORT = ">H"
#Unsigned Int
UINT = ">I"
#Unsigned Long Long
ULLONG = ">Q"

#PNG Errors
class CorruptPNGError(Exception):
    def __init__(self, message) -> None:
        super().__init__("Error! Corrupt PNG. " + message)

#PNG Data Types
#Will need to implement error checking using crc in the future
class Chunk():
    def __eq__(self, __value: object) -> bool:
        if(self.type == __value):
            return True
        else:
            return False
    
    #Will return the size of the data chunk (excludes 12 bytes for length type and crc)
    def __sizeof__(self) -> int:
        return self.length

    def __init__(self, length, type, crc):
        self.length = length
        self.type = type
        self.crc = crc

class Header(Chunk):
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

    def getData(self):
        return self.data

    def getNumColorChannels(self):
        if(self.colorType == 0 | self.colorType == 4):
            return 1
        return 3

    def _encode(self, width, height, interlaceMethod=0):
        if(width == -1 | height == -1):
            print("Error! Attempting to encode without specifying width and height")
            exit(0)
        
        self.data = []
        #length
        self.data.append(pack(PNGConstants.UINT, 13))
        #self.data type
        self.data.append(pack(PNGConstants.UINT, PNGConstants.IDHR))
        #width
        self.data.append(pack(PNGConstants.UINT, width))
        #height
        self.data.append(pack(PNGConstants.UINT, height))
        #bit depth
        #Only supporting bit depth of 8
        self.data.append(pack(PNGConstants.UCHAR, 8))
        #color type
        #only supporting true color
        self.data.append(pack(PNGConstants.UCHAR, 2))
        #Compression method must be 0
        self.data.append(pack(PNGConstants.UCHAR, 0))
        #Filter method must be 0
        self.data.append(pack(PNGConstants.UCHAR, 0))
        #Interlace Method Only supporting no interlace
        self.data.append(pack(PNGConstants.UCHAR, 0))
        return
    
    def _decode(self, data):
        #Image width in pixels is 4 bytes long
        self.width = unpack(UINT, data[0:4])[0]
        #Image height in pixels is 4 bytes long
        self.height = unpack(UINT, data[4:8])[0]
        #Bit depth 1 byte long
        self.bitDepth = unpack(UCHAR,data[8:9])[0]
        if(self.bitDepth != 1 & self.bitDepth != 2 & self.bitDepth != 4 & self.bitDepth != 8 & self.bitDepth != 16):
            raise CorruptPNGError(f"Invalid bit depth, recieved in header: {self.bitDepth}") 
        
        #Color type 1 byte long
        self.colorType = unpack(UCHAR,data[9:10])[0]
        if(self.colorType != 0 & self.colorType != 2 & self.colorType != 3 & self.colorType != 4 & self.colorType != 6):
            raise CorruptPNGError(f"Invalid color type, recieved in header: {self.colorType}")
        
        #Check that the file contains allowed bit types based on the color type
        match(self.colorType):
            #can skip case 0 becuase any bit depth is allowed
            #case 0:
            case 2 | 4 | 6: 
                if(self.bitDepth != 8 & self.bitDepth != 16):
                    raise CorruptPNGError(f"Invalid bit depth for color type. Color type: {self.colorType}, bit depth: {self.bitDepth}")
            case 3:
                if(self.bitDepth != 1 & self.bitDepth != 2 & self.bitDepth != 4 & self.bitDepth != 8):
                    raise CorruptPNGError(f"Invalid bit depth for color type. Color type: {self.colorType}, bit depth: {self.bitDepth}")
            case _:
                #Do nothing
                None

        #Compression method 1 byte long, must be 0
        self.compressionMethod = unpack(UCHAR,data[10:11])[0]
        if(self.compressionMethod != 0):
            raise CorruptPNGError(f"Invalid compression method in header, recieved: {self.compressionMethod}")

        #Filter method 1 byte long, must be 0
        self.filterMethod = unpack(UCHAR,data[11:12])[0]
        if(self.filterMethod != 0):
            raise CorruptPNGError(f"Invalid filter method in header, recieved {self.filterMethod}")
            
        #Interlace method, 1 byte long. 0 is no interlace, 1 is interlace
        self.interlaceMethod = unpack(UCHAR,data[12:13])[0]
        if(self.interlaceMethod != 0 & self.interlaceMethod != 1):
            raise CorruptPNGError(f"Invalid interlace method in header, recieved {self.interlaceMethod}")
        return


    def __init__(self, data=None,  crc=-1, width=-1, height=-1):
        #assume encoding if data is none
        if(data == None):
            self.data = []
            crc = zlib.crc32(self.data)
            self.data.append(crc)
            self._encode(width, height)
            super().__init__(13, IDHR, crc)
        else:
            super().__init__(13, IHDR, crc)
            self.width = 0
            self.height = 0
            self.bitDepth = 0
            self.colorType = 0
            self.compressionMethod = 0
            self.filterMethod = 0
            self.interlaceMethod = 0
            self._decode(data)
        return None

    def __str__(self):
        string = "\nPNG HEADER START"
        string = string
        return string

class Palette(Chunk):
    class Entry():
        def __init__(self, r, g, b) -> None:
            self.r = r
            self.g = g
            self.b = b
        
        def __getitem(self,index) -> int:
            match(index):
                case 0:
                    return self.r
                case 1:
                    return self.g
                case 2:
                    return self.b

    def __init__(self, length, data, crc) -> None:
        if(length % 3 != 0):
            raise CorruptPNGError(f"Invalid pallete. Must be divisible by three to include all rgb values.")
        
        super().__init__(length, PLTE, crc)
        self.entries = []
        offset = 0
        for i in range(0,length,3):
            #1 byte per rgb ranges from 0 to 255
            r = unpack(UCHAR,data[offset:offset+1])[0]
            g = unpack(UCHAR,data[offset+1:offset+2])[0]
            b = unpack(UCHAR,data[offset+2:offset+3])[0]
            if(r < 0 | r > 255 | g < 0 | g > 255 | b < 0 | b > 255):
                raise CorruptPNGError(f"Invalid rgb values for entry (should be between 0 and 255). r: {r}, g: {g}, b: {b}")
            offset += 3
            self.entries.append(self.Entry(r,g,b))

class ImageData(Chunk):
    def _encode(self, length):
        #only supporting Deflate with 256 byte window
        #compressedData = zlib.
        encodedData = []
        pass
    
    def __init__(self, length, data=None, crc=-1):
        #assume encoding if data = none
        if(data == None):
            self.data = []
            self._encode(length)
        else:
            super().__init__(length, IDAT, crc)
            self.data = data
    
    def addChunk(self, chunk):
        if(chunk.type != IDAT):
            raise TypeError(f"Concatenating IDAT with {chunk.type.decode('ASCII')}")
        self.data = self.data + chunk.data
        self.length = self.length + len(chunk.data)

class ImageEnd(Chunk):
    def __init__(self, crc):
        #Has no data, simply used as a marker
        super().__init__(0, IEND, crc)

#Ancillary chunk data types (Not required)
class BackgroundColor(Chunk):
    def __init__(self, length, colorType, bitDepth, data, crc):
        super().__init__(length, BKGD, crc)
        self.palIndex = None
        self.gray = None
        self.r = None
        self.g = None
        self.b = None
        match(colorType):
            case 3:
                #1 byte long
                self.palIndex = unpack(UCHAR, data[0:1])[0]
            case 0 | 4:
                #2 bytes long
                self.gray = unpack(USHORT, data[0:2])[0]
                if(self.gray < 0 | self.gray > (math.pow(2,bitDepth)-1)):
                    print("Warning! Background color out of range, defaulting to white")
                    self.gray = 0
            case 2 | 6:
                self.r = unpack(USHORT, data[0:2])[0]
                self.g = unpack(USHORT, data[2:4])[0]
                self.b = unpack(USHORT, data[4:6])[0]
                maxVal = math.pow(2,bitDepth)-1
                if(self.r < 0 | self.r > maxVal | self.g < 0 | self.g > maxVal | self.b < 0 | self.b > maxVal):
                    print("Warning! Background color out of range, defaulting to white")
                    self.r = maxVal
                    self.g = maxVal
                    self.b = maxVal
        return None


class PrimaryChromaticities(Chunk):
    def __init__(self, length, data, crc):
        super().__init__(length, CHRM, crc)
        #4 bytes long
        self.whitePointX = unpack(UINT, data[0:4])[0]
        #4 bytes long
        self.whitePointY = unpack(UINT, data[4:8])[0]
        #4 bytes long
        self.rX = unpack(UINT, data[8:12])[0]
        #4 bytes long
        self.rY = unpack(UINT, data[12:16])[0]
        #4 bytes long
        self.gX = unpack(UINT, data[16:20])[0]
        #4 bytes long
        self.gY = unpack(UINT, data[20:24])[0]
        #4 bytes long
        self.bX = unpack(UINT, data[24:28])[0]
        #4 bytes long
        self.bY = unpack(UINT, data[28:32])[0]
        return None

class ImageGamma(Chunk):
    def __init__(self, length, data, crc):
        super().__init__(length, GAMA, crc)
        #4 bytes long, gamma is stored as its value x 100000
        self.imageGamma = unpack(UINT, data[0:4])[0]
        return None

class ImageHistogram(Chunk):
    def __init__(self, length, data, crc):
        super().__init__(length, HIST, crc)

class PhysicalPixelDimensions(Chunk):
    def __init__(self, length, data, crc):
        super().__init__(length, PHYS, crc)
        #4 bytes long
        self.pixelsPerUnitX = unpack(UINT, data[0:4])[0]
        #4 bytes long
        self.pixelsPerUnitY = unpack(UINT, data[4:8])[0]
        #1 byte long, can only be 0 (unit is unknown) or 1 (unit is meters)
        self.unit = unpack(UCHAR, data[8:9])[0]
        if(self.unit != 0 & self.unit != 1):
            print("Warning! Invalid unit type for physical pixel dimensions, defualting to unknow")
            self.unit = 0

class SignificantBits(Chunk):
    def __init__(self, length, data, crc):
        super().__init__(length, SBIT, crc)

class TextualData(Chunk):
    def __init__(self, length, data, crc):
        super().__init__(length, TEXT, crc)

class TimeLastModified(Chunk):
    def __init__(self, length, data, crc):
        super().__init__(length, TIME, crc)

class Transparency(Chunk):
    def __init__(self, length, data, crc):
        super().__init__(length, TRNS, crc)

class CompressedTextData(Chunk):
    def __init__(self, length, data, crc):
        super().__init__(length, ZTXT, crc)

#Useful Functions for PNG files
def filterSub(currentCol, currentIndex, data):
    val = 0
    if(currentCol > 0):
        val = data[currentIndex - 1]
    return val

def filterUp(currentCol, currentRow, currentIndex, data):
    val = 0
    if(currentRow > 0):
        val = data[currentIndex - width]
    return val

def filterAverage(currentCol, currentRow, currentIndex, maxCols, data):
    prev = filterSub(currentCol, currentIndex, data)
    up = filterUp(currentCol, currentRow, currentIndex, data)
    return math.floor((prev + up)/2)

def filterPaeth(currentCol, currentRow, currentIndex, maxCols, data):
    prev = filterSub(currentCol, currentIndex, data)
    up = filterUp(currentCol, currentRow, currentIndex, data)
    prevUp = 0
    if(currentCol > 0 & currentRow > 0):
        prevUp = data[(((currentRow-1)*maxCols) + currentCol - 1)]

    paeth = prev + up - prevUp
    distToPrev = abs(paeth - prev)
    distToUp = abs(paeth - up)
    distToPrevUp = abs(paeth - prevUp)

    #Get smallest difference between paeth and prev, up, and prevUp
    if(distToPrev <= distToUp & distToPrev <= distToPrevUp):
        return prev
    elif(distToUp < distToPrev & distToUp < distToPrevUp):
        return up
    else:
        return prevUp