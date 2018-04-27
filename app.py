# 杯ども、それはかすかな目です！！！
# or i guess miku is a better projected idol than kizuna ai huh



#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from flask import Flask, render_template, request, Response, Markup
import idol
import traceback
import configparser
import logging

configparser = configparser.RawConfigParser()
configFilePath = r'config.conf'
configparser.read(configFilePath)

matrixCom = configparser.get('general', 'matrixCom')
matrixType = configparser.get('general', 'matrixType')
musicSource = configparser.get('general', 'musicSource')
dtvSources = configparser.get('general', 'dtvSources').split(",")
sourceNames = configparser.get('general', 'sourceNames').split(",")
numberOfTargets = configparser.get('general', 'numberOfTargets')
projectorLayout = configparser.get('general', 'projectorLayout') # "twos" or "threes"
zones = configparser.get('general', 'zones')
numberOfZones = len(zones.split(','))
zoneNames = configparser.get('general', 'zoneNames').split(",")



# hook into the logger
logger = idol.logger

# initialize our flask app
app = Flask(__name__)

# initialize an idol instance with our config info
miku = idol.idol(matrixCom,matrixType,musicSource,dtvSources,numberOfTargets,zones)

# set our base template data w/ config info
templateData = {'oi' : 'wassup', 'numberOfTargets' : int(numberOfTargets), 'numberOfSources' : len(sourceNames), 'dtvSources' : dtvSources, 'sourceNames' : sourceNames, 'numberOfZones': numberOfZones, 'zoneNames': zoneNames}

# home
@app.route('/')
def main():
    # Pass the template data into the template index.html and return it to the user
    try:
        del templateData['message']
    except:
        pass
    
    return render_template('index.html', **templateData)

# scene selection
@app.route('/scene/<number>')
def scene(number):
    # depending on our projector layout, set different scenes
    if projectorLayout == "threes":
        # depending on which scene was called, run a different idol function
        if number == '1':
            # in scene 1, we run the twos standard scene, which looks like Music | DTV1 | Music | DTV2| Music ...
            miku.standardScene()
            templateData['message'] = "Ran standard scene for twos"
        elif number == '2':
            # in scene 2, we run the twos standard scene, which looks like Music | DTV1 | Music | Music | DTV2 | Music ...
            miku.standardSceneThrees()
            templateData['message'] = "Ran standard scene for threes"
        elif number == '3':
            # in scene 3, we run music videos across the house
            miku.singleSourceScene(int(1))
            templateData['message'] = "Ran scene 3, music across the house"
        elif number == '4':
            # in scene 4 we run logos across the house
            miku.singleSourceScene(int(12))
            templateData['message'] = "Ran scene 4, logos across the house"
        elif number == '5':
            # in scene 5, we have our first multi-command scene. This sets our first 3 zones (main lanes) to logos and our 4th zone (VIP) to music videos
            miku.singleSourceZone(11,0) # MMS2 (logos) to zone 1
            miku.singleSourceZone(11,1) # MMS2 (logos) to zone 2
            miku.singleSourceZone(11,2) # MMS2 (logos) to zone 3
            miku.singleSourceZone(0,3) # music to zone 4 (vip)
            templateData['message'] = "Ran scene 5, logos in main and videos in vip"
        elif number == '6':
            # in scene 6, our first two zones show logos and our second two zones show videos
            miku.singleSourceZone(11,0) # MMS2 (logos) to zone 1
            miku.singleSourceZone(11,1) # MMS2 (logos) to zone 2
            miku.singleSourceZone(0,2) # music to zone 3
            miku.singleSourceZone(0,3) # music to zone 4 (vip)
            templateData['message'] = "Ran scene 6, logos in first half and videos in second"
        else:
            templateData['errorMessage'] = "That's not a valid scene, please try 1-5"
            traceback.print_exc()
    elif projectorLayout == "twos":
        if number == '1':
            miku.standardScene()
        elif number == '2':
            miku.standardSceneThrees()
        elif number == '3':
            miku.musicAllScene()
        elif number == '4':
            miku.singleSourceScene(int(musicSource))
        elif number == '5':
            miku.standardSceneThrees()
        else:
            templateData['errorMessage'] = "That's not a valid scene, please try 1-5"
            traceback.print_exc()
    return render_template('index.html', **templateData)

# neither built nor exposed on the page, but will be able to turn off power to the matrix either via serial or a wifi plug, depending on matrix model
@app.route('/matrix/<control>')
def matrix(control):
    templateData = {'number': 'iunno man'}
    if control == "on":
        miku.poweron()
    elif control == "off":
        miku.poweroff()
    else:
        templateData['errorMessage'] = "That's not a valid control, please try on or off"
    
    return render_template('index.html', **templateData)

#set an individual projector to a specific source
@app.route('/customScene/<source>/<target>')
def customScene(source, target):
    logger.debug('Source is: ' + str(source))
    logger.debug('Target is: ' + str(target))
    source = int(source) + 1
    target = int(target) + 1
    miku.customScene(source,target)
    
    templateData['message'] = "Sent source #" + str(int(source) + 1) + " to target #" + str(int(target) + 1)
    
    return render_template('index.html', **templateData)

#set a single surce for all projectors    
@app.route('/singleSourceAll/<source>')
def singleSourceAll(source):
    logger.debug('Source is: ' + str(source))
    source = int(source) + 1
    miku.singleSourceScene(int(source)+1)
    
    templateData['message'] = "Sent " + sourceNames[int(source)] + " to all targets"
    
    return render_template('index.html', **templateData)

@app.route('/singleSourceZone/<source>/<zone>')
def singleSourceZone(source, zone):
    source = int(source) + 1
    logger.debug('Source is: ' + str(source))
    logger.debug('Zone is: ' + str(zoneNames[int(zone)]))
    miku.singleSourceZone(source,zone)
    templateData['message'] = "Sent " + sourceNames[int(source)-1] + " to " + zoneNames[int(zone)]
    return render_template('index.html', **templateData)

@app.route('/aidoru/')
def aidoru():
    templateData['message'] = ""
    return render_template('aidoru.html', **templateData)
    
if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run(debug=True, host='0.0.0.0')