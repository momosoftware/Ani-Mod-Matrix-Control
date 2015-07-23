#!/usr/bin/env python
#title          :ProjectorControl.py
#description    :Management interface for the Ani-Mod video matrix
#author         :Jesse "acostoss" Hamilton
#date           :2014-09-24
#version        :1.2.0
#usage          :python setup.py py2exe
#notes          :Only tested in Windows 8.1 Pro
#todo           :Redirect to log files without stdout and stderr
#todo           :add program status bar to bottom of window
#todo           :finish refactoring code to allow for cmd-line switches, separating gui and backing code
#todo           :error checking for command line code
#pythonVersion  :2.7.8
#===============================================================================

import ttk
from Tkinter import *
import serial
import threading
import ConfigParser
import logging
import sys
import time
import tkMessageBox
import httplib
import urllib
import random
from win32api import GetSystemMetrics


global com, v, COMPortNumber, BowlingMusicNetworkInputNumber, screenWidth, screenHeight



# Set up our logging files
sys.stderr = open('ProjectorControl.log', 'a')
# sys.stdout = open('ProjectorControl.err', 'a')

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

# initialize our gui
root = Tk()

root.iconbitmap('avicon.ico')

# init the variable to be used by our radio buttons to determine which input was selected
v = StringVar()
v.set("1") # default it to 1, the first input

# class for spiffy case/switch implementation from http://code.activestate.com/recipes/410692/
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        yield self.match
        raise StopIteration

    def match(self, *args):
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False

