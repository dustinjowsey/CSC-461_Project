from struct import pack
import re
import math
from constants import BMPConstants

class BMPEncoder:

    def __encodeHeader(self,width,height,numColorChannels):
        #Begin writing the header.
        #ID 2 bytes long
        self.bmpFile.write(pack('B',0x42))
        self.offset += 1
        self.bmpFile.write(pack('B',0x4D))
        self.offset += 1

        #Size of BMP file 4 bytes long (including header length which is always 14 bytes long)
        paddingLen = width % 4
        #Size is 14 bytes for BMP Header + 16 for DIB header + height x width x number of color channels + Number of padding bytes x height
        #*** Assuming DIB Header is of length 16 for simplicity *** need to fix in future
        size = 14 + 16 + (width * height * numColorChannels) + (paddingLen * height)
        self.bmpFile.write(pack('<L',size))
        self.offset += 4

        #Unused 2 bytes long
        self.bmpFile.write(pack('<H',0))
        self.offset += 2

        #Unused 2 bytes long
        self.bmpFile.write(pack('<H',0))
        self.offset += 2

        #Offset where the bitmap data begins 4 bytes long (end of header?)
        #*** We assumed DIB header to length 16 *** so 14 + 16 = 30
        self.bmpFile.write(pack('<L',30))
        self.offset += 4

        #DIB header
        #Number of bytes in the DIB header 4 bytes long
        #*** Assumed to be 16 for simplicity ***
        self.bmpFile.write(pack('<L',16))
        self.offset += 4

        #Width of bitmap in pixels 4 bytes long
        self.bmpFile.write(pack('<L',width))
        self.offset += 4

        #Height of bitmap in pixels 4 bytes long
        self.bmpFile.write(pack('<L',height))
        self.offset += 4

        #Number of color planes 2 bytes long
        #Must be 1
        self.bmpFile.write(pack('<H',1))
        self.offset += 2

        #Number of bits per pixel 2 bytes long
        #We have 8 bits per color so 24 bits per pixel
        self.bmpFile.write(pack('<H',24))
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
        return None
    
    def __writeData(self, data, width, height, numColorChannels):
        #We only support true color with no alpha with 8 bits per pixel so we need to add padding
        maxX = numColorChannels*width
        maxY = height

        #BMP is stored from bottom row up
        for y in range(maxY, 0, -1):
            count = 0
            for x in range(0, maxX, numColorChannels):
                index = (y * maxX) + x
                self.bmpFile.write(data[index:index+numColorChannels])
                count += 1
            #add padding to row
            if(count % 4 != 0):
                for i in range(count % 4):
                    self.bmpFile.write(0x00)

    def __init__(self,filename,width,height,numColorChannels,data):
        regex = re.compile("[^.]*")
        filename = regex.search(filename).group()
        
        #If we are encoding we want to create a BMP file
        self.bmpFile = open(f"{filename}.bmp", 'wb')
        if self.bmpFile == None:
            print(f"Error! Cannot create bmp file with name {filename}")
            exit(0)

        self.offset = 0
        self.__encodeHeader(width, height, numColorChannels)
        self.__writeData(data, width, height, numColorChannels)
        self.bmpFile.close()

