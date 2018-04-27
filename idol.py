#!/usr/bin/env python
#title          : idol.py
#description    : Management interface for the Ani-Mod video matrix, Casio Projectors
#author         : Jesse "acostoss" Hamilton
#date           : 2018-01-31
#version        : 2.0.1
#usage          : python app.py
#notes          : Tested in Windows 7 Pro and 8.1 Pro, should work wherever python works
#todo           : see above class definition
#pythonVersion  : 3.6.1
#===============================================================================

# Idol projection software

import serial
import configparser
import logging
import sys
from time import sleep
import http.client
import urllib.request, urllib.parse, urllib.error
import random
#from DirectPy import DIRECTV


# load our config and prepare to read the file
configparser = configparser.RawConfigParser()
configFilePath = r'config.conf'
configparser.read(configFilePath)


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

# TODO
# musicToAll - this is done now actually
# projectorsOn https://puu.sh/AbAPH/76fb9cd73f.png 

class idol:
    def __init__(self, matrixCom, matrixType, musicSource, dtvSources, numberOfTargets, zones):
        """ 
        Initialize the idol class 

        Initializes the idol class and does some prep work for the class functions, such as defining
        the matrix com port options, defining our zones from the config string, and defining other
        oprions passed from the config file

        Parameters
        ----------
        matrixCom : string
            Contains the COM port that the matrix is on. 
            In the format of the device path on linux (/dev/ttyUSB0) or the com device name in windows (COM1) 
            (Currently unused)
        matrixType : string
            String  containing the type of matrix we're targetting. This informs how commands are built before
            sending them to the com port. 
        musicSource : int
            Int containing the source that our music videos are attached to, used for some scene functions.
        dtvSources : list
            List of ints containing all sources with directTV boxes on them. Used to inform some scene functions
            that need to loop through all DTV sources multiple times without including other sources
        numberOfTargets : int
            Total number of targets we can point sources to, used in a variety of places including scene functions,
            web page generation functions, and to limit what targets we can point sources to (to avoid pissing off
            the video matrix)
        zones : string
            String in the format of `start1-end1,start2-end2,...` where start and end are ints representing target
            ranges to be defined as zones. Used to send out sources to a range of user-defined zones without having 
            to send to all define these zones during each use or to send out sources to targets one by one. Is split
            into a list of lists containing ints of all numbers in each range during the initialization of the class

        Returns
        -------
        commandList : list
            Returns a list of strings, commands built by the function to tell the matrix which source to 
            put to which targets. Expect one list value for each target passed to the function

        Todo
        ----
        Allow usage of com set in config
            Need to use the matrixCom value in the general section of the config for the com port definition
        """
        self.matrixCom = serial.Serial(
                port = '/dev/ttyUSB0',
                baudrate = 9600,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize = serial.EIGHTBITS
            )
        self.matrixType = matrixType
        self.musicSource = musicSource
        self.dtvSources = dtvSources
        self.numberOfTargets = numberOfTargets
        self.zoneLanes = []
        for zone in zones.split(','):
            lanes = list(map(int, zone.split('-')))
            self.zoneLanes.append(list(range(lanes[0],lanes[1]+1)))

    
    def _buildSingleSourceCommand(self,source,targets):
        """ 
        Single source to multiple targets helper class

        Build a command using a single source and one or more targets for the matrix defined in the config file

        Parameters
        ----------
        source : int
            The source that we wish to direct each of the targets to display
        targets : list
            A list of targets we wish to have directed to the source

        Returns
        -------
        commandList : list
            Returns a list of strings, commands built by the function to tell the matrix which source to 
            put to which targets. Expect one list value for each target passed to the function

        """
        commandList = []
        if self.matrixType == "animod":
            for target in targets:
                command = str(source) + "B" + str(target) + "."
                commandList.append(command)
        elif self.matrixType == "wolf":
            commandBase = "x" + str(source) + "X" 
            for target in targets:
                commandBase += "x" + str(target) + "&"
            command = commandBase[:-1] + "."
        
        return commandList
    
    def _buildMultiSourceCommand(self,sources,targets):
        """ 
        Multiple sources to multiple targets helper class

        Build a command using multiple sources and multiple targets for the matrix defined in the config file.
        Just kinda zippers them together, first source to first target, second source to second target, etc. If
        it runs out of sources, it loops back around to the first until all targets have a source

        Parameters
        ----------
        source : list
            A list of the sources that we wish to direct the targets to display
        targets : list
            A list of targets we wish to have directed to the sources

        Returns
        -------
        commandList : list
            Returns a list of strings, commands built by the function to tell the matrix which source to 
            put to which target. Expect one list value for each target list item passed to the function

        """
        commandList = []
        for target in targets:
            index = targets.index(target)
            if self.matrixType == "animod":
                command = str(sources[index]) + "B" + str(target) + "."
            elif self.matrixType == "wolf":
                command = "x" + str(sources[index]) + "X" + "x" + str(target) + "."
        
            commandList.append(command)
        
        return commandList

    
    def _sendSerial(self,com,commands):
        """ 
        Serial command sender helper class

        Takes a list of commands and a pyserial object, iterates through the list of commands,
        opens the serial deivce, writes the command, waits approx 1/3rd of a second, closes the device,
        then continues with the next command.

        Parameters
        ----------
        com : pyserial object
            The pyserial object we'll be using to send commands to the matrix
        targets : list
            A list of commands we wish to send to the matrix

        """
        logger.debug('Sending commands')
        for command in commands:
            logger.debug('Sending command: ' + command)
            try:
                try: 
                    com.open()
                except:
                    logger.debug('Port is already open')
                com.write(bytes(command, 'UTF-8'))
                sleep(0.3)
                com.close()
            except serial.SerialException as ex:
                logger.error('Port is unavailable: ' + ex)
            # for some reason it wont always send the last command unless you open and close the port again????
            sleep(0.2)
            com.open()
            sleep(0.2)
            com.close()
    

    def standardScene(self):
        dtvSources = self.dtvSources
        dtvSourcesStatic = self.dtvSources
        numberOfDTVSources = int(len(dtvSources))
        numberOfTargets = int(self.numberOfTargets)
        logger.debug("Starting number of DTV Sources: " + str(numberOfDTVSources))
        logger.debug("Starting number of Targets: " + str(numberOfTargets))
        while numberOfDTVSources < numberOfTargets:
            diff = numberOfTargets - numberOfDTVSources
            logger.debug("Starting difference: " + str(diff))
            while diff > numberOfDTVSources:
                diff = diff - numberOfDTVSources
                logger.debug("Diff: " + str(diff))
                dtvSources.extend(dtvSourcesStatic)
            
            dtvSources.extend(dtvSourcesStatic[:diff])
            numberOfDTVSources = int(len(dtvSources))
            logger.debug("New Total DTV Sources: " + str(numberOfDTVSources))
            
        musicTargets = []
        dtvTargets = []
        for target in range(numberOfTargets):
            # our current target ID is the number of the actual button that would be pressed on the matrix, which will be one more than our target value, as the range counts from zero and the physical matrix counts from 1
            currentTargetID = target + 1
            # if we divide by 2 is there a remainder? if so, it's odd, if not, even
            if currentTargetID % 2 != 0: #odd, music
                musicTargets.append(currentTargetID)
            else: #even, dtv
                dtvTargets.append(currentTargetID)
            
            
        musicOutCommands = self._buildSingleSourceCommand(self.musicSource, musicTargets)

        dtvOutCommands = self._buildMultiSourceCommand(dtvSources, dtvTargets)
        logger.debug("Music commands: " + str(musicOutCommands))
        logger.debug("dtv commands: " + str(dtvOutCommands))
        self._sendSerial(self.matrixCom,musicOutCommands)
        self._sendSerial(self.matrixCom,dtvOutCommands)


    def standardSceneThrees(self):
        dtvSources = self.dtvSources
        dtvSourcesStatic = self.dtvSources
        numberOfDTVSources = int(len(dtvSources))
        numberOfTargets = int(self.numberOfTargets)
        logger.debug("Starting number of DTV Sources: " + str(numberOfDTVSources))
        logger.debug("Starting number of Targets: " + str(numberOfTargets))
        while numberOfDTVSources < numberOfTargets:
            diff = numberOfTargets - numberOfDTVSources
            logger.debug("Starting difference: " + str(diff))
            while diff > numberOfDTVSources:
                diff = diff - numberOfDTVSources
                logger.debug("Diff: " + str(diff))
                dtvSources.extend(dtvSourcesStatic)
            
            dtvSources.extend(dtvSourcesStatic[:diff])
            numberOfDTVSources = int(len(dtvSources))
            logger.debug("New Total DTV Sources: " + str(numberOfDTVSources))
            
        musicTargets = []
        dtvTargets = []
        for target in range(numberOfTargets):
            musicTargets.append(target+1)
        
        for target in range(numberOfTargets)[1::3]:
            dtvTargets.append(target+1)
            
        musicOutCommands = self._buildSingleSourceCommand(self.musicSource, musicTargets)

        dtvOutCommands = self._buildMultiSourceCommand(dtvSources, dtvTargets)
        logger.debug("Music commands: " + str(musicOutCommands))
        logger.debug("dtv commands: " + str(dtvOutCommands))
        self._sendSerial(self.matrixCom,musicOutCommands)
        self._sendSerial(self.matrixCom,dtvOutCommands)
        
    def singleSourceScene(self,source):
        targets = []
        numberOfTargets = int(self.numberOfTargets)
        for target in range(numberOfTargets):
            # our current target ID is the number of the actual button that would be pressed on the matrix, which will be one more than our target value, as the range counts from zero and the physical matrix counts from 1
            currentTargetID = target + 1
            targets.append(currentTargetID)
        command = self._buildSingleSourceCommand(source, targets)
        logger.debug(command)
        self._sendSerial(self.matrixCom, command)   

    def singleSourceZone(self,source,zone):
        logger.debug('singlesourcezone')
        targets = self.zoneLanes[int(zone)]
        logger.debug(targets)
        command = self._buildSingleSourceCommand(source, targets)
        logger.debug('command')
        logger.debug(command)
        self._sendSerial(self.matrixCom, command)

    def customScene(self, source, target):
        targets = []
        targets.append(target)
        musicOutCommand = self._buildSingleSourceCommand(source, targets)
        logger.debug("Music command: " + str(musicOutCommand))
        self._sendSerial(self.matrixCom, musicOutCommand)