class Master(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent

    # ########################
    # Get Output Status
    # ########################
    # Grabs current input number for each output
    # and prints to a label in the same row
    # as the output button.
    # ########################
    def getOutputStatus(self):
        logger.debug('====Init Status====')

        try:
            notFirstRun
        except NameError:
            logger.debug('=====First Run=====')
        else:
            logger.debug('===Not First Run===')
            statusModal = Toplevel(self)
            statusModal.title("Loading Status")
            screenWidth = int(GetSystemMetrics (0))
            screenHeight = int(GetSystemMetrics (1))
            winX = screenWidth/2 - 150/2
            winY = screenHeight/2 - 50/2
            modalSizePos = "250x10+" + str(winX) + "+" + str(winY)
            statusModal.geometry(str(modalSizePos))
            statusModal.lift()
            loadingLabel = Label(statusModal, text="loading").grid(row=0, column=0)
            root.withdraw()
            statusModal.grab_set()

        for output in range(int(configParser.get('general', 'numberOfOutputs'))):
            #lets see if we can open the port
            try:
                com = serial.Serial(
                    port = int(configParser.get('general', 'COMPortNumber'))-1,
                    baudrate = 9600,
                    parity = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_ONE,
                    bytesize = serial.EIGHTBITS,
                    timeout = .4
                )
                #if it is open, then let's send our command
                if com.isOpen():
                    trashResponse = com.read(100)
                    logger.debug("trash: " + trashResponse)
                    com.write('Status' + str(int(output+1)) + '.') # int(string("fuck it")) w
                    time.sleep(0.4)
                    response = com.read(6)
                    currentInput = response[-3:]
                    logger.debug('Output ' + str(output) + '\'s current input:' + str(currentInput))
                    w = Label(self, text=currentInput, relief=SUNKEN, width=5).grid(row=output, padx = 5,  column=1)
                    # print response
                    com.close()
            #if we were unable to open it then let's log the exception
            except serial.SerialException as ex:
                logger.debug('Port ' + str(int(configParser.get('general', 'COMPortNumber'))-1) + ' is unavailable: ' + ex) # int(string("fuck it")) w
        try:
            notFirstRun
        except NameError:
            logger.debug('==Still First Run==')
        else:
            logger.debug('==Kill the modal!==')
            root.deiconify()
            statusModal.grab_release()
            statusModal.destroy()
        global notFirstRun
        notFirstRun = True

    # ########################
    # Bowling Music to all
    # ########################
    # Puts bowling music across the entire house,
    # standard setup for glow birthday parties
    # and glow bowl on nights without sports games
    # Erin @ strikers
    # 954-749-1400
    # ########################
    def bmnToAll(self,gui):
        logger.debug('====================')
        logger.debug('Set Bowling Music to all')
        logger.debug(str(configParser.get('general', 'BowlingMusicNetworkInputNumber')) + 'All.')
        logger.debug('====================')
        logger.debug(' ')

        #lets see if we can open the port
        #9600,8,n,1
        try:
            com = serial.Serial(
                port = int(configParser.get('general', 'COMPortNumber'))-1,
                baudrate = 9600,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize = serial.EIGHTBITS
            )
            #if it is open, then let's send our command
            if com.isOpen():
                com.write(str(configParser.get('general', 'BowlingMusicNetworkInputNumber')) + 'All.')
                com.close()
                #get our status refilled
                if (gui == True):
                    self.getOutputStatus()

        #if we were unable to open it then let's log the exception
        except serial.SerialException as ex:
            logger.debug('Port ' + str(int(configParser.get('general', 'COMPortNumber'))-1) + ' is unavailable: ' + ex)

    def standardInOut(self, gui):
        logger.debug('====================')
        logger.debug('Set standard AV config')
        #start with 1
        currentInput = 1
        numIn = configParser.get('general', 'numberOfInputs')
        # define our Bowling Music Input
        bmnIn = configParser.get('general', 'bowlingMusicNetworkInputNumber')
        #iterate through the loop a number of times equal to our number of outputs

        inOuts = []

        # then fill it, naming it DTV# where # is the input number,
        # unless it is # matches the bowling music input number (bmnIn)
        # at which point we name it Bowling Music

        for i in range(int(configParser.get('general', 'numberOfOutputs'))):
            #if our output is divisible by two with no remainder...
            if (i + 1) % 2 == 0:
                # then it is even, which means we need to put
                # our next input onto that lane
                if currentInput != int(bmnIn) - 1:
                    # if our current input is not bowling music,
                    # we're in the clear and don't need to do anything to our
                    # currentInput before moving on.
                    pass
                else:
                    # our currentInput is our BowlingMusic input, so we have to
                    # increment currentInput by one before moving on
                    currentInput = currentInput + 1

                # Once we've verified this is an even lane and have also
                # verified we're not currently sitting on the bowling music
                # input, we can put our currentInput and current outpit into our
                # inOuts dict
                inOuts.append([currentInput, i + 1])

                # move on to the next input
                currentInput = currentInput + 1

            else:
                # otherwise it is odd, so it gets bowling music
                inOuts.append([configParser.get('general', 'BowlingMusicNetworkInputNumber'), i + 1])


        logger.debug('====================')
        logger.debug(' writing inOuts')
        logger.debug('====================')
        logger.debug(inOuts)

        #lets see if we can open the port
        try:
            com = serial.Serial(
                port = int(configParser.get('general', 'COMPortNumber'))-1,
                baudrate = 9600,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize = serial.EIGHTBITS
            )
            #if it is open, then let's send our command
            if com.isOpen():
                for input, output in inOuts:
                    com.write(str(input) + 'B' + str(output) + '.')
                    logger.debug(str(input) + 'B' + str(output) + '.')
                com.close()
        #if we were unable to open it then let's log the exception
        except serial.SerialException as ex:
            logger.debug('Port ' + str(int(configParser.get('general', 'COMPortNumber'))-1) + ' is unavailable: ' + ex)

        time.sleep(0.5)
        if (gui == True):
            self.getOutputStatus() #refresh our status
            
    # 
    # Custom Command Function
    #
    #
    #
    #
    #
    #
    # 
    # 
    
    def getCustom1Cmd(self):
        customCmd1 = configParser.get('general', 'custom1cmd')
        try:
            com = serial.Serial(
                port = int(configParser.get('general', 'COMPortNumber'))-1,
                baudrate = 9600,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize = serial.EIGHTBITS
            )
            #if it is open, then let's send our command
            if com.isOpen():
                for input, output in inOuts:
                    com.write(str(customCmd1))
                    logger.debug("command:" + str(customCmd1))
            com.close()
        #if we were unable to open it then let's log the exception
        except serial.SerialException as ex:
            logger.debug('Port ' + str(int(configParser.get('general', 'COMPortNumber'))-1) + ' is unavailable: ' + ex)
   

    # ########################
    # Custom In/Out function
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
    def setCustomInOut(self, input, output):
        logger.debug('====================')
        logger.debug('Set a custom config')
        logger.debug(str(input) + 'B' + str(output) + '.')
        logger.debug('====================')
        logger.debug(' ')
        #lets see if we can open the port
        try:
            com = serial.Serial(
                port = int(configParser.get('general', 'COMPortNumber'))-1,
                baudrate = 9600,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize = serial.EIGHTBITS
            )
            #if it is open, then let's send our command
            if com.isOpen():
                com.write(str(input) + 'B' + str(output) + '.')
                com.close()
                self.getOutputStatus()
        #if we were unable to open it then let's log the exception
        except serial.SerialException as ex:
            logger.debug('Port ' + str(int(configParser.get('general', 'COMPortNumber'))-1) + ' is unavailable: ' + ex)


    # ########################
    # Projectors On
    # ########################
    # Turns all projectors n the house on. Does so
    # through use of HTTP POST, lifted straight from the
    # projector's web portal. Doesn't require any sort
    # of authentication to hit the POST taget, despite needing
    # auth to access the page which send the POST if accessing
    # via web browser.
    #
    # Really glad that I didn't have to do any bullshit with cURL
    # and can get away with use of httplib and urllib'
    #
    # Currently a proof of concept
    # TODO:
    # - starting with a projStartingIP, take numOfProj variable amount
    #   iterate through a for loop and turn all projectors on.
    # - Do something similar to turn them off.
    # - Another function for turning on/off a single projector
    # - one for status
    # - oh and properly comment the function
    # ########################
    def projectorsOn(self):
        logger.debug('====================')
        logger.debug('Turn on a specific projector')
        logger.debug('====================')

        projSubnet = configParser.get('general', 'projectorSubnet')
        projHost = configParser.get('general', 'projectorStartingHost')
        currentProjHost = int(projHost)
        for i in range(int(configParser.get('general', 'numberOfOutputs'))):
            projIP = "192.168." + str(projSubnet) + "." + str(currentProjHost)

            logger.debug("URL: " + projIP)
            projCMD = "command=24003100    0f0001010003010001"
            params = urllib.urlencode({'@number': 12524, '@type': 'issue', '@action': 'show'})
            headers = {"Content-Type": "application/x-www-form-urlencoded", "Cache-Control": "no-cache"}
            logger.debug(headers)
            projCON = httplib.HTTPConnection(projIP)
            projCON.request("POST", "/tgi/return.tgi?sid=" + str(random.random()), projCMD, headers)
            projRESP = projCON.getresponse()
            logger.debug(projRESP.status)
            logger.debug(projRESP.reason)
            data = projRESP.read()
            logger.debug(data)
            projCON.close()

            currentProjHost = currentProjHost + 1

    def initUI(self):
        root.deiconify()
        # set window title
        self.parent.title("Projector Control")

        # init menubar
        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)

        # fill menubar with items
        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Standard setup", command=self.standardInOut)
        fileMenu.add_command(label="Bowling Music to all", command=self.bmnToAll)
        fileMenu.add_command(label="Turn on projectors", command=self.projectorsOn)
        fileMenu.add_command(label="Refresh", command=self.getOutputStatus)
        
        fileMenu.add_separator()
        
        fileMenu.add_command(label=configParser.get('general', 'custom1Name'), command=self.getCustom1Cmd)

        fileMenu.add_separator()

        fileMenu.add_command(label="Exit", underline = 0, command=self.onExit)
        menubar.add_cascade(label="File", underline = 0, menu=fileMenu)

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

        # set window size
        windowSizePos = str(windowWidth) + "x" + str(windowHeight) + "+" + str(windowX) + "+" + str(windowY)
        root.geometry(windowSizePos)

        #init our inputs dict
        inputs = []

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
            #b.grid(column=0, padx = 10, sticky=W)

        # get number of outputs from var and create buttons for each
        # output, each corresponding to a specific projector. When clicked
        # the buttons should send the value of "v" (which designates
        # which input is currently selected) and the output number to our
        # CustomInOut() function.
        logger.debug('====Init outputs====')
        for i in range(int(configParser.get('general', 'numberOfOutputs'))):
            vars()['btnOut' + str(i)] = Button(self, width=15, text="Projector " + str(i + 1), command=lambda i=i: self.setCustomInOut(v.get(), i+1) )
            #vars()['btnOut' + str(i)].grid(row=i, column=2, sticky=E)

        #get our status filled
        #self.getOutputStatus()

    def onExit(self):
        self.quit()

    # ########################
    # (cmd) Get Output Status
    # ########################
    # Same as above but without a lot of gui-specific code.
    # need to just toss that stuff in conditionals lik I do for most of the other functions but eh
    # ########################
    def cmdGetOutputStatus(self):
        inputStat = []
        for output in range(int(configParser.get('general', 'numberOfOutputs'))):
            #lets see if we can open the port
            try:
                com = serial.Serial(
                    port = int(configParser.get('general', 'COMPortNumber'))-1,
                    baudrate = 9600,
                    parity = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_ONE,
                    bytesize = serial.EIGHTBITS,
                    timeout = .4
                )
                #if it is open, then let's send our command
                if com.isOpen():
                    trashResponse = com.read(100)
                    logger.debug("trash: " + trashResponse)
                    com.write('Status' + str(int(output+1)) + '.') # int(string("fuck it")) w
                    time.sleep(0.4)
                    response = com.read(6)
                    currentInput = response[-3:]
                    logger.debug('Output ' + str(output) + '\'s current input:' + str(currentInput))
                    inputStat.append(str(output) + "|" + str(currentInput))
                    # print response
                    com.close()
            #if we were unable to open it then let's log the exception
            except serial.SerialException as ex:
                logger.debug('Port ' + str(int(configParser.get('general', 'COMPortNumber'))-1) + ' is unavailable: ' + ex) # int(string("fuck it")) w
        status = ",".join(inputStat)
        f = open('status.txt','w')
        f.write(status) # python will convert \n to os.linesep
        f.close()
    # ########################
    # (cmd) Custom In/Out function
    # ########################
    # Same as custInOut above, calls cmdGetOutputStatus though so no gui
    # ########################
    def cmdSetCustomInOut(self, input, output):
        logger.debug('====================')
        logger.debug('Set a custom config [cmd]')
        logger.debug(str(input) + 'B' + str(output) + '.')
        logger.debug('====================')
        logger.debug(' ')
        #lets see if we can open the port
        try:
            com = serial.Serial(
                port = int(configParser.get('general', 'COMPortNumber'))-1,
                baudrate = 9600,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize = serial.EIGHTBITS
            )
            #if it is open, then let's send our command
            if com.isOpen():
                com.write(str(input) + 'B' + str(output) + '.')
                com.close()
                self.cmdGetOutputStatus()
        #if we were unable to open it then let's log the exception
        except serial.SerialException as ex:
            logger.debug('Port ' + str(int(configParser.get('general', 'COMPortNumber'))-1) + ' is unavailable: ' + ex)
            
