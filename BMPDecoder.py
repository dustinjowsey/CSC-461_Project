import BMPConstants

class BMPDecoder():
    #**WILL NEED WORK TO ALLOW FOR PIXELS WITH <8 BITS PER PIXEL IE NEED BITSTREAM
    def _decodeImage(self, width, height, data):
        decodedData = []

        #NOTE WE DO NOT ALLOW FOR ALPHA CHANNEL VALUES< STRICTLY 24 BITS PER PIXEL
        #bitmap image data starts at bottom left hand corner of the image
        offset = 0
        for y in range(height, 0, -1):
            for x in range(0, width, 1):
                #R
                decodedData.append(unpack(BMPConstants.UCHAR, data[offset:offset+1])[0])
                offset += 1
                #G
                decodedData.append(unpack(BMPConstants.UCHAR, data[offset:offset+1])[0])
                offset += 1
                #B
                decodedData.append(unpack(BMPConstants.UCHAR, data[offset:offset+1])[0])
                offset += 1
        
        return decodedData

    def __init__(self, filename):
        print("*Beginning BMP Decoding*")
        try:
            f = open(filename, "rb")
        except FileExistsError as e:
            print(f"Error! caught {type(e)}: {e}")
        data = f.read()

        offset = 0
        #always length 14
        bmpHeader = BMPConstants.BMPHeader(data[0:14])
        self.width = bmpHeader.getWidth()
        self.height = bmpHeader.getHeight()

        #For now we only need to support 3 color channels
        self.numColorChannels = 3

        dibHeaderLen = unpack(BMPConstants.UINT, data[14:18])[0]
        dibHeader = BMPConstants.DIBHeader(dibHeaderLen, data[14:14+dibHeaderLen])

        print("*Decoding Image Data*")
        decodedData = self._decodeImage(self.width, self.height, data[bmpHeader.imageOffset:])
        self.data = decodedData
        print("*Finished Decoding BMP File*")