from struct import unpack

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
BKGD = 0
#Chromaticity Coordinates
CHRM = 0
#Digital Signatures
DSIG = 0
#Exif Metadata
EXIF = 0
#Gamma
GAMA = 0
#Histogram/Total Amount of Each Color in the Image
HIST = 0
#ICC Color Profile
ICCP = 0
#Compression Encodings
ITXT = 0
#Pixel Size/Pixel Aspect Ratio
PHYS = 0
#Color Accuracy of Source Data
SBIT = 0
#Palette to Use if Full Range of Colors is Unavailable
SPLT = 0
#Indicates RGB is Being Used
SRGB = 0
#Stero Image Indicator
STER = 0
#Text
TEXT = 0
#Time Image Was Last Changed
TIME = 0
#Transparency Information
TRNS = 0
#Compressed Text
ZTXT = 0

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
class Chunk():
    def __eq__(self, __value: object) -> bool:
        if(self.type == __value):
            return True
        else:
            return False
    
    #Will return the size of the data chunk (excludes 12 bytes for length type and crc)
    def __sizeof__(self) -> int:
        return self.length

    def __init__(self, length, type):
        self.length = length
        self.type = type

class Header(Chunk):
    def __init__(self, data, crc, length = 13, type = IHDR):
        super().__init__(length, type)
        if(length != 13):
            raise CorruptPNGError(f"Header length must be 13, but recieved: {length}")

        self.length = length
        #Image width in pixels is 4 bytes long
        self.width = unpack(UINT, data[0:4])[0]
        #Image height in pixels is 4 bytes long
        self.height = unpack(UINT, data[4:8])[0]
        #Bit depth 1 byte long
        self.bitDepth = unpack("B",data[8:9])[0]
        if(self.bitDepth != 1 & self.bitDepth != 2 & self.bitDepth != 4 & self.bitDepth != 8 & self.bitDepth != 16):
            raise CorruptPNGError(f"Invalid bit depth, recieved in header: {self.bitDepth}") 
        
        #Color type 1 byte long
        self.colorType = unpack("B",data[9:10])[0]
        if(self.colorType != 0 & self.colorType != 2 & self.colorType != 3 & self.colorType != 4 & self.colorType != 6):
            raise CorruptPNGError(f"Invalid color type, recieved in header: {self.colorType}")
            
        #Compression method 1 byte long, must be 0
        self.compressionMethod = unpack("B",data[10:11])[0]
        if(self.compressionMethod != 0):
            raise CorruptPNGError(f"Invalid compression method in header, recieved: {self.compressionMethod}")

        #Filter method 1 byte long, must be 0
        self.filterMethod = unpack("B",data[11:12])[0]
        if(self.filterMethod != 0):
            raise CorruptPNGError(f"Invalid filter method in header, recieved {self.filterMethod}")
            
        #Interlace method, 1 byte long. 0 is no interlace, 1 is interlace
        self.interlaceMethod = unpack("B",data[12:13])[0]
        if(self.interlaceMethod != 0 & self.interlaceMethod != 1):
            raise CorruptPNGError(f"Invalid interlace method in header, recieved {self.interlaceMethod}")

        return None

class Palette(Chunk):
    def __init__(self, length, data, crc, type = PLTE):
        super().__init__(length, type)


