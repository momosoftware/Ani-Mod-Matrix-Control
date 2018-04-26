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
# projectorsOn

class idol:
    def __init__(self, matrixCom, matrixType, musicSource, dtvSources, numberOfTargets):
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
    
    def _buildSingleSourceCommand(self,source,targets):
        # Takets a single source (input) and a list of targets (outputs) and generates a list of the command for them for whichever matrix you're using
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
        
        commandList.append(command)
        return commandList
    
    def _buildMultiSourceCommand(self,sources,targets):
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
        for command in commands:
            try:
                try: 
                    com.open()
                except:
                    logger.debug('Port is already open')
                com.write(bytes(command, 'UTF-8'))
                sleep(0.1)
                com.close()
            except serial.SerialException as ex:
                logger.error('Port is unavailable: ' + ex)
    

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
    
    # will replace this with singleSourceScene once i rewrite the dict-based case-switch statement into a n if elseif else statement
    def musicAllScene(self):
        targets = []
        numberOfTargets = int(self.numberOfTargets)
        for target in range(numberOfTargets):
            # our current target ID is the number of the actual button that would be pressed on the matrix, which will be one more than our target value, as the range counts from zero and the physical matrix counts from 1
            currentTargetID = target + 1
            targets.append(currentTargetID)
        command = self._buildSingleSourceCommand(self.musicSource, targets)
        logger.debug(command)
        self._sendSerial(self.matrixCom, command)

    def customScene(self, source, target):
        targets = []
        targets.append(target)
        musicOutCommand = self._buildSingleSourceCommand(source, targets)
        logger.debug("Music command: " + str(musicOutCommand))
        self._sendSerial(self.matrixCom, musicOutCommand)

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
    # TODO:
    # - starting with a projStartingIP, take numOfProj variable amount
    #   iterate through a for loop and turn all projectors on.
    # - Do something similar to turn them off.
    # - Another function for turning on/off a single projector
    # - one for status
    # - oh and properly comment the function
    # ########################
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
