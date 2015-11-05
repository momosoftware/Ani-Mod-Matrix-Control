#!/usr/bin/env python
#title          : ProjectorControl.py
#description    : Management interface for the Ani-Mod video matrix, Casio Projectors
#author         : Jesse "acostoss" Hamilton
#date           : 2014-09-24
#version        : 1.5.2
#usage          : python setup.py py2exe
#notes          : Tested in Windows 7 Pro and 8.1 Pro, should work wherever python works
#todo           : add program status bar to bottom of window
#               : add directv
#pythonVersion  : 3.4.3
#===============================================================================

from tkinter import *
import serial
import threading
import configparser
import logging
import sys
import time
import http.client
import urllib.request, urllib.parse, urllib.error
import random
from win32api import GetSystemMetrics
from DirectPy import DIRECTV


global comNum, bmnNum, numOut, com, v, COMPortNumber, BowlingMusicNetworkInputNumber, screenWidth, screenHeight


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
configparser = configparser.RawConfigParser()
configFilePath = r'config.conf'
configparser.read(configFilePath)

# pull config values from the file to
# fill our comNum and bmnNum globals
comNum = configparser.get('general', 'COMPortNumber')
bmnNum = configparser.get('general', 'BowlingMusicNetworkInputNumber')
numOut = configparser.get('general', 'numberOfOutputs')

# initialize our gui
root = Tk()

root.iconbitmap('avicon.ico')

# init the variable to be used by our radio buttons to determine which input was selected
v = StringVar()
v.set("1") # default it to 1, the first input

