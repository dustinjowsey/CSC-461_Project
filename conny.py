import sys
import re
import JPEGDecoder
import PNGDecoder
import PNGEncoder
import BMPDecoder
import BMPEncoder

def display_options():
    print("conny [File] [option]\nOptions:\n-h list of all commands in conny.")

def main(argv):
    #Process options
    options = argv[2:]

    #check provided arguments
    match(argv):
        case [_,"-h"]:
            display_options()
        case [_, filename, *_]:
            regex = re.compile("[.][a-z]*[A-Z]*")
            extension = regex.search(filename)
            if extension == None:
                print("File does not exist. (Include file extension)")
                exit(0)
            extension = extension.group()[1:]
            
            match(extension, options):
                case("jpeg" | "jpg" | "jfif", ["-d"]):
                    JPEGDecoder(filename)
                case("jpeg" | "jpg" | "jfif", ["-d", "-i"]):
                    jpeg = JPEGDecoder.JPEGDecoder(filename)
                    print(jpeg)
                case("png", ["-d"]):
                    png = PNGDecoder.PNGDecoder(filename)
                case("png", ["-d", "-e", "bmp"]):
                    png = PNGDecoder.PNGDecoder(filename)
                    BMPEncoder.BMPEncoder(filename,png.width,png.height,png.numColorChannels,png.data)
                case("bmp", ["-d"]):
                    bmp = BMPDecoder.BMPDecoder(filename)
                case("bmp", ["-d -e png"]):
                    bmp = BMPDecoder.BMPDecoder(filename)
                    PNGEncoder.PNGEncoder(filename,bmp.width,bmp.height,bmp.numColorChannels,bmp.data)

        case _:
            print("do nothing")
            

    if(len(argv) < 3):
        print("Incorrect command please type conny -h for help")


if __name__ == "__main__":
    main(sys.argv)
