from struct import unpack
import math
import PNGConstants
import zlib

#Note PNG is big Endian
class PNGDecoder():
    def __readChunks(self, data) -> list():
        chunks = []
        type = PNGConstants.IHDR
        offset = 0
        while(type != PNGConstants.IEND):
            if(offset > len(data)):
                raise EOFError(f"Error! read past end of file while reading chunks. offset = {offset}")
            #Each chunk begins with 4 bytes which represent the length, but only includes length of the data field
            length = unpack(PNGConstants.UINT, data[offset:offset + 4])[0]
            offset += 4
            
            #Chunk type is 4 bytes long
            type = unpack(PNGConstants.UINT, data[offset:offset + 4])[0]
            offset += 4
            #*** ONLY CONSIDERING CRITICAL CHUNKS RIGHT NOW ***
            match(type):
                case PNGConstants.IHDR:
                    chunks.append(PNGConstants.Header(data[offset:offset+length],data[offset+length:offset+length+4]))
                case PNGConstants.PLTE:
                    chunks.append(PNGConstants.Palette(length, data[offset:offset+length],data[offset+length:offset+length+4]))
                case PNGConstants.IDAT:
                    chunks.append(PNGConstants.ImageData(length, data[offset:offset+length], data[offset+length:offset+length+4]))
                case PNGConstants.IEND:
                    chunks.append(PNGConstants.ImageEnd(data[offset:offset+4]))
            #4 more bytes for crc values
            offset += length
            offset += 4
        
        return chunks
    
    def __decodeImage(self, header, chunks):        
        pallete = None
        data = PNGConstants.ImageData(0,b'',b'')

        for chunk in chunks:
            match(chunk.type):
                case PNGConstants.PLTE:
                    pallete = chunk
                case PNGConstants.IDAT:
                    data.addChunk(chunk)
        
        #** Want to code this without using zlib library **
        decompressedData = zlib.decompress(data.data)
        return decompressedData

    def __defilterImage(self, header, bytesPerPixel, data):
        maxY = header.height
        maxX = header.width * bytesPerPixel

        defilteredImage = []

        i = 0
        for y in range(maxY):
            #filter option for row
            filter = data[i]
            i += 1
            for x in range(maxX):
                match(filter):
                    #filter type None
                    case 0:
                        val = data[i]
                    #filter type Sub
                    case 1:
                        val = PNGConstants.filterSub(x, i, data)
                    #filter type Up
                    case 2:
                        val = PNGConstants.filterUp(x,y,maxX,data)
                    #filter type Average
                    case 3:
                        val = PNGConstants.filterAverage(x,y,i,maxX,data)
                    #filter type Paeth
                    case 4:
                        val = PNGConstants.filterPaeth(x,y,i,maxX,data)
                defilteredImage.append((data[i] + val) % 256)
                i += 1

        return defilteredImage
    
    def __verifyChunkOrder(self, chunks):
        if(chunks[0] != PNGConstants.IDHR | chunks[1] != PNGConstants.PLTE | chunks[2] != PNGConstants.IDAT | chunks[3] != PNGConstants.IEND):
            raise PNGConstants.CorruptPNGError("Invalid chunk order cannot properly decode image.")

    def __init__(self, filename):
        print("*Beginning PNG Decoding*")
        try:
            f = open(filename, "rb")
        except FileExistsError as e:
            print(f"Error! caught {type(e)}: e")
        data = f.read()

        offset = 0
        #Need to verify we actually have a png file, first 8 byted will be the PNG signature
        sig = unpack(PNGConstants.ULLONG, data[offset:offset+8])[0]
        offset += 8
        if sig != PNGConstants.PNGSIG:
            print(f"Error! File is not a valid PNG file. Recieved signature {sig}, but should be {PNGConstants.PNGSIG}")
            exit(0)
        
        print("*Reading Chunk Data*")
        chunks = self.__readChunks(data[8:])
        #Header must be the first chunk in the file
        if(chunks[0] == None):
            raise PNGConstants.CorruptPNGError("Invalid png format, No chunks were read or found")
        if(chunks[0].type != PNGConstants.IHDR):
            raise PNGConstants.CorruptPNGError("Invalid png format, header should be the first chunk in the file but is not")
        
        header = chunks[0]
        bytesPerPixel = 0
        print("*Decoding Image Data*")
        decodedData = self.__decodeImage(header, chunks)
        print("*Defilitering Image Data*")
        defilteredImage = self.__defilterImage(header, 4, decodedData)
