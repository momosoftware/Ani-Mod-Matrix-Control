from Tkinter import *
import serial
import threading
import ConfigParser
import logging
import sys
from win32api import GetSystemMetrics

#9600,8,n,1

global comNum, bmnNum, com, v, COMPortNumber, BowlingMusicNetworkInputNumber, screenWidth, screenHeight


# Set up our logging files
sys.stderr = open('ProjectorControl.log', 'w')
sys.stdout = open('ProjectorControl.err', 'w')

# create logger
logger = logging.getLogger("logging")
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter("[%(asctime)s] - %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)
logger.debug('====ProgramStart====')

# load our config and prepare to read the file
configParser = ConfigParser.RawConfigParser()   
configFilePath = r'config.conf'
configParser.read(configFilePath)

# pull config values from the file to 
# fill our comNum and bmnNum globals
comNum = configParser.get('general', 'COMPortNumber')
bmnNum = configParser.get('general', 'BowlingMusicNetworkInputNumber')


# initialize our gui
root = Tk()

root.iconbitmap('avicon.ico')

# init the variable to be used by our radio buttons    
v = StringVar()
v.set("1") # default it to 1, the first input

class Example(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent        
        self.initUI()
    
    # ########################
    # Bowling Music to all
    # ########################
    # Puts bowling music across the entire house,
    # standard setup for glow birthday parties
    # and glow bowl on nights without sports games
    # ########################
    
    def bmnToAll(self):
        logger.debug('====================')
        logger.debug('Set Bowling Music to all')
        logger.debug(str(bmnNum) + 'All.')
        logger.debug('====================')
        logger.debug(' ')
        
        #lets see if we can open the port
        #9600,8,n,1
        try:
            com = serial.Serial(
                port = int(comNum)-1,
                baudrate = 9600,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize = serial.EIGHTBITS
            )
            #if it is open, then let's send our command
            if com.isOpen():
                com.write(str(bmnNum) + 'All.')
                com.close()
        #if we were unable to open it then let's log the exception
        except serial.SerialException as ex:
            logger.debug('Port ' + int(comNum)-1 + ' is unavailable: ' + ex)
        
    
    # ########################
    # Standard setup
    # ########################
    # Puts bowling music on each odd pair
    # and DirectTV on each even pair, sequentially.
    # You end up with:
    #
    # Lanes 1 & 2   Bowling Music
    # Lanes 3 & 4   DTV1
    # Lanes 5 & 6   Bowling Music
    # Lanes 7 & 8   DTV2
    #
    # and so on
    #
    # need to automate into loop, but not today
    # ########################
    def standardInOut (self):
        logger.debug('====================')
        logger.debug('Set standard AV config')
        logger.debug(str(bmnNum) + 'B1,3,5,7,9,11,13,15.')
        logger.debug('1B2.')
        logger.debug('2B4.')
        logger.debug('3B6.')
        logger.debug('4B8.')
        logger.debug('5B10.')
        logger.debug('6B12.')
        logger.debug('7B14.')
        logger.debug('8B16.')
        logger.debug('====================')
        logger.debug(' ')
        #lets see if we can open the port
        try:
            com = serial.Serial(
                port = int(comNum)-1,
                baudrate = 9600,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize = serial.EIGHTBITS
            )
            #if it is open, then let's send our command
            if com.isOpen():
                com.write(str(bmnNum) + 'B1,3,5,7,9,11,13,15.') # BM to every other projector
                com.write('1B2.') # DTV1 to Pair2
                com.write('2B4.') # DTV2 to Pair4
                com.write('3B6.') # and so on
                com.write('4B8.') # and so forth
                com.write('5B10.')
                com.write('6B12.')
                com.write('7B14.')
                com.write('8B16.')
                com.close()
        #if we were unable to open it then let's log the exception
        except serial.SerialException as ex:
            logger.debug('Port ' + int(comNum)-1 + ' is unavailable: ' + ex)
    
    
    # ########################
    # Standard In/Out function
    # ########################
    # takes three arguments, ignores the first 
    # as i don't know what it is or why it is 
    # passed, probably something related to 
    # the lambda function, maybe its identifier?
    #
    # The next two arguments are the input and 
    # output numbers we'd like to set. These are 
    # provided by radio button and button, respectfully.
    # Only sets one output to one input at a time, 
    # most useful for changing a single pair to a 
    # certain DTV box or back to music videos, 
    # if the customer requests it specifically.
    # ########################
    def setCustomInOut(dummy, input, output):
        logger.debug('====================')
        logger.debug('Set a custom config')
        logger.debug(str(input) + 'B' + str(output) + '.')
        logger.debug('====================')
        logger.debug(' ')
        #lets see if we can open the port
        try:
            com = serial.Serial(
                port = int(comNum)-1,
                baudrate = 9600,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize = serial.EIGHTBITS
            )
            #if it is open, then let's send our command
            if com.isOpen():
                com.write(str(input) + 'B' + str(output) + '.')
                com.close()
        #if we were unable to open it then let's log the exception
        except serial.SerialException as ex:
            logger.debug('Port ' + int(comNum)-1 + ' is unavailable: ' + ex)
    
    
    def initUI(self):
        # set window title
        self.parent.title("Projector Control")
        
        # init menubar
        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)
        
        # fill menubar with items
        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Standard setup", command=self.standardInOut)
        fileMenu.add_command(label="Bowling Music to all", command=self.bmnToAll)
        menubar.add_cascade(label="File", menu=fileMenu)

        self.pack(fill=BOTH, expand=1)
        self.var = IntVar()
        
        # pull total number of inputs as well
        # as the Bowling Music input number 
        # from config file and assign var
        logger.debug('==Read config file==')
        numIn = configParser.get('general', 'numberOfInputs')
        bmnIn = configParser.get('general', 'bowlingMusicNetworkInputNumber')
        
        # ######################################################
        # ######################################################
        # ######################################################
        # Center window by getting screensize from Windows
        # dividing by 2, then subtracting windowsize/2
        # ######################################################
        # ######################################################
        # ######################################################
        screenWidth = int(GetSystemMetrics (0))
        screenHeight = int(GetSystemMetrics (1))
        
        windowWidth = int(configParser.get('general', 'windowWidth'))
        windowHeight = int(configParser.get('general', 'windowHeight'))
        
        windowX = screenWidth/2 - windowWidth/2
        windowY = screenHeight/2 - windowHeight/2
        
        #logger.debug('Screen Width: ' + str(screenWidth) + '\nScreen Height: ' + str(screenHeight))
        #logger.debug('Window Width: ' + str(windowWidth) + '\nWindown Height: ' + str(windowHeight))
        # logger.debug(str(windowWidth) + "x" + str(windowHeight) + "+" + str(windowX) + "+" + str(windowY))
        
        # set window size
        windowSizePos = str(windowWidth) + "x" + str(windowHeight) + "+" + str(windowX) + "+" + str(windowY)
        root.geometry(windowSizePos)
        
        #init our inputs dict
        inputs= [] 
        
        # then fill it, naming it DTV# where # is the input number,
        # unless it is # matches the bowling music input number (bmnIn)
        # at which point we name it Bowling Music
        logger.debug('=====Init input=====')
        for i in range(int(numIn)):
            if i != int(bmnIn) - 1:
                inputs.append(['DTV' + str(i + 1), str(i + 1)])
            else:
                inputs.append(['Bowling Music', str(bmnIn)])
        
        # take our list of inputs and make radio buttons for them,
        # storing the value in the variable "v" that we initialized earlier
        for text, input in inputs:
            b = Radiobutton(self, text=text,
                            variable=v, value=input)
            b.grid(column=0, padx = 10, sticky=W)
        
        
        # get number of outputs from file and get current input
        # status of each output, print to label
        # Need better logging
        numOut = configParser.get('general', 'numberOfOutputs')
        
        logger.debug('====Init Status====')
        for output in range(int(numOut)):
            #lets see if we can open the port
            try:
                com = serial.Serial(
                    port = int(comNum)-1,
                    baudrate = 9600,
                    parity = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_ONE,
                    bytesize = serial.EIGHTBITS,
                    timeout = .5
                )
                #if it is open, then let's send our command
                if com.isOpen():
                    
                    com.write('Status' + str(int(output+1)) + '.') # int(string("fuck it")) w
                    response = com.read(6)
                    currentOutput = response[-3:]
                    logger.debug(str(currentOutput))
                    w = Label(self, text=currentOutput, relief=SUNKEN, width=5).grid(row=output, padx = 5,  column=1)
                    # print response
                    com.close()
            #if we were unable to open it then let's log the exception
            except serial.SerialException as ex:
                print ""
                #logger.debug('Port ' + int(comNum)-1 + ' is unavailable: ' + ex)
        
        # get number of outputs from var and create buttons for each
        # output, each corresponding to a specific projector. When clicked
        # the buttons should send the value of "v" (which designates 
        # which input is currently selected) and the output number to our 
        # CustomInOut() function.
        logger.debug('====Init outputs====')
        for i in range(int(numOut)):
            vars()['btnOut' + str(i)] = Button(self, width=15, text="Projector " + str(i + 1), command=lambda i=i: self.setCustomInOut(v.get(), i+1) )
            vars()['btnOut' + str(i)].grid(row=i, column=2, sticky=E)
        
        

        
    def onExit(self):
        logger.debug('=====ProgramEnd=====')
        raise SystemExit

def main():
    
    app = Example(root)
    root.mainloop()  


if __name__ == '__main__':
    main()  