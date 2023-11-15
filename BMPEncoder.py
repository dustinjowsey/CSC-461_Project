import struct

class BMP:
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

    def __decodeBMP(self):
        pass

    def __encodeDIBHeader(self):
        #DIB header
        #Number of bytes in the DIB header 4 bytes long
        self.bmpFile.pack(self.offset,0x00000000)
        self.offset += 4

        #Width of bitmap in pixels 4 bytes long
        self.bmpFile.write(self.offset,0x00000000)
        self.offset += 4

        #Height of bitmap in pixels 4 bytes long
        self.bmpFile.write(self.offset,0x00000000)
        self.offset += 4

        #Number of color planes 2 bytes long
        #Must be 1
        self.bmpFile.write(self.offset,0x0001)
        self.offset += 2

        #Number of bits per pixel 2 bytes long
        #We have 8 bits per color so 24 bits per pixel
        self.bmpFile.write(self.offset,0x0018)
        self.offset += 2

        return None
        #** ASSUMING THIS IS WHERE THE HEADER ENDS FOR SIMPLICITY **

        #Pixel array compression being used 4 bytes long
        self.bmpFile.write(self.offset,0x00000000)
        self.offset += 2

        #Size of bitmap data (includes padding) 4 bytes long
        self.bmpFile.write(self.offset,0x00000000)
        self.offset += 4

        #Horizontal resolution of image (pixels/metre) 4 bytes long
        self.bmpFile.write(self.offset,0x00000000)
        self.offset += 4

        #Vertical resolution of image (pixels/metre) 4 bytes long
        self.bmpFile.write(self.offset,0x00000000)
        self.offset += 4

        #Number of colors in the palette 4 bytes long
        self.bmpFile.write(self.offset,0x00000000)
        self.offset += 4

        #Important colors (0 means all colors are important) 4 bytes long
        self.bmpFile.write(self.offset,0x00000000)
        self.offset += 4

    def __encodeBMPHeader(self):
        #Begin writing the header.
        #ID 2 bytes long
        struct.pack_into('<B',self.bmpFile,self.offset,'B')
        self.offset += 1
        struct.pack_into('<B',self.bmpFile,self.offset,'M')
        self.offset += 1

        #Size of BMP file 4 bytes long (including header length which is always 14 bytes long)
        #Size is 14 bytes for BMP Header + 12 for + height x width x number of color planes + Number of padding bytes x height
        size = 14 + 12 
        self.bmpFile.write(self.offset,0x00000000)
        self.offset += 4

        #Unused 2 bytes long
        self.bmpFile.write(self.offset,0x0000)
        self.offset += 2

        #Unused 2 bytes long
        self.bmpFile.write(self.offset,0x0000)
        self.offset += 2

        #Offset where the bitmap data begins 4 bytes long (end of header?)
        self.bmpFile.write(self.offset,0x00000000)
        self.offset += 4
        
        return None

    def encodeBMP(self):
        self.__encodeBMPHeader()
        self.__encodeDIBHeader()
        pass
        

    def __init__(self, encode=True):
        #If we are encoding we want to create a BMP file
        if(encode):
            self.bmpFile = open("bmp.bmp", 'wb')
            self.offset = 0