def main():
    root.withdraw()
    # ########################
    # Argument Parser
    # ########################
    # Pulls arguments and decides which function to call
    # arv[0] is the program itself, in that "avcontrol.exe gui",
    # [0] is avcontrol.exe and [1] is gui
    # ########################
    m = Master(root)
    if len(sys.argv) > 1:
        parsed = sys.argv[1]
    else:
        parsed = None


    logger.debug(''.join(sys.argv))

    #spiffy case/switch implimentation from http://code.activestate.com/recipes/410692/
    for case in switch(parsed):
        if case('projOn'):
            logger.debug('Projectors On | CMD')
            m.projectorsOn()
            break
        if case('custInOut'):
            # Usage:
            # avcontrol.exe custInOut input output
            logger.debug('custInOut | CMD')
            m.cmdSetCustomInOut(sys.argv[2],sys.argv[3])
            break
        if case('stanInOut'):
            logger.debug('stanInOut | CMD')
            m.standardInOut(False)
            break
        if case('bmnToAll'):
            m.bmnToAll(False)
            break
        if case('status'):
            logger.debug('status')
            m.cmdGetOutputStatus()
            break
        if case('gui'):
            logger.debug('gui')
            app = Master(root)

            app.initUI()
            root.mainloop()
            break
        if case('help'):
            helptext = ("AV Control Version 1.2.0 \n"
                        "Management interface for the Ani-Mod video matrix and certain Casio projectors\n\n"
                        "Copyright (C) 2014 BMA, Inc.\n"
                        "License MIT <http://opensource.org/licenses/MIT>\n"
                        "This is free software: you are free to change and redistribute it.\n"
                        "There is NO WARRANTY, to the extent permitted by law.\n\n"
                        "Valid options:\n"
                        "\tprojOn\n"
                        "\t\tTurns on all projectors, starting with a host on a certain\n"
                        "\t\tsubnet, both specified in the config.conf. Continues for a\n"
                        "\t\tnumber of projectors specified in the config.conf. All \n"
                        "\t\tprojector hosts must be in sequential order on the same subnet.\n\n"
                        "\tcustInOut input output (where 'input' and 'output' are integer values)\n"
                        "\t\tSets the specified input as the specified output's source.\n"
                        "\t\tThere is not yet any validation so out-of-bounds values are\n"
                        "\t\tstill accepted and just won't do anything.\n\n"
                        "\tstanInOut\n"
                        "\t\tSets all outputs to the standard configuration of\n"
                        "\t\t[BMN, DTV1, BMN, DTV2, BMN, DTV3, ...], limited by number\n"
                        "\t\tof outputs in the house.\n\n"
                        "\tbmnToAll\n"
                        "\t\tSets the BMN input as the source to all outputs.\n\n"
                        "\tstatus\n"
                        "\t\tReads the current input from each output\n\n"
                        "\tgui\n"
                        "\t\tBrings up the old barebones graphical user interface\n\n\n"
                        "Report bugs to: jesse@dassle.us\n"
                        "Software Github Page: <http://github.com/acostoss/Ani-Mod-Matrix-Control/>")
            sys.stdout.write(helptext)
            break
        if case(): # default, could also just omit condition or 'if True'
            if len(sys.argv) > 1: #unknown argument given, and we know there is at least one
                args = ", ".join(sys.argv[1:])
                sys.stdout.write("Invalid argument(s) given: '" + args + "'\nPlease use the 'help' argument for a list of accepted arguments")
            else: #unknown argument given, is actually just empty
                sys.stdout.write("No argument given. Please use the 'help' argument for a list of accepted arguments")
            # No need to break here, it'll stop anyway



if __name__ == '__main__':
    main()
