from struct import pack
import re
import math
import BMPConstants

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
    
    def __encodePixelArray(self,width,height,MCUs):
        MCUdim = MCUs[0][0].dim
        MCUWidth = math.ceil(width / MCUdim)
        MCUHeight = math.ceil(height / MCUdim)
        #BMP files have rows that must be a multiple of 4 thus we my need some padding at the end of each row
        paddingLen = width % 4
        #note MCUs are dimxdim blocks and BMP stores pixels by full rows
        #bottom up
        for i in range(MCUHeight,0,-1):
            #MCUs are 8x8 or 16x16
            MCURow = math.floor(i / MCUdim)
            #Row of pixels within current MCU block
            pixelRow = i % MCUdim
            for j in range(0,MCUWidth,1):
                MCUCol = math.floor(i / MCUdim)
                #Col of pixels within current MCU block
                pixelCol = j % MCUdim
                #print(f"MCUROW: {MCURow}\nMCUCOL: {MCUCol}\npixelRow: {pixelRow}\npixelCol: {pixelCol}\n")
                self.bmpFile.write(pack('B',MCUs[MCURow][MCUCol].b[pixelRow][pixelCol]))
                self.offset += 1
                self.bmpFile.write(pack('B',MCUs[MCURow][MCUCol].g[pixelRow][pixelCol]))
                self.offset += 1
                self.bmpFile.write(pack('B',MCUs[MCURow][MCUCol].r[pixelRow][pixelCol]))
                self.offset += 1
            #add padding to end of each row if needed
            for j in range(paddingLen):
                self.bmpFile.write(pack('B',0))
                self.offset += 1



    def __init__(self,file,width,height,numColorChannels,MCUs):
        regex = re.compile("[^.]*")
        filename = regex.search(file).group()
        
        #If we are encoding we want to create a BMP file
        self.bmpFile = open(f"{filename}.bmp", 'wb')
        if self.bmpFile == None:
            print(f"Error! Cannot create bmp file with name {filename}")
            exit(0)

        self.offset = 0
        self.__encodeHeader(width,height,numColorChannels)
        self.__encodePixelArray(width,height,MCUs)
        self.bmpFile.close()

