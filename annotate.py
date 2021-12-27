#!/usr/bin/python

""" Annotaes and image provided by the allsky software https://github.com/thomasjacquin/allsky 
    
    This script will take various inputs, see the -h option and use these to overlay test and
    images on images captured by the allsky software. It is intended to be used in real-time
    as part of the save image scripts. This script provides far more flexability than the 
    built in systems for adding text to the captured images.
"""

import csv
import re
import os
import ephem
import json
import argparse
import cv2
import re
import sys
import numpy as np
import pathlib

from datetime import datetime
from math import radians
from math import degrees
from datetime import datetime
from datetime import date
from PIL import ImageFont
from PIL import ImageDraw
from PIL import Image
from PIL import ImageColor

__author__ = "Alex Greenland"
__copyright__ = "Copyright 2021, Alex Greenland"
__credits__ = ["The Internet!"]
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Alex Greenland"
__email__ = "alex.greenland@gmail.com"
__status__ = "Alpha"

class ALLSKYANNOTATE:
    """ The main annotater class. Does all of the funky work :-) """
    _allSkyHomeDirectory = None
    _allSkyVariables = None
    _cameraConfig = None
    _scriptPath = None

    _observerLat = "52N"
    _observerLon = "0.2E"
    _moonAzimuth = None
    _moonElevation = None
    _moonIllumination = None
    _moonPhaseSymbol = None

    _configFile = None
    _dataFile = None
    _imageFile = None
    _verbose = False
    _kwargs = None

    _config = None
    _data = {}
    _image = None
    _fonts = {}

    _startTime = 0
    _lastTimer = None

    def __init__(self, configFile, dataFile, imageFile, verbose, kwargs):
        """ Initialise the class """
        self._scriptPath = os.path.dirname(__file__)

        if verbose is not None:
            self._verbose = verbose

        self._configFile = os.path.join(self._scriptPath, "annotate.json")
        if configFile is not None:           
            if self._isFileReadable(configFile):
                self._configFile = configFile
            else:
                self._log("ERROR: Cannot access config file " + configFile)
        self._log("NOTICE: Config file set to " + self._configFile)
        
        if dataFile is not None:
            self._dataFile = dataFile.strip()         
        self._log("NOTICE: Data file set to " + str(self._dataFile))

        if imageFile is not None:
            self._imageFile = imageFile.strip()
        self._log("NOTICE: Image file set to " + str(self._imageFile))

        self._kwargs = kwargs
        self._log("NOTICE: kwars set to " + str(self._kwargs))

    def _log(self, text):
        """ Very simple method to lod data if in verbose mode """
        if self._verbose:
            print(text, file=sys.stdout)

    def _timer(self, text):
        """ Method to display the elapsed time between function calls and the total script execution time """
        if self._verbose:
            if self._lastTimer is None:
                elapsedSinceLastTime = datetime.now() - self._startTime
            else:
                elapsedSinceLastTime = datetime.now() - self._lastTimer
            
            lastText = str(elapsedSinceLastTime.total_seconds())
            self._lastTimer = datetime.now()

            elapsedTime = datetime.now() - self._startTime
            print(text + " took " + lastText + " Seconds. Elapsed Time " + str(elapsedTime.total_seconds()) + " Seconds.")

    def annotate(self):
        """ The main annotater entry point. This is the only public method available """
        if self._verbose:
            if os.path.exists("last.png"):
                os.remove("last.png")        
        self._startTime = datetime.now()
        if self._checkForAllsky():
            self._timer("Finding allsky")
            self._log("NOTICE: allsky found at " + self._allSkyHomeDirectory)
            if self._loadConfigFile():
                self._timer("Loading config")
                if self._loadFonts():
                    self._timer("Loading fonts")            
                    self._initialiseMoon()
                    self._timer("Moon initialisation")            
                    if self._loadDataFile():
                        self._timer("Loading data file")
                        if self._kwargs is not None:
                            for field in self._kwargs:
                                self._data["fields"][field] = self._kwargs[field]
                        else:
                            self._data["fields"]["date"] = "jkj"
                            self._data["fields"]["sensortemp"] = "N/A"
                            self._data["fields"]["exposure"] = "N/A"
                            self._data["fields"]["gain"] = "N/A"
                            self._data["fields"]["brightness"] = "N/A"

                        if self._loadImageFile():
                            self._timer("Loading image file")
                            self._addText()
                            self._timer("Adding text")            
                            self._addImages()
                            self._timer("Adding images")
                            self._saveImagefile()        
                            self._timer("Saving final image")

            self._timer("Processing Complete")

    def _checkForAllsky(self):
        """ Attempts to find the all sky installation. The script will abort if this cannot be found """
        result = True
        try:
            self._allSkyHomeDirectory = os.environ['ALLSKY_HOME']

            with open(self._allSkyHomeDirectory + "/config/config.sh") as stream: # dont hard code dir seps
                contents = stream.read().strip()

            var_declarations = re.findall(r"^[a-zA-Z0-9_]+=.*$", contents, flags=re.MULTILINE)
            reader = csv.reader(var_declarations, delimiter="=")
            self._allSkyVariables = dict(reader)  

            try:
                if self._allSkyVariables["CAMERA"] == "ZWO":
                    camerSettingsFile = "/etc/raspap/settings_ZWO.json"
                else:
                    camerSettingsFile = "/etc/raspap/settings_RPiHQ.json"

                allskySettingsFile = open(camerSettingsFile, 'r')
                self._cameraConfig = json.load(allskySettingsFile)

                self._observerLat = self._cameraConfig["latitude"]
                self._observerLon = self._cameraConfig["longitude"]
            except FileNotFoundError:
                self._log("ERROR: Cannot find the allsky camera config")
                result = False
        except KeyError:
            self._log("ERROR: Cannot find allsky installation")
            result = False

        return result

    def _convertLatLon(self, input):
        """ Converts the lat and lon from the all sky config to decimal notation i.e. 0.2E becomes -0.2"""
        multiplier = 1 if input[-1] in ['N', 'E'] else -1
        return multiplier * sum(float(x) / 60 ** n for n, x in enumerate(input[:-1].split('-')))

    def _initialiseMoon(self):
        """ Setup all of the data for the Moon """
        lat = radians(self._convertLatLon(self._observerLat))
        lon = radians(self._convertLatLon(self._observerLon))

        observer = ephem.Observer()  
        observer.lat = lat
        observer.long = lon 
        moon = ephem.Moon()      
        observer.date = date.today()
        observer.date = datetime.now()        
        moon.compute(observer)  

        nnm = ephem.next_new_moon(observer.date)  
        pnm = ephem.previous_new_moon(observer.date)  

        lunation=(observer.date-pnm)/(nnm-pnm)  
        symbol=lunation*26  
        if symbol < 0.2 or symbol > 25.8 :  
            symbol = '1'  # new moon  
        else:  
            symbol = chr(ord('A')+int(symbol+0.5)-1) 

        azTemp = str(moon.az).split(":")
        self._moonAzimuth = azTemp[0] + u"\N{DEGREE SIGN}"
        self._moonElevation = str(round(degrees(moon.alt),2)) + u"\N{DEGREE SIGN}"
        self._moonIllumination = str(round(moon.phase, 2))
        self._moonPhaseSymbol  = symbol

    def _isFileWriteable(self, fileName):
        """ Check if a file exists and can be written to """
        if os.path.exists(fileName):
            if os.path.isfile(fileName):
                return os.access(fileName, os.W_OK)
            else:
                return False 
        else:
            return False            

    def _isFileReadable(self, fileName):
        """ Check if a file is readable """
        if os.path.exists(fileName):
            if os.path.isfile(fileName):
                return os.access(fileName, os.R_OK)
            else:
                return False 
        else:
            return False  

    def _loadImageFile(self):
        """ Loads the image file to annotate. If no image is specified on the command line
            then this method will attempt to use the image specified in the all sky camera
            config
        """
        result = True
        if self._imageFile is None:
            self._imageFile = os.path.join(self._allSkyHomeDirectory, self._cameraConfig["filename"])

        if self._isFileReadable(self._imageFile):
            if self._isFileWriteable(self._imageFile):
                self._image = cv2.imread(self._imageFile)
                self._log("INFO: Using image file " + self._imageFile)
            else:
                self._log("ERROR: Cannot write to the image file " + self._imageFile)
                result = False
        else:
            self._log("ERROR: Cannot read the image file " + self._imageFile)
            result = False

        return result

    def _saveImagefile(self):
        """ Saves the final image """
        if self._verbose:
            cv2.imwrite(os.path.join(self._scriptPath, "last.png"), self._image, params=None)
        cv2.imwrite(self._imageFile, self._image, params=None)

    def _loadConfigFile(self):
        result = True
        if self._isFileReadable(self._configFile):
            with open(self._configFile) as file:
                self._config = json.load(file)
        
            if len(self._config["fields"]) == 0 and len(self._config["images"]) == 0:
                self._log("WARNING: Config file (" + self._configFile + ") is empty. Did you create a config file? Nothing to do so ABORTING")
                result = False        
        else:
            self._log("ERROR: Config File not accessible " + self._configFile)
            result = False
        
        return result

    def _loadDataFile(self):
        result = True
        self._data["fields"] = {}
        if self._dataFile is not None:
            fileExtension = pathlib.Path(self._dataFile).suffix
            if fileExtension == ".json":
                if self._isFileReadable(self._dataFile):
                    with open(self._dataFile) as file:
                        self._data = json.load(file)
                else:
                    self._log("ERROR: Data File not accessible - ABORTING")
                    result = False
            else:
                if self._isFileReadable(self._dataFile):
                    with open(self._dataFile) as file:
                        for line in file:
                            name, var = line.partition("=")[::2]
                            self._data["fields"][name.strip()] = var   
                else:
                    self._log("ERROR: Data File not accessible - ABORTING")
                    result = False                            
        return result

    def _loadFonts(self):
        fontsLoaded = True
        for index, font in enumerate(self._config["fonts"]):
            fontData = self._config["fonts"][font]
            if self._isFileReadable(fontData["fontPath"]):
                fontPath = fontData["fontPath"]
            else:
                fontPath = os.path.join(self._scriptPath, fontData["fontPath"])
            fontSize = fontData["fontSize"]
            try:
                self._fonts[font] = ImageFont.truetype(fontPath, fontSize)
            except OSError:
                self._log("ERROR: Cannot locate font " + fontPath)
                fontsLoaded = False
        
        return fontsLoaded

    def _addText(self):
        for index, name in enumerate(self._config["fields"]):
            fieldData = self._config["fields"][name]
            if "font" not in fieldData.keys():
                self._processText(name, fieldData)

        pilImage = Image.fromarray(self._image)
        for index, name in enumerate(self._config["fields"]):
            fieldData = self._config["fields"][name]
            if "font" in fieldData.keys():
                pilImage = self._processText(name, fieldData, pilImage)
        self._image = np.array(pilImage)

    def _processText(self, name, fieldData, pilImage = None):
        if "font" in fieldData.keys():
            fontName = fieldData["font"]
        else:
            fontName = None

        fieldX = fieldData["position"]["x"]
        fieldY = fieldData["position"]["y"]
        if "colour" in fieldData.keys():
            fieldColour = fieldData["colour"]
        else:
            fieldColour = "white" 
        
        try:
            r,g,b = ImageColor.getcolor(fieldColour, "RGB")
        except:
            self._log("ERROR: The colour '" + fieldColour + "' for field '" + name + "' Is NOT valid - Defaulting to white")
            r = 255
            g = 255
            b = 255

        if "variable" in fieldData.keys():
            fieldVariable = fieldData["variable"]
            fieldLabel = fieldData["label"]

            fieldValue = None
            if (len(fieldVariable) > 0 and fieldVariable[0] == "%"):
                fieldKey = fieldVariable[1:]
                if fieldKey in self._data["fields"]:
                    fieldValue = str(self._data["fields"][fieldKey])
            else:
                if (len(fieldVariable) > 0 and fieldVariable[0] == "^"):
                    fieldValue = self._getInternalVariable(fieldVariable)                                             
                else:
                    fieldValue = fieldVariable

            if fieldValue is not None:
                fieldString = fieldLabel + fieldValue
                
                if fontName not in self._fonts:
                    self._log("ERROR: Font name '" + fontName + "' not found for field '" + name + "'")
                    fontName = None

                if fontName is None:
                    cv2.putText(self._image, fieldString, (fieldX,fieldY), cv2.FONT_HERSHEY_SIMPLEX, 1, (b,g,r), 1, cv2.LINE_AA)
                else:
                    draw = ImageDraw.Draw(pilImage)
                    font = self._fonts[fontName]
                    a = 0
                    draw.text((fieldX, fieldY), fieldString, font = font, fill = (b, g, r, a))

                self._log("Adding text field " + name + " variable name = '" + fieldVariable + "', value = '" + fieldString + "'")
                self._timer("Adding text field " + name)
            else:
                self._log("ERROR: Adding field " + name + " field value not found.")

        if "file" in fieldData.keys():
            fileName = fieldData["file"]

            if fileName == "":
                fileName = self._cameraConfig["extratext"]

            if self._isFileReadable(fileName):
                fontSize = cv2.getTextSize("dummy", cv2.FONT_HERSHEY_SIMPLEX, 1, 1)
                lineHeight = int(fontSize[0][1] * 1.5)
                if fontName is not None:
                    try:
                        font = self._fonts[fontName]
                        ascent, descent = font.getmetrics()
                        lineHeight = font.getmask("dummy").getbbox()[3] + descent
                    except:
                        self._log("ERROR: Font name '" + fontName + "' not found for field '" + name + "'")
                        fontName = None

                with open(fileName) as file:
                    for line in file:
                        line = line.rstrip()
                        if fontName is None:
                            cv2.putText(self._image, line, (fieldX,fieldY), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (b,g,r), 1, cv2.LINE_AA)
                        else:
                            draw = ImageDraw.Draw(pilImage)
                            a = 0
                            draw.text((fieldX, fieldY), line, font = font, fill = (b, g, r, a))  
                        fieldY = fieldY + lineHeight
                self._log("Adding file " + fileName)
            else:
                self._log("ERROR: Cannot read from extra text file " + fileName)

        return pilImage

    def _getInternalVariable(self, fieldVariable):
        fieldValue = None
        if fieldVariable == "^moonphase":
            fieldValue = str(self._moonPhaseSymbol)
        if fieldVariable == "^moonazimuth":
            fieldValue = str(self._moonAzimuth)
        if fieldVariable == "^moonelevation":
            fieldValue = str(self._moonElevation)
        if fieldVariable == "^moonillumination":
            fieldValue = str(self._moonIllumination)  

        return fieldValue
        
    def _addImages(self):
        for index, name in enumerate(self._config["images"]):
            imageData = self._config["images"][name]
            imageName = imageData["image"]
            imageX = imageData["position"]["x"]
            imageY = imageData["position"]["y"]
            image = None

            if self._isFileReadable(imageName):
                image = cv2.imread(imageName)
            else:
                imageNameTemp = os.path.join(self._scriptPath, imageName)
                if self._isFileReadable(imageNameTemp):
                    image = cv2.imread(imageNameTemp, cv2.IMREAD_UNCHANGED)

            if image is not None:
                if "rotate" in imageData.keys():
                    image = self._rotate_image(image, imageData["rotate"])

                #self._image = self._merge_image(imageName, self._image, image, imageX, imageY)
                self._image = self._overlay_transparent(imageName, self._image, image, imageX, imageY)

            else:
                self._log("ERROR: Cannot locate image " + imageName)

    def _overlay_transparent(self, imageName, background, overlay, x, y):

        if (overlay.shape[0] + y < background.shape[0]) and (overlay.shape[1] + x < background.shape[1]):
            background_width = background.shape[1]
            background_height = background.shape[0]

            if x >= background_width or y >= background_height:
                return background

            h, w = overlay.shape[0], overlay.shape[1]

            if x + w > background_width:
                w = background_width - x
                overlay = overlay[:, :w]

            if y + h > background_height:
                h = background_height - y
                overlay = overlay[:h]

            if overlay.shape[2] < 4:
                overlay = np.concatenate(
                    [
                        overlay,
                        np.ones((overlay.shape[0], overlay.shape[1], 1), dtype = overlay.dtype) * 255
                    ],
                    axis = 2,
                )

            overlay_image = overlay[..., :3]
            mask = overlay[..., 3:] / 255.0

            background[y:y+h, x:x+w] = (1.0 - mask) * background[y:y+h, x:x+w] + mask * overlay_image

            self._log("Adding image " + imageName)
        else:
            self._log("ERROR: Adding image " + imageName + ". Its outside the bounds of the main image")
        return background

    def _merge_image(self, imageName, back, front, x,y):
        if back.shape[2] == 3:
            back = cv2.cvtColor(back, cv2.COLOR_BGR2BGRA)
        if front.shape[2] == 3:
            front = cv2.cvtColor(front, cv2.COLOR_BGR2BGRA)

        if (front.shape[0] + y < back.shape[0]) and (front.shape[1] + x < back.shape[1]):
            bh,bw = back.shape[:2]
            fh,fw = front.shape[:2]
            x1, x2 = max(x, 0), min(x+fw, bw)
            y1, y2 = max(y, 0), min(y+fh, bh)
            front_cropped = front[y1-y:y2-y, x1-x:x2-x]
            back_cropped = back[y1:y2, x1:x2]

            alpha_front = front_cropped[:,:,3:4] / 255
            alpha_back = back_cropped[:,:,3:4] / 255
            result = back.copy()

            result[y1:y2, x1:x2, :3] = alpha_front * front_cropped[:,:,:3] + (1-alpha_front) * back_cropped[:,:,:3]
            result[y1:y2, x1:x2, 3:4] = (alpha_front + alpha_back) / (1 + alpha_front*alpha_back) * 255
            self._log("Adding image " + imageName)
        else:
            self._log("ERROR: Adding image " + imageName + ". Its outside the bounds of the main image")
            result = back

        return result

    def _rotate_image(self, image, angle):
        image_center = tuple(np.array(image.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
        result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
        return result

class keyvalue(argparse.Action):
    def __call__( self , parser, namespace, values, option_string = None):
        setattr(namespace, self.dest, dict())
          
        for value in values:
            key, value = value.split('=')
            getattr(namespace, self.dest)[key] = value

def main():    
    parser = argparse.ArgumentParser() 
    parser.add_argument("-v", "--verbose", action="store_true",  help="Verbose output")
    parser.add_argument("-d", "--data", help="Path to extra data")   
    parser.add_argument("-c", "--config", help="Path to config file, if none will use annotate.json")  
    parser.add_argument("-i", "--image", help="Image file to use, if none latest allsky image will be used")
    parser.add_argument("-k", "--kwargs", nargs='*', action = keyvalue, help="list of key pair values for field data --kwargs sensor=32.1 date=20211207 231234")
    arguments = parser.parse_args()

    annotater = ALLSKYANNOTATE(arguments.config, arguments.data, arguments.image, arguments.verbose, arguments.kwargs)
    annotater.annotate()

if __name__ == "__main__":
    main()