# replacing the old projector on/off code, needs a better name
    def allTargetsCommand(self,command):
        logger.debug("Turning on projectors")
        targetSubnet = configparser.get('general', 'targetSubnet')
        targetHost = configparser.get('general', 'targetStartingHost')
        currentHost = int(targetHost)
        if command == "on":
            targetCommand = "command=24003100    0f0001010003010001"
        elif comand == "off":
            targetCommand = "command=24003100    0f0001010003010002"
        else:
            targetCommand = "command=24003100    0e00023100000000"
        
        for i in range(int(self.numberOfTargets)):
            currentIP = "192.168." + str(targetSubnet) + "." + str(currentHost)
            logger.debug("URL: " + currentP)
            params = urllib.parse.urlencode({'@number': 12524, '@type': 'issue', '@action': 'show'})
            headers = {"Content-Type": "application/x-www-form-urlencoded", "Cache-Control": "no-cache"}
            logger.debug(headers)
            currentCON = http.client.HTTPConnection(currentIP)
            currentCON.request("POST", "/tgi/return.tgi?sid=" + str(random.random()), targetCommand, headers)
            currentRESP = currentCON.getresponse()
            logger.debug("Status:")
            logger.debug(currentRESP.status)
            logger.debug("Reason:")
            logger.debug(currentRESP.reason)
            data = currentRESP.read()
            logger.debug("Data:")
            logger.debug(data)
            currentCON.close()
            
            currentHost = currentHost + 1
