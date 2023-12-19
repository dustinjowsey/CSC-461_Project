# CSC-461 Project

<h2>**Project Proposal**</h2>
**File Converter**
Image and Video File Type Conversion

**What’s the problem?**    
The issue of having numerous file types is that some applications may require you to use specific
file types in their software. It is important to have methods to convert between file types to allow
people to use software easier.

**What has been done?**    
Current file conversion options tend to cost money, or are posted on insecure websites. You can
not always be too sure what you are downloading when installing the converted file.

**Approach to the project**    
My approach to this project is to begin with researching common photo file types. After doing this I
will begin implementing a file conversion program for decoding and encoding these common photo file
types. After this I will research audio file formats and implement encoding and decoding algorithms for
these types of files as well. If time permits I would like to attempt video file conversion as well as file
compression such as .zip.

**Delivery**    
I plan to deliver this on my GitHub page and use command line to run the program. By October 23rd
(our update date) I want to have finished the photo conversion part of the program. After this I want to
have implemented the audio conversion aspect by November 6th. Then I would like to continue
researching video file types and have this implemented by the December 4th. If I can get ahead of
schedule I would like to look into .zip file types and maybe create a UI as well.
 
**Website**    
https://github.com/dustinjowsey/CSC-461_Project

<h2>**Conny Documentation:**</h2>    
To run please type <br />
python conny.py [filename] [options] <br />
Note: <br />
&nbsp;&nbsp;Right now please use python conny.py profile.jpg -d -i <br />
This will display the steps of the decoding process up to the point I have made it to i.e not as far as I would like to have made it. <br />
<br />
<h2>**Project update**</h2>    
Dustin Jowsey     
V00964979    
CSC-461    
									Project Update    
    
• For the schedule I have created, I am quite far behind. I do not think it is possible to complete all that I had planned originally in the time period of the project.       
• The main issue I have been having is underestimating the complexity of the JPEG image format. I would like my program to account for as many different types of JPEGS as well, so there has been a lot of learning to do. Furthermore, information on JPEG is out there, but it is often not easily understood (at least for me) or it is somewhat misleading in how the process to encoding a JPEG image works. This has definitely been the biggest struggle for me. I have read that the PNG encoding is a lot simpler so I am hoping it won’t take as long as JPEG.       
• I think I will need to adjust my proposal as I wanted to be working on audio file conversions by now, but am still working on the JPEG decoder. I think I will be able to complete the JPEG and PNG converter soon as once I finish the decoder I will have a really good idea of the process that goes into JPEG images. I would like to push myself to at least complete an audio file conversion by the end of the course. I would like to attempt MP3 to WAV and vice versa.        
• I would like to update the output of data to provide a better way of displaying data the decoding process if they choose to see the output.       
<h2>**References**</h2>
https://yasoob.me/posts/understanding-and-writing-jpeg-decoder-in-python/ <br />
This reference has helped me to understand the JPEG Header a lot as well as give me a way to compare my output to what is expected from a working JPEG decoder.



