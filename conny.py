import sys
import re
from struct import unpack
import struct

class Node():
    def __init__(self, val):
        self.left = None
        self.right = None
        self.val = val

class JPEG():
    #data types for JPEG objects
    class defaultHeader():
        length = 0
        identifier = 0
        version = 0
        units = 0
        density = (0,0)
        thumbnail = 0
    
    class quantizationTable():
        length = 0
        destination = 0
        table = []

    class huffManTable():

        #returns a list of pairs of bit count plus code since codes will be integers
        #for each code of a given length adds the current code to the list and increments the code by 1. 
        #once all the codes of a certain length are found add a 0 to the end (shift left) and repeat
        def createBinaryValues(self):
            codeList = []
            #base case length 1
            curCode = 0b0
            symbolCount = 0
            for i in range(len(self.symbolBitLengths)):
                if(self.symbolBitLengths[i] != 0):
                    for j in range(self.symbolBitLengths[i]):
                        #add bit count, code and symbol to list
                        codeList.append((j,bin(curCode),self.symbols[symbolCount]))
                        symbolCount = symbolCount + 1
                        curCode = curCode + 0b0000000000000001
                curCode <<= 1
            return codeList
        
        #Extracts data from a huffman table block used in jpeg file formats
        #length - provide the length of the block (given by hex values at 2-4)
        #huffData - provide the data of the huffmantable block beginning at the start of the marker
        def __init__(self, length, huffData):
            #note length does not include the length of the marker
            self.length = length
            classDestByte = unpack("B", huffData[4:5])[0]
            #0 = DC or 1 = AC table
            self.classification = 1 if (0x10 & classDestByte) == 0x10 else 0
            self.destination = 1 if (0x01 & classDestByte) == 0x01 else 0

            #always length of 16
            self.symbolBitLengths = [unpack("B", huffData[5 + i:6 + i])[0] for i in range(16)]
            self.symbols = [unpack("B",huffData[21 + i:22 + i])[0] for i in range(length-19)]
            self.codes = self.createBinaryValues()
            return None

        def __str__(self) -> str:
            string = f"\nHUFFMAN TABLE\nMarker = 0xFFC4\nLength = {self.length} hex values (not including 2 values for marker)\nClass = {self.classification}\nDestination = {self.destination}\nBit length array = {self.symbolBitLengths}\nSymbols = {self.symbols}\n"
            string = string + f"Codes/Symbols:\n"
            for i in range(len(self.codes)):
                string = string + f"    {self.codes[i][1]} = {self.codes[i][2]}\n"
            string = string + "END\n"
            return string

    class startOfScan():
        length = 0
    
    data = []
    imageData = []
    defHeader = defaultHeader()
    startScan = startOfScan()
    quantizationTables = []
    huffmanTables = []
    startOfFrame = {"length":0, "precision":0, "line Nb" : 0, "samples": 0, "components": 0}
    startOfScan = {""}

    def searchForHeaders(self):
        maxIndex = len(self.data)
        i = 0
        defaultHeaderIndex = 0
        quantizationTables = []
        frameStartIndex = 0
        huffmanTables = []
        scanStartIndex = 0
        endOfImageIndex = 0

        while i < maxIndex:
            try:
                index = self.data.index(0xFF, i)
                i = index + 1
            except:
                break
            match self.data[index + 1]:
                case 0xE0: #default header 0xFF 0xE0
                    self.defHeader.length = unpack(">H",self.data[(index+2):(index+4)])[0]
                    self.defHeader.version = unpack(">H", self.data[index+9:index+11])[0]
                    self.defHeader.density = (unpack(">H", self.data[index+12:index+14])[0],unpack(">H", self.data[index+14:index+16])[0])
                    self.defHeader.thumbnail = unpack(">H", self.data[index+16:index+18])[0]
                case 0xDB: #quantization tables 0xFF 0xDB
                    quantTable = self.quantizationTable()
                    quantTable.length = unpack(">H", self.data[index+2:index+4])[0]
                    quantTable.destination = unpack("B", self.data[index+4:index+5])[0]
                    quantTable.table = [unpack("B",self.data[index+6+i:index+7+i])[0] for i in range(0,quantTable.length-3,1)]
                    self.quantizationTables.append(quantTable)
                #case 0xC0: #start of frame 0xFF 0xC0
                case 0xC4: #huffman tables 0xFF 0xC4
                    huffLength = unpack(">H", self.data[index + 2: index + 4])[0]
                    #length does not include the marker
                    huffTable = self.huffManTable(huffLength, self.data[index: index + huffLength + 2])
                    huffmanTables.append(huffTable)
                    print(huffTable)
                case 0xDA: #start of scan 0xFF 0xDA
                    self.startScan.length = unpack(">H", self.data[index + 2: index + 4])[0]
                    self.imageData = self.data[index + 2 + self.startScan.length:-2]
                #case 0xD9: #end of image 0xFF 0xD9
                


    def __init__(self, file):
        with open(file, 'rb') as f:
            self.data = f.read()
        #jpg files start with 0xFF 0xD8
        if(self.data[0] != 0xFF | self.data[1] != 0xD8):
            print("File is not a correct jpg, jpeg or jfif file. Cannot decode")
            exit(0)
        self.searchForHeaders()

def display_options():
    print("conny [File] [option]\nOptions:\n-h list of all commands in conny.")

def main(argv):
    #check provided arguments
    match(argv):
        case [_,"-h"]:
            display_options()
        case [_, filename, option]:
            regex = re.compile("[.][a-z]*")
            extension = regex.search(filename)
            if extension == None:
                print("File does not exist. (Include file extension)")
                exit(0)
            extension = extension.group()[1:]

            match(extension):
                case "jpg"|"jpeg"|"jfif":
                    JPEG(filename)
            
        case _:
            print("do nothing")
            

    if(len(argv) != 3):
        print("Incorrect command please type conny -h for help")


if __name__ == "__main__":
    main(sys.argv)