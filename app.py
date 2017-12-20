# haidomo, virtual youtuber kizuna ai desu!
# or i guess miku is a better projected idol huh


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
templateData = {'oi' : 'wassup'}

@app.route('/')
def main():
    # Pass the template data into the template index.html and return it to the user
    return render_template('index.html', **templateData)


@app.route('/scene/<number>')
def scene(number):
    if projectorLayout == "threes":
        scenes = {'1' : miku.standardSceneThrees,
               '2' : miku.standardSceneThrees,
               '3' : miku.standardSceneThrees,
               '4' : miku.standardSceneThrees,
               '5' : miku.standardSceneThrees
        }
    else:
        scenes = {'1' : miku.standardScene,
               '2' : miku.standardScene,
               '3' : miku.standardScene,
               '4' : miku.standardScene,
               '5' : miku.standardScene
        }
    
    try:
        #call our scene from the dict depending on number passed in url
        scenes[number]()  
    except AttributeError:
        templateData['message'] = "That's not a valid scene, please try 1-5"
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
        templateData['message'] = "That's not a valid control, please try on or off"
    
    return render_template('index.html', **templateData)

if __name__ == '__main__':
    app.run(host='0.0.0.0')