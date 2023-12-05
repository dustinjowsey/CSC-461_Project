from struct import unpack

#Identifiers
BM = 0x424D
BA = 0x4241
CI = 0x4349
CP = 0x4350
IC = 0x4943
PT = 0x5054

#DIB Header Types (determines size of header)
BITMAPCOREHEADER = 12
OS21XBITMAPHEADER = 12
#Can be either 64 or 16, if 16 the size is still 64 but all values beyond the first 16 bytes are 0
OS22XBITMAPHEADER = (64,16)
BITMAPINFOHEADER = 40
BITMAPV2INFOHEADER = 52
BITMAPV3INFOHEADER = 56
BITMAPV4HEADER = 108
BITMAPV5HEADER = 124

#Halftoning Compression Options
NONE = 0
ERRORDIFFUSION = 1
PANDA = 2
SUPER_CIRCLE = 3

#Compression Methods
BI_RGB = 0
BI_RLE8 = 1
BI_RLE4 = 2
BI_BITFIELDS = 3
BI_JPEG = 4
BI_PNG = 5
BI_ALPHABITFIELDS = 6
BI_CMYK = 11
BI_CMYKRLE8 = 12
BI_CMYKRLE4 = 13

#BMP format types for unpack
#Unsigned Char
UCHAR = "B"
#Signed Char
SCHAR = "B"
#Unsigned Short
USHORT = "<H"
#Signed Short
SSHORT = "<h"
#Unsigned Int
UINT = "<I"
#Signed Int
SINT = "<i"
#Unsigned Long Long
ULLONG = "<Q"

class CorruptBMPError(Exception):
    def __init__(self, message):
        super.__init__("Error! Corrupt BMP. " + message)

class BMPHeader():
    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def _encode(self, data):
        pass 
    def _decode(self, data : list):
        if(len(data) != 14):
            raise CorruptBMPError("Header length is less than 14 bytes. should be exactly 14 bytes")

        #BMP header identifier, 2 bytes long
        self.id = unpack(USHORT, data[0:2])[0]
        #only supporting BM format for times sake
        if(self.id != BM):
            raise BMPConstants.CorruptBMPError("Invalid or unsupported bmp format. Currently only supporting BM formats.")
        
        #file size, 4 bytes long
        self.fileLength = unpack(UINT, data[2:6])[0]

        #reserved bytes, 2 bytes long
        self.res1 = unpack(USHORT, data[6:8])[0]

        #reserved bytes, 2 bytes long
        self.res2 = unpack(USHORT, data[8:10])[0]

        #offset where image data starts, 4 bytes long
        self.imageOffset = unpack(UINT, data[10:14])[0]
        return

    def __init__(self, data, encode=True):
        self.id = None
        self.fileLength
        self.res1
        self.res2
        self.imageOffset

        if(encode):
            self._encode(data)
        else:
            self._decode(data)
        return

class DIBHeader():
    def _encode(self, data : list):
        pass

    def _decode(self, data : list):
        #Width in pixels, 4 bytes long
        self.width = unpack(SINT, data[4:8])[0]

        #Height in pixels, 4 bytes long
        self.height = unpack(SINT, data[8:12])[0]

        #Number of color planes, 2 bytes, MUST BE 1
        self.numColPan = unpack(UCHAR, data[12:14])[0]
        if(self.numColPan != 1):
            raise BMPConstants.CorruptBMPError(f"Invalid number of color planes. Must be 1, but recieved {self.numColPan}")

        #Bits per pixel, 2
        self.bitsPerPix = unpack(UCHAR, data[14:16])[0]
        if(self.bitsPerPix != 1 & self.bitsPerPix != 4 & self.bitsPerPix != 8 & self.bitsPerPix != 16 & self.bitsPerPix != 24 & self.bitsPerPix != 32):
            raise BMPConstants.CorruptBMPError(f"Invalid number of bits per pixel. Should be 1,4,8,16,24, or 32, but recieved {self.bitsPerPix}")
        return

    def __init__(self, length, data, encode=True):
        #for simplicity we will assume a length of 16
        if(length != 16):
            raise BMPConstants.CorruptBMPError("Invalid or unsupported DIB header. Currently only supporting 16 byte OS22XBITMAPHEADER")
        self.length = length
        self.width
        self.height
        self.numColPan
        self.bitsPerPix
        #self.compMethod
        #self.imageSize
        #self.horizontalRes
        #self.verticalRes
        #self.numColInPalette
        #self.numImportantColors
        #self.unitsForRes
        #self.padding
        #self.bitmapFillDirection
        #self.halftoningAlg
        #self.halftoningPar1
        #self.halftoningPar2
        #self.colEncoding
        #self.appID
        #EXTRA BIT MASKS IF BITMAPINFOHEADER IS USED WITH BI_BITFIELDS OR BI_ALPHABITFIELDS
        #self.extBitMasks

        if(encode):
            self._encode(data)
        else:
            self._decode(data)
        return

#Right after DIB Header if used
class ColorTable():
    def __init__(self):
        pass

class Gap1():
    def __init__(self):
        pass

class PixelArray():
    def __init__(self):
        pass

class Gap2():
    def __init__(self):
        pass

class ICCColProfile():
    def __init__(self):
        pass
