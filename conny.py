import sys
import re
import JPEGDecoder
import PNGDecoder

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
            
        case _:
            print("do nothing")
            

    if(len(argv) < 3):
        print("Incorrect command please type conny -h for help")


if __name__ == "__main__":
    main(sys.argv)
