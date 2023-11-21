from struct import unpack
import PNGConstants

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
            match(type):
                case PNGConstants.IDHR:
                    chunks.append(PNGConstants.Header(data[offset:offset+length],data[offset+length:offset+length+4]))
                case PNGConstants.PLTE:
                    chunks.append(PNGConstants.Palette(length, data[offset:offset+length],data[offset+length:offset+length+4]))
                case PNGConstants.IDAT:
                    pass
                case PNGConstants.IEND:
                    pass
            #4 more bytes for crc values
            offset += length
            offset += 4
    
    def __init__(self, filename):
        print("*Beginning PNG Decoding*")
        try:
            f = open(filename, "rb")
        except FileExistsError as e:
            print(f"Error! caught {type(e)}: e")

        offset = 0
        #Need to verify we actually have a png file, first 8 byted will be the PNG signature
        sig = unpack('>Q', f[offset:offset+8])
        offset += 8
        if sig != PNGConstants.PNGSIG:
            print(f"Error! File is not a valid PNG file. Recieved signature {sig}, but should be {PNGSIG}")
            exit(0)
        
        #Header must be the first chunk in the file
        chunks = self.__readChunks(f[8:])
        