class Master(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    # ########################
    # Get Output Status
    # ########################
    # Grabs current input number for each output
    # and prints to a label in the same row
    # as the output button.
    # ########################
    def getOutputStatus(self):
        logger.debug('====Init Status====')
        generateOutputs = configparser.get('general', 'generateOutputs')
        if generateOutputs != "True":
            customOutputs = configparser.get('general', 'customOutputs')
            outputNames = customOutputs.split(',')
            numOut = len(outputNames)
            logger.debug("number of outputs= " + str(numOut))
        
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
            

        for output in range(int(numOut)):
            #lets see if we can open the port
            try:
                com = serial.Serial(
                    port = int(comNum)-1,
                    baudrate = 9600,
                    parity = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_ONE,
                    bytesize = serial.EIGHTBITS,
                    timeout = .4
                )
                #if it is open, then let's send our command
                if com.isOpen():
                    trashResponse = com.read(100)
                    logger.debug("trash: " + trashResponse.decode('UTF-8'))
                    com.write(bytes('Status' + str(int(output+1)) + '.', 'UTF-8'))  # int(string("fuck it")) w
                    time.sleep(0.4)
                    response = com.read(6)
                    currentInput = response[-3:]
                    logger.debug('Output ' + str(output) + '\'s current input:' + str(currentInput))
                    w = Label(self, text=currentInput, relief=SUNKEN, width=5).grid(row=output, padx = 5,  column=1)
                    # print response
                    com.close()
            #if we were unable to open it then let's log the exception
            except serial.SerialException as ex:
                logger.debug('Port ' + str(int(comNum)-1) + ' is unavailable: ' + ex) # int(string("fuck it")) w
        try:
            notFirstRun
        except NameError:
            logger.debug('==Still First Run==')
        else:
            logger.debug('==Kill the modal!==')
            root.deiconify()
            statusModal.grab_release()
            statusModal.destroy()
        notFirstRun = True
        
    def getSingleOutputStatus(self, reqOutput):
        logger.debug('================')
        logger.debug('Get status for output #' + str(reqOutput + 1))
        logger.debug('================')
        
        try:
            com = serial.Serial(
                port = int(comNum)-1,
                baudrate = 9600,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize = serial.EIGHTBITS,
                timeout = .4
            )
            #if it is open, then let's send our command
            if com.isOpen():
                trashResponse = com.read(100)
                logger.debug("trash: " + trashResponse.decode('utf-8'))
                com.write(bytes('Status' + str(int(reqOutput)) + '.', 'UTF-8')) # int(string("fuck it")) w
                logger.debug('Status' + str(int(reqOutput+1)) + '.')
                time.sleep(0.4)
                response = com.read(6)
                currentInput = response[-3:]
                logger.debug('Output ' + str(reqOutput) + '\'s current input:' + str(currentInput))
                w = Label(self, text=currentInput, relief=SUNKEN, width=5).grid(row=reqOutput-1, padx = 5,  column=1)
                # print response
                com.close()
        #if we were unable to open it then let's log the exception
        except serial.SerialException as ex:
            logger.debug('Port ' + str(int(comNum)-1) + ' is unavailable: ' + ex) # int(string("fuck it")) w
        

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
                com.write(bytes(str(bmnNum) + 'All.', 'UTF-8'))
                com.close()
                #get our status refilled
                self.getOutputStatus()
        #if we were unable to open it then let's log the exception
        except serial.SerialException as ex:
            logger.debug('Port ' + str(int(comNum)-1) + ' is unavailable: ' + ex)

    # ########################
    # Standard In Out Odd
    # ########################
    # need to rewrite it to split into groups by a 
    # divisor and output to those in even/odd, but 
    # for now we'll just do it the manual way to 
    # get it done and in production at the center
    # ########################
    def standardInOutOdd(self):
        logger.debug('====================')
        logger.debug('Set standard AV config odd')
        outputList = ['1B1.', '7B2.', '1B3.', '1B4.', '7B5.', '1B6.', '1B7.', '7B8.', '1B9.']
        logger.debug(outputList)
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
                for output in outputList:
                    com.write(bytes(str(output), 'UTF-8'))
            com.close()
        #if we were unable to open it then let's log the exception
        except serial.SerialException as ex:
            logger.debug('Port ' + str(int(comNum)-1) + ' is unavailable: ' + ex)

        time.sleep(0.5)
        self.getOutputStatus() #refresh our status
        
    def standardInOut(self):
        logger.debug('====================')
        logger.debug('Set standard AV config')
        #start with 1
        currentInput = 1
        numIn = configparser.get('general', 'numberOfInputs')
        # define our Bowling Music Input
        bmnIn = configparser.get('general', 'bowlingMusicNetworkInputNumber')
        #iterate through the loop a number of times equal to our number of outputs

        inOuts = []

        # then fill it, naming it DTV# where # is the input number,
        # unless it is # matches the bowling music input number (bmnIn)
        # at which point we name it Bowling Music

        for i in range(int(numOut)):
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
                inOuts.append([bmnNum, i + 1])


        logger.debug('====================')
        logger.debug(' writing inOuts')
        logger.debug('====================')
        logger.debug(inOuts)

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
                for input, output in inOuts:
                    com.write(bytes(str(input) + 'B' + str(output) + '.', 'UTF-8'))
                    logger.debug(str(input) + 'B' + str(output) + '.')
                com.close()
        #if we were unable to open it then let's log the exception
        except serial.SerialException as ex:
            logger.debug('Port ' + str(int(comNum)-1) + ' is unavailable: ' + ex)

        time.sleep(0.5)
        self.getOutputStatus() #refresh our status

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
                port = int(comNum)-1,
                baudrate = 9600,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize = serial.EIGHTBITS
            )
            #if it is open, then let's send our command
            if com.isOpen():
                com.write(bytes(str(input) + 'B' + str(output) + '.', 'UTF-8'))
                com.close()
                self.getSingleOutputStatus(output)
        #if we were unable to open it then let's log the exception
        except serial.SerialException as ex:
            logger.debug('Port ' + str(int(comNum)-1) + ' is unavailable: ' + ex)


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

        projSubnet = configparser.get('general', 'projectorSubnet')
        projHost = configparser.get('general', 'projectorStartingHost')
        currentProjHost = int(projHost)
        for i in range(int(numOut)):
            projIP = "192.168." + str(projSubnet) + "." + str(currentProjHost)
            #Projector off  command=24003100    0f0001010003010002
            #Status         command=24003100    0e00023100000000
            logger.debug("URL: " + projIP)
            projCMD = "command=24003100    0f0001010003010001"
            params = urllib.parse.urlencode({'@number': 12524, '@type': 'issue', '@action': 'show'})
            headers = {"Content-Type": "application/x-www-form-urlencoded", "Cache-Control": "no-cache"}
            logger.debug(headers)
            projCON = http.client.HTTPConnection(projIP)
            projCON.request("POST", "/tgi/return.tgi?sid=" + str(random.random()), projCMD, headers)
            projRESP = projCON.getresponse()
            logger.debug(projRESP.status)
            logger.debug(projRESP.reason)
            data = projRESP.read()
            logger.debug(data)
            projCON.close()

            currentProjHost = currentProjHost + 1

    def initUI(self):
        # set window title
        self.parent.title("Projector Control")
        
        
        oddOuts = configparser.get('general', 'oddOuts')

        # init menubar
        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)

        # fill menubar with items
        fileMenu = Menu(menubar)
        sceneMenu = Menu(fileMenu)
        projMenu = Menu(fileMenu)
        
        
        if oddOuts == "true":
            sceneMenu.add_command(label="Standard setup", command=self.standardInOutOdd)
        else:
            sceneMenu.add_command(label="Standard setup", command=self.standardInOut)
            
        sceneMenu.add_command(label="Bowling Music to all", command=self.bmnToAll)
        
        fileMenu.add_cascade(label="Scenes", underline = 0, menu=sceneMenu)

        projMenu.add_command(label="Turn on projectors", underline = 0, command=self.projectorsOn)
        fileMenu.add_cascade(label="Projectors", underline = 0, menu=projMenu)

        fileMenu.add_separator()

        fileMenu.add_command(label="Refresh", command=self.getOutputStatus)

        fileMenu.add_separator()

        fileMenu.add_command(label="Exit", underline = 0, command=root.quit())
        menubar.add_cascade(label="File", underline = 0, menu=fileMenu)



        self.pack(fill=BOTH, expand=1)
        self.var = IntVar()

        # pull number of inputs, number of bmns, 
        # and which input number the bmns start at for use in initUI
        logger.debug('==Read config file==')
        numIn = configparser.get('general', 'numberOfInputs')
        bmnStart = configparser.get('general', 'bowlingMusicNetworkInputNumber')
        bmnCount = configparser.get('general', 'numberOfBMN')
        
        # Center window by getting screensize from Windows
        # dividing by 2, then subtracting windowsize/2
        screenWidth = int(GetSystemMetrics (0))
        screenHeight = int(GetSystemMetrics (1))

        windowWidth = int(configparser.get('general', 'windowWidth'))
        windowHeight = int(configparser.get('general', 'windowHeight'))

        windowX = screenWidth/2 - windowWidth/2
        windowY = screenHeight/2 - windowHeight/2

        # set window size
        windowSizePos = str(windowWidth) + "x" + str(windowHeight) + "+" + str(int(windowX)) + "+" + str(int(windowY))
        root.geometry(windowSizePos)

        #init our inputs list then fill it
        logger.debug('=====Init input=====')
        inputs = []
        generateInputs = configparser.get('general', 'generateInputs')
        if generateInputs == "True":
            inputIterable = iter(list(range(int(numIn)+ 1)))
            for i in inputIterable:
                logger.debug('iterable turn ' + str(i))
                if i + 1 == int(bmnStart):
                    logger.debug('i == bmnStart')
                    for bmn in range(int(bmnCount)):
                        inputs.append(['Bowling Music ' + str(int(bmn) + int(bmnStart)), str(int(bmn) + int(bmnStart))]) #i hate myself for this
                        logger.debug('Bowling Music ' + str(int(bmn) + int(bmnStart)))
                        next(inputIterable)
                else:
                    inputs.append(['DTV' + str(i - int(bmnCount)), str(i)]) 
        else:
            customInputs = str(configparser.get('general', 'customInputs'))
            inputNames = customInputs.split(',')
            logger.debug("custom inputs = ")
            logger.debug(inputNames)

        # take our list of inputs and make radio buttons for them,
        # storing the value in the variable "v" that we initialized earlier
        
        logger.debug(inputs)
        
        inputNums = []
        
        if generateInputs != "True":
            inputNums = list(range(len(inputNames)))
            inputs = dict(zip(inputNames, inputNums))
            logger.debug(inputs)
            for text, input in inputs.items():
                row = int(input)
                b = Radiobutton(self, text=text, variable=v, value=str(int(input) + 1))
                b.grid(row=row, column=0, padx = 10, sticky=W)
        else:
            for text, input in inputs:
                row = int(input) - 1
                b = Radiobutton(self, text=text, variable=v, value=input)
                b.grid(row=row, column=0, padx = 10, sticky=W)
                

        # get number of outputs from var and create buttons for each
        # output, each corresponding to a specific projector. When clicked
        # the buttons should send the value of "v" (which designates
        # which input is currently selected) and the output number to our
        # CustomInOut() function.
        logger.debug('====Init outputs====')
        generateOutputs = configparser.get('general', 'generateOutputs')
        if generateOutputs != "True":
            customOutputs = str(configparser.get('general', 'customOutputs'))
            outputNames = customOutputs.split(',')
            outputNums = list(range(len(outputNames)))
            outputs = dict(zip(outputNames, outputNums))
            for text, output in outputs.items():
                vars()['btnOut' + str(output + 1)] = Button(self, width=15, text=text, command=lambda output=output: self.setCustomInOut(v.get(), output+1) )
                vars()['btnOut' + str(output + 1)].grid(row=output, column=2, sticky=E)
        else:
            for i in range(int(numOut)):
                vars()['btnOut' + str(i)] = Button(self, width=15, text="Projector " + str(i + 1), command=lambda i=i: self.setCustomInOut(v.get(), i+1) )
                vars()['btnOut' + str(i)].grid(row=i, column=2, sticky=E)

        #get our status filled
        self.getOutputStatus()

        def onExit(self):
            self.quit()

def main():

    app = Master(root)
    root.mainloop()


if __name__ == '__main__':
    main()