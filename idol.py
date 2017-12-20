#!/usr/bin/env python
#title          : idol.py
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

# Idol projection software

import serial
import configparser
import logging
import sys
import time
import http.client
import urllib.request, urllib.parse, urllib.error
import random
#from DirectPy import DIRECTV


# make vars
# comNum, bmnNum, numOut, com, v, COMPortNumber, BowlingMusicNetworkInputNumber, screenWidth, screenHeight

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

# commandBuilder

# getAllOutputStatus
# getSingleOutputStatus
# musicToAll
# standardScene
# standardSceneThrees
# customScene
# projectorsOn

class idol:
    def __init__(self, matrixCom, matrixType, musicSource, dtvSources, numberOfTargets):
#        self.matrixCom = serial.Serial(
#                port = 'COM' + str(matrixCom),
#                baudrate = 9600,
#                parity = serial.PARITY_NONE,
#                stopbits = serial.STOPBITS_ONE,
#                bytesize = serial.EIGHTBITS
#            )
        self.matrixType = matrixType
        self.musicSource = musicSource
        self.dtvSources = dtvSources
        self.numberOfTargets = numberOfTargets
    
    def _buildSingleSourceCommand(self,source,targets):
        # Takets a single source (input) and a list of targets (outputs) and generates a list of the command for them for whichever matrix you're using
        commandList = []
        if self.matrixType == "animod":
            commandBase = str(source) + "B"
            for target in targets:
                commandBase += str(target) + ", "
            command = commandBase[:-2] + "."
        elif self.matrixType == "wolf":
            commandBase = "x" + str(source) + "X" 
            for target in targets:
                commandBase += "x" + str(target) + "&"
            command = commandBase[:-1] + "."
        
        commandList.append(command)
        return commandList
    
    def _buildMultiSourceCommand(self,sources,targets):
        commandList = []
        #['1B1.', '7B2.', '1B3.', '1B4.', '7B5.', '1B6.', '1B7.', '7B8.', '1B9.']
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
                com.write(bytes(command, 'UTF-8'))
            except serial.SerialException as ex:
                logger.error('Port ' + str(comNum-1) + ' is unavailable: ' + ex)
    
        # NEEDS WORK
        # NEEDS WORK
        # NEEDS WORK
        # NEEDS WORK
        # NEEDS WORK
        # NEEDS WORK
        # NEEDS WORK
        # NEEDS WORK
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
        #self._sendSerial(self.matrixCom,musicOutCommands)
        #self._sendSerial(self.matrixCom,dtvOutCommands)


        
        
    def standardSceneThrees(self):
        # l = [1,2,3,4,5,6,7,8,9]
        # for i in l[1::3]:
        #     print(i)
        # >>> 2,5,8
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
        #self._sendSerial(self.matrixCom,musicOutCommands)
        #self._sendSerial(self.matrixCom,dtvOutCommands)
