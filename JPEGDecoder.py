from struct import unpack
import math
from typing import Any
import BMPEncoder

class JPEGDecoder():

    class __bitStream():
        #data is a list of hex values
        def __init__(self, data) -> None:
            self.data = data
            self.len = len(data)*8
            self.pos = 0

        #by default want index to start at pos
        def getBit(self, index = -1):
            if index <= -1:
                index = self.pos
                #lets maintain our position if the user wants to index a specific bit
                self.pos += 1
            #indicates end of stream
            if index >= self.len:
                return -1

            #since we open the file in rb each entry in data is 8 bits long
            chunk = self.data[math.floor(index/8)]
            bit = None
            match index % 8 :
                case 0:
                    bit = (chunk & 0x80) >> 7
                case 1:
                    bit = (chunk & 0x40) >> 6
                case 2:
                    bit = (chunk & 0x20) >> 5
                case 3:
                    bit = (chunk & 0x10) >> 4
                case 4:
                    bit = (chunk & 0x08) >> 3
                case 5: 
                    bit = (chunk & 0x04) >> 2
                case 6:
                    bit = (chunk & 0x02) >> 1
                case 7:
                    bit = chunk & 0x01
                case _:
                    return None
            return bit
        
        def getBits(self,length) -> int:
            bits = 0
            for i in range(length):
                cur = self.getBit()
                if cur == -1:
                    break
                bits = (bits << 1) | cur
            return bits

        #restarts the stream at 0
        def restartStream(self):
            self.pos = 0

        #start stream where you like
        def setStreamStart(self, start):
            if start > self.len:
                print("Error! Start is greater than stream length")
            else:
                self.pos = start

        def isValidBit(self):
            bit = self.getBit(self.pos)
            if bit == -1:
                return False
            else:
                True

        def getLen():
            return self.len

        #will show all bits in the stream
        def show(self, start = 0, end = -1):
            string = ""
            if end == -1:
                end = self.getLen()
            for i in range(start,end,1):
                string = string + str(self.getBit(i))
            print(string)
            return None
        
        #prints first 50 bits then prints length of the stream
        def __str__(self) -> str:
            string = ""
            for i in range(50):
                bit = self.getBit(i)
                if bit == -1:
                    return string
                string = string + str(bit)
            return string + f"... + [{self.len-50}] more bits"


    #data types for JPEG objects

    class __defaultHeader():
        def __init__(self, length, data) -> None:
            self.length = length
            if(length != len(data)):
                print("Error! Invalid data length for Default Header. Cannot process data accuratly.")
                exit(0)

            version = unpack(">H", data[7:9])[0]
            self.version = [version>>8,version & 0xFF]
            self.density = (unpack(">H", data[10:12])[0],unpack(">H", data[12:14])[0])
            self.thumbnail = unpack(">H", data[14:16])[0]
            
        def __str__(self):
            string = f"DEFAULT HEADER\nLength: {self.length}\nVersion: {self.version[0]}.{self.version[1]}\nDensity: {self.density}\nThumbnail: {self.thumbnail}\nEND\n"
            return string

    class __huffmanTable():
        class huffNode():
            def __init__(self, val, left = None, right = None, isSymbol = False):
                self.left = left
                self.right = right
                self.val = val
                self.isSymbol = isSymbol

        class huffTree():
            def __init__(self, root = None):
                self.root = root

        def addOneToBinaryArray(self, curCode):
            i = len(curCode) - 1
            #find rightmost zero
            while(i >= 0):
                if curCode[i] == 0:
                    break
                else:
                    i -= 1

            #if i == 0 then all ones or right most zero is first symbol
            allones = False
            if i == 0:
                if curCode[0] == 0:
                    allones = False
                else:
                    allones = True

            if allones:
                for j in range(len(curCode)):
                    curCode[j] = 0
                curCode.insert(0,1)
            #swap every one after rightmost zero
            else:
                curCode[i] = 1
                for j in range(i+1, len(curCode), 1):
                    curCode[j] = 0
            
            return curCode

        #returns a list of pairs of bit count plus code since codes will be integers
        #for each code of a given length adds the current code to the list and increments the code by 1. 
        #once all the codes of a certain length are found add a 0 to the end (shift left) and repeat
        def createBinaryValues(self):
            codeList = []
            symbolCount = 0
            curCode = [0]
            for i in range(len(self.symbolBitLengths)):
                if(self.symbolBitLengths[i] != 0):
                    for j in range(self.symbolBitLengths[i]):
                        #add bit count, code and symbol to list
                        codeList.append((i+1,curCode,self.symbols[symbolCount]))
                        curCode = curCode.copy()
                        symbolCount = symbolCount + 1
                        curCode = self.addOneToBinaryArray(curCode)
                curCode.append(0)
            return codeList
        
        def createHuffTree(self, codeList):
            root = self.huffNode(None)
            tree = self.huffTree(root)
            cur = root
            for code in codeList:
                cur = root
                for num in code[1]:
                    #go left
                    if num == 0:
                        if cur.left == None:
                            cur.left = self.huffNode(None)
                        cur = cur.left
                    #go right
                    if num == 1:
                        if cur.right == None:
                            cur.right = self.huffNode(None)
                        cur = cur.right
                cur.val = code[2]
                cur.isSymbol = True
            return tree
                    
        def searchHuffTree(self, bitstream):
            cur = self.tree.root
            while(not cur.isSymbol):
                bit = bitstream.getBit()
                if(bit == -1):
                    return None
                #go left
                if bit == 0:
                    if(cur.left == None):
                        return None
                    cur = cur.left
                #go right
                if bit == 1:
                    if(cur.right == None):
                        return None
                    cur = cur.right
            #print()
            return cur.val

        def decodeHuffman(self, stream):
            decodedData = []
            while(stream.isValidBit()):
                val = self.searchHuffTree(stream)
                decodedData.append(val)
            return decodedData

        #Extracts data from a huffman table block used in jpeg file formats
        #length - provide the length of the block (given by hex values at 2-4)
        #data - provide the data of the huffmanTable block beginning at the start of the marker
        def __init__(self, length, data):
            #note length does not include the length of the marker
            self.length = length
            if(length != len(data)):
                print("Error! Invalid data length for 'Huffman Table'. Cannot process data accuratly.")
                exit(0)

            classIdByte = unpack("B", data[2:3])[0]
            #0 = DC For Luminance
            #1 = AC For chrominance
            self.classification = classIdByte >> 4
            #note class must be 0 or 1
            if(self.classification != 0 | self.classification != 1):
                print(f"Error! Invalid classification of huffman table. class should be 0 for DC and 1 for AC, but recieved {self.classification}")
                exit(0)
            #id of table
            self.id = 0x0F & classIdByte
            #note id can only be from 0-3
            if(self.id > 3):
                print(f"Error! Invalid id for huffman table. recieved id value {self.id}")
                exit(0)

            #always length of 16
            self.symbolBitLengths = [unpack("B", data[3 + i:4 + i])[0] for i in range(16)]
            
            self.symbols = [unpack("B",data[19 + i:20 + i])[0] for i in range(length-19)]
            self.codes = self.createBinaryValues()
            self.tree = self.createHuffTree(self.codes)
            return None

        def __str__(self) -> str:
            string = f"\nHUFFMAN TABLE\nMarker = 0xFFC4\nLength = {self.length} hex values (not including 2 values for marker)\nClass = {self.classification}"
            if self.classification == 0:
                string = string + " (DC)"
            else:
                string = string + " (AC)"
            
            string = string + f"\nid = {self.id}\nBit length array = {self.symbolBitLengths}\nSymbols = {self.symbols}\n"
            string = string + f"Code length : binary codes = Symbols:\n"
            for i in range(len(self.codes)):
                temp = ""
                for j in range(len(self.codes[i][1])):
                    temp = temp + str(self.codes[i][1][j])
                string = string + f"    {self.codes[i][0]} : {temp} = {self.codes[i][2]}\n"
            string = string + "END\n"
            return string

    class __quantizationTable():

        def __init__(self, length, data) -> None:
            #note length does not include the marker
            self.length = length
            if(length != len(data)):
                print("Error! Invalid data length for 'Quantization Table'. Cannot process data accuratly.")
                exit(0)

            #id 0 is luminance
            #id 1 is chrominance
            self.id = unpack("B", data[2:3])[0]
            self.tablesize = self.length-3
            if self.id > 3:
                print(f"Invalid Quantization table id: {self.id}")
                exit(0)

            self.table = [None for i in range(64)]
            entries = [unpack("B",data[3+i:4+i])[0] for i in range(length - 3)]
            if self.tablesize == 16:
                # ***Need to finish 16x16 map***
                zigzagOrder16 = [0,1,16,32,17,2,3,18,33,48,64]
                for i in range(128):
                    self.table[zigzagOrder16[i]] = entries[i]
            else:
                zigzagOrder8 = [0,1,8,16,9,2,3,10,
                                17,24,32,25,18,11,4,5,
                                12,19,26,33,40,48,41,34,
                                27,20,13,6,7,14,21,28,
                                35,42,49,56,57,50,43,36,
                                29,22,15,23,30,37,44,51,
                                58,59,52,45,38,31,39,46,
                                53,60,61,54,47,55,62,63]
                for i in range(64):
                    self.table[zigzagOrder8[i]] = entries[i]

        def __str__(self) -> str:
            count = 0
            string = f"QUANTIZATION TABLE\nId: {self.id}"
            if self.id == 0:
                string = string + " (Luminance)"
            elif self.id == 1:
                string = string + " (Chrominance)"
            string = string + f"\nTable size: {self.tablesize}x{self.tablesize}\nTable Data:\n"
            for i in self.table:
                string = string + " " + str(i)
                count = count + 1
                if count % 8 == 0:
                    string = string + "\n"
            string = string + "END\n"
            return string

    class __startOfFrame():
        def __init__(self, length, data) -> None:
            self.length = length
            if(length != len(data)):
                print("Error! Invalid data length for 'Start of Frame' interval. Cannot process data accuratly.")
                exit(0)

            self.precision = unpack("B", data[2:3])[0]
            if self.precision != 8:
                print(f"Error! JPEG precision must be 8 got a precision of: {self.precision}")
                exit(0)

            self.height = unpack(">H", data[3:5])[0]
            self.width = unpack(">H", data[5:7])[0]
            if(self.height <= 0 | self.width <= 0):
                print(f"Error! Image height and width are either 0 or less which is not possible. Image dimensions recieved are ({self.width}x{self.height})")
                exit(0)

            #if numcomponents = 1 then the jpeg is Y i.e has only the luminance channel (greyscale)
            #if numcomponents = 3 then the jpeg is YCbCr i.e has both luminance and chrominance channels (color)
            #if numcomponents = 4 then the jpeg is CMYK color
            
            self.numComponents = unpack("B", data[7:8])[0]
            if(self.numComponents != 1 | self.numComponents != 3 | self.numComponents != 4 ):
                print(f"Error! Invaild number of color channels. number recieved is: {self.numComponents}") 
                exit(0)
            
            #some JPEGS may start the id at 0 therefore we should account for this
            startsAtZero = False
            #check if first components id is 0 or not
            if(unpack("B", data[8:9])[0] == 0):
                startsAtZero = True

            self.components = []
            self.quantizationMapping = []
            for comp in range(self.numComponents):
                id = unpack("B", data[8 + comp*3:9 + comp*3])[0]
                #if the id starts at zero lets increment it and the other ids by one to work with the rest of our code
                if(startsAtZero):
                    id += 1

                if(id < 1 | id > 3):
                    print(f"Error! Invalid component/channel id. number recieved is: {id}")
                    exit(0)
                
                sampFactor = unpack("B", data[9 + comp*3:10 + comp*3])[0]
                horizontalSampFactor = sampFactor >> 4
                verticalSampFacator = sampFactor & 0x0F
                if(horizontalSampFactor != 1 | verticalSampFacator != 1):
                    print(f"Sorry we are not currently supporting JPEG files with sampling factors other than 1. Recieved a value of {sampFactor}")
                    exit(0)

                quantTableNum = unpack("B", data[10 + comp*3:11 + comp*3])[0]
                self.quantizationMapping.append(quantTableNum)
                component = (id, horizontalSampFactor, verticalSampFacator, quantTableNum)
                self.components.append(component)
            
            #ensures there are no duplicate channels if we have more than one channel
            if self.numComponents > 1:
                for i in range(len(self.components)):
                    for j in range(i+1,len(self.components) - 1,1):
                        if(self.components[i][0] == self.components[j][0]):
                            print(f"Error! Found duplicate component/channel ids. duplicate id is {self.components[i][0]}")
                            exit(0)

        def __str__(self) -> str:
            string = f"START OF FRAME\nPrecision: {self.precision}\nLength: {self.length}\nImage Size: {self.width}x{self.height}\nNumber of Coponenets (Number of Color Channels): {self.numComponents}\nComponents (Color Channels):\n"
            for comp in self.components:
                string = string + f"  id: {comp[0]}\n  horizontal sampling factor:vertical sampling factor: {comp[1]}:{comp[2]}\n  quantization table number (reference): {comp[3]}\n"
            string = string + "END"
            return string

    class __startOfScan():
        def __init__(self, length, data):
            #note length of data will be greater than length of this header so cannot check length
            self.length = length
            self.numComponents = unpack("B", data[2:3])[0]
            self.blocks = []
            for i in range(3,length-5,1):
                compId = unpack("B", data[i:i+1])[0]
                DCAC = unpack("B", data[i+1:i+2])[0]
                DCHuffId = DCAC >> 4
                ACHuffId = 0x0F & DCAC
                block = (compId, DCHuffId, ACHuffId)
                self.blocks.append(block)
            #must be zero in base
            self.startSelection = unpack("B", data[length-4:length-3])[0]
            self.endSelection = unpack("B", data[length-3:length-2])[0]
            self.aprox = unpack("B", data[length-2:length-1])[0]
            #Everything after this header is the huffman bitstream
        
        def __str__(self):
            string = f"START OF SCAN\nLength: {self.length}\nNumber of Components (Color Channels): {self.numComponents}\nBlock Data:\n"
            for block in self.blocks:
                string = string + f"  component id: {block[0]}\n  DC huffman table id: {block[1]}\n  AC huffman table id: {block[2]}\n"
            string = string + f"Start of Selection: {self.startSelection}\nEnd of Selection: {self.endSelection}\nApproximation: {self.approx}\nEND\n"
            return string
    
    class __RestartInterval():
        def __init__(self, length, data):
            self.length = length
            if(length != len(data)):
                print("Error! Invalid data length for 'Restart Interval'. Cannot process data accuratly.")
                exit(0)
            self.restartInterval = unpack(">H", data[2:4])

    class __MCU():
        def __init__(self,dim = 8):
            #size of the map dim x dim
            self.dim = dim

            self.y = [[0 for i in range(dim)] for j in range(dim)]
            self.cb = [[0 for i in range(dim)] for j in range(dim)]
            self.cr = [[0 for i in range(dim)] for j in range(dim)]
            #want r,g,b to access same list so we make them equal
            self.r = self.y
            self.g = self.cb
            self.b = self.cr
        
        def __getitem__(self, index) -> list[list]:
            match(index):
                case 0:
                    return self.y
                case 1:
                    return self.cb
                case 2:
                    return self.cr
                case _:
                    print(f"Error! Index out of range in MCU class. Recieved index {index} but max index is 2.")
                    exit(0)

    imageData = []
    defHeader = None
    startScan = None
    startFrame = None
    restInterval = None
    imageBeingRead = False
    huffmanTables = []
    quantizationTables = []
    blockDim = 0
    zigzagMap = [[0,1,8,16,9,2,3,10,
                    17,24,32,25,18,11,4,5,
                    12,19,26,33,40,48,41,34,
                    27,20,13,6,7,14,21,28,
                    35,42,49,56,57,50,43,36,
                    29,22,15,23,30,37,44,51,
                    58,59,52,45,38,31,39,46,
                    53,60,61,54,47,55,62,63]]

    #def __handleOtherMarkers(self, marker, data):
        #match marker:
            #APPN markers
        #    case 0xE0 | 0xE1 | 0xE2 | 0xE3 | 0xE4 | 0xE5 | 0xE6 | 0xE7 | 0xE8 | 0xE9 | 0xEA | 0xEB | 0xEC | 0xED | 0xEE | 0xEF:
        #        length = unpack
        #
        #   #RST markers
        #   case 
        #pass
    #searches JPEG for headers
    def __searchForHeaders(self):
        maxIndex = len(self.data)
        i = 0
        while i < maxIndex:
            try:
                index = self.data.index(0xFF, i)
                i = index + 1
            except:
                break
            match self.data[index + 1]:
                case 0xD8: # start of image
                    if self.imageBeingRead == True:
                        print("Error! Image data has already started being read, but encountered start of image marker again.")
                        exit(0)
                    self.imageBeingRead = True

                case 0xE0: #default header 0xFF 0xE0
                    defLength = unpack(">H",self.data[(index+2):(index+4)])[0]
                    self.defHeader = self.__defaultHeader(defLength, self.data[index+2: index + defLength + 2])

                case 0xDB: #quantization tables 0xFF 0xDB
                    quantLength = unpack(">H", self.data[index+2:index+4])[0]
                    #length does not include marker
                    quantTable = self.__quantizationTable(quantLength, self.data[index + 2: index + quantLength + 2])
                    if(self.blockDim == 0):
                        self.blockDim = int(math.pow(quantTable.tablesize,0.5))
                    self.quantizationTables.append(quantTable)

                case 0xDD: #Restart Interval 0xFF 0xDD
                    restLength = unpack(">H", self.data[index+2:index+4])[0]
                    self.restInterval = self.__RestartInterval(restLength, self.data[index + 2: index + restLength + 2])
                
                case 0xC0: #start of frame 0xFF 0xC0 (baseline JPEG format)
                    startFrameLength = unpack(">H", self.data[index+2:index+4])[0]
                    
                    #if there was already a start frame in the file we do not know which to use
                    if self.startFrame != None:
                        print("Error! encountered a second start frame! This is a corrupted JPEG, I do not know which one to use.")
                        exit(0)
                    self.startFrame = self.__startOfFrame(startFrameLength, self.data[index + 2: index+startFrameLength+2])

                case 0xC4: #huffman tables 0xFF 0xC4
                    huffLength = unpack(">H", self.data[index+2:index+4])[0]
                    #length does not include the marker
                    huffTable = self.__huffmanTable(huffLength, self.data[index + 2: index + huffLength + 2])
                    self.huffmanTables.append(huffTable)

                case 0xDA: #start of scan 0xFF 0xDA
                    length = unpack(">H", self.data[index+2:index+4])[0]
                    self.startScan = self.__startOfScan(length, self.data[index + 2 : index + 2 + length])
                    self.imageData=self.data[index + 2 + length:]

                #case _:
                #    self.__handleOtherMarkers(self.data[index+2])
                #case 0xD9: #end of image 0xFF 0xD9

    #remove 0xFF00 that appears in the image data
    def __removeStuffing(self):
        data = []
        for i in range(len(self.imageData)):
            cur = unpack("B", self.imageData[i:i+1])[0]
            next = unpack("B", self.imageData[i+1:i+2])[0]
            if cur == 0xFF:
                if next == 0x00:
                    data.append(self.imageData[i])
                    i += 1
                elif next == 0xD9:
                    break
                else:
                    data.append(self.imageData[i])
            else:
                data.append(self.imageData[i])
        return data

    def __getDCCoefLen(self, tableId, stream):
        DCCoeflength = DCTables[tableId].searchHuffTree(stream)
        if(DCCoeflength == None):
            print("Error! bitstream could not be converted to a symbol")
            exit(0)
        if(DCCoeflength > 11):
            print("Error! DC length greater than 11")
            exit(0)
        return DCCoeflength

    def __getDCCoef(self,stream,length):
        DCCoef = stream.getBits(length)
        if(DCCoef == -1):
            print("Error! Invalid DC Coefficient value")
            exit(0)
        #check if DCCoef is negative
        if(length != 0 & DCCoef < math.pow(2,length-1)):
            DCCoef = DCCoef - (math.pow(2,length) - 1)
        return DCCoef

    def __getACCoef(self):


    #Begin decoding the data using the huffman tables
    def __createMCUsFromHuffman(self,data):
        #Need to handle restart intervals!!!! Might need to change the way data is processed

        MCURows = math.ceil(self.startFrame.width / self.blockDim) 
        MCUCols = math.ceil(self.startFrame.height / self.blockDim)
        MCUs = [[self.__MCU(self.blockDim) for i in range(MCURows)] for j in range(MCUCols)]
        #Organize the DC and AC Huffman tables
        DCTables = [None for i in range(4)]
        ACTables = [None for i in range(4)]
        for table in self.huffmanTables:
            if(table.id > 3 | table.id == 0):
                print("Error! Invalid table id found in __decodingFromHuffman")
                exit(0)
            #DC Table
            if table.classification == 0:
                DCTables[table.id] = table
            #AC Table
            elif table.classification == 1:
                ACTables[table.id] = table
            else:
                print("Error! Invalid classification found in __decodingFromHuffman")
                exit(0)
        
        print(DCTables[0])

        mapIndex = 0
        if(self.blockDim == 16):
            mapIndex = 1

        prevDCCoef = [0 for i in range(3)]
        stream = self.__bitStream(data)
        for i in range(MCURows):
            for j in range(MCUCols):
                for k in range(self.startScan.numComponents):
                    #start by getting DC coefficient length
                    DCCoeflength = self.__getDCCoefLength(self.startScan.blocks[k][1],stream)
                    #using the length get the actual DC coefficient
                    DCCoef = self.__getDCCoef(stream,DCCoeflength)

                    #Keep track of old DCCoef since they will build onto eachother
                    MCUs[i][j][k][0][0] = DCCoef + prevDCCoef[k]
                    prevDCCoef[k] = DCCoef


                    #***
                    #*** MADE IT HERE SIMPLIFY CODE AND FIGURE OUT WHAT IS WRONG ***
                    #***


                    #get AC values *** Note for simplicity we will only account for JPEGs with self.blockDim x self.blockDim tables
                    for l in range(1,self.blockDim*self.blockDim,1):
                        symbol = ACTables[self.startScan.blocks[k][1]].searchHuffTree(stream)
                        if(symbol == -1):
                            print("Error! Invalid AC value")
                            exit(0)
                        
                        #if the symbol is 0 we just fill the rest of the MCU component with 0s
                        if(symbol == 0):
                            while(l < MCURows):
                                x = math.floor(self.zigzagMap[mapIndex][l] / self.blockDim) 
                                y = self.zigzagMap[mapIndex][l] % self.blockDim
                                MCUs[l][j][k][x][y] = 0
                                l += 1
                            break
                        
                        numZeros = symbol >> 4
                        ACCoeflength = symbol & 0x0F

                        #0xF0
                        if(symbol == 0xF0):
                            numZeros = 16
                        
                        if(l + numZeros >= self.blockDim * self.blockDim):
                            print("Error! index out of bounds while adding zeros to MCU")
                            exit(0)
                        
                        for m in range(numZeros):
                            #Need to convert 1d array zigzag map into 2d array indexes
                            x = math.floor(self.zigzagMap[mapIndex][m] / self.blockDim) 
                            y = self.zigzagMap[mapIndex][m] % self.blockDim
                            MCUs[l][m][k][x][y] = 0
                            l += 1
                        
                        #AC coeff cannot be greater than 10
                        if(ACCoeflength > 10):
                            print("Error! AC length greater than 10")
                            exit(0)

                        if(ACCoeflength != 0):
                            ACCoef = stream.getBits(ACCoeflength)
                            if(ACCoef == -1):
                                print("Error! Invalid DC Coefficient value")
                                exit(0)
                             #check if ACCoef is negative
                            if(ACCoeflength != 0 & ACCoef < math.pow(2,ACCoeflength-1)):
                                ACCoef = ACCoef - (math.pow(2,ACCoeflength) - 1)
                            
                            #Need to convert 1d array zigzag map into 2d array indexes
                            x = math.floor(self.zigzagMap[mapIndex][l] / self.blockDim) 
                            y = self.zigzagMap[mapIndex][l] % self.blockDim
                            MCUs[l][j][k][x][y] = ACCoef
                            l += 1
        return MCUs


    def decodeImage(self):
        print("\n*** Starting Decoding *** Not complete yet\n")
        data = self.__removeStuffing()
        MCUs = self.__createMCUsFromHuffman(data)
        BMPEncoder.BMPEncoder(self.file,self.startFrame.width,self.startFrame.height,self.startFrame.numComponents,MCUs)


    def __init__(self, file):
        self.file = file
        with open(file, 'rb') as f:
            self.data = f.read()
        #jpg files start with 0xFF 0xD8
        if(self.data[0] != 0xFF | self.data[1] != 0xD8):
            print("Error! File is not a correct jpg, jpeg or jfif file. Cannot decode")
            exit(0)
        print("\n*** Scanning JPEG File ***\n")
        self.__searchForHeaders()
        self.decodeImage()

    def __str__(self) -> str:
        string = self.defHeader
        for table in self.quantizationTables:
            string = string + table
        string = string + self.startFrame
        for table in self.huffmanTables:
            string = string + table
        string = string + self.startScan
        return string

