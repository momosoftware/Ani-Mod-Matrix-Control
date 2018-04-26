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

app = Flask(__name__)
miku = idol.idol(matrixCom,matrixType,musicSource,dtvSources,numberOfTargets)
templateData = {'oi' : 'wassup', 'numberOfTargets' : int(numberOfTargets), 'numberOfSources' : len(sourceNames), 'dtvSources' : dtvSources, 'sourceNames' : sourceNames}

@app.route('/')
def main():
    # Pass the template data into the template index.html and return it to the user
    try:
        del templateData['message']
    except:
        pass
    
    return render_template('index.html', **templateData)


@app.route('/scene/<number>')
def scene(number):
    #i need to turn this into an if ifelse else statement
    if projectorLayout == "threes":
        if number == '1':
            miku.standardScene()
            templateData['message'] = "Ran standard scene for twos"
        elif number == '2':
            miku.standardSceneThrees()
            templateData['message'] = "Ran standard scene for threes"
        elif number == '3':
            miku.musicAllScene()
            templateData['message'] = "Ran the music all scene"
        elif number == '4':
            miku.singleSourceScene(int(12))
            templateData['message'] = "Ran the single source scene with MMS2 source"
        elif number == '5':
            miku.standardSceneThrees()
            templateData['message'] = "Ran scene 5, standard scene threes"
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

@app.route('/customScene/<source>/<target>')
def customScene(source, target):
    print('Source is: ' + str(source))
    print('Target is: ' + str(target))
    source = int(source) + 1
    target = int(target) + 1
    miku.customScene(source,target)
    
    templateData['message'] = "Sent source #" + str(int(source) + 1) + " to target #" + str(int(target) + 1)
    
    return render_template('index.html', **templateData)
    
@app.route('/singleSourceAll/<source>')
def singleSourceAll(source):
    print('Source is: ' + str(source))
    miku.singleSourceScene(int(source)+1)
    
    templateData['message'] = "Sent " + sourceNames[int(source)] + " to all targets"
    
    return render_template('index.html', **templateData)

@app.route('/aidoru/')
def aidoru():
    templateData['message'] = ""
    return render_template('aidoru.html', **templateData)
    
if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run(debug=True, host='0.0.0.0')