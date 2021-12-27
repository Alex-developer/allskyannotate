#!/usr/bin/python3

import os
import argparse
from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit.shortcuts import message_dialog

from agbase import AGBASE

class IMAGEMANAGER(AGBASE):

    _rotation = None
    _image = None 
    _xpos = None
    _ypos = None
    _name = None

    def __init__(self, verbose, rotation, image, xpos, ypos, configFile, name):

        super().__init__(configFile, verbose)

        self._image = image
        self._rotation = rotation
        self._xpos = xpos
        self._ypos = ypos
        self._name = name
        
    def run(self):
        if self._loadConfigFile():
            if self._validateData():
                if self._checkFieldExists(self._name, "images"):
                    self._updateField()
                    self._saveConfigFile()

    def _validateData(self):
        result = True
        if not self._isFileReadable(self._image):
            message_dialog(title="Error",text="The image (" + self._image + ") Is Not Readable. Please check the file exists and has the correct permissions",).run()
        return result

    def _updateField(self):
        if self._name in self._config["images"]:
            self._config["images"][self._name]["image"] = self._image
            self._config["images"][self._name]["position"]["x"] = int(self._xpos)
            self._config["images"][self._name]["position"]["x"] = int(self._xpos)

            if self._rotation is not None:
                self._config["images"][self._name]["rotate"] = int(self._rotation)
            else:
                self._config["images"][self._name]["rotate"] = 0

        else:
            newField  = {
                self._name: {
                    "image" : self._image,
                    "position" : {
                        "x": int(self._xpos),
                        "y": int(self._ypos)
                    }
                }
            }
            
            if (self._rotation is not None):
                newField[self._name].update({"rotate" : self._rotation})
            else:
                newField[self._name].update({"rotate" : 0})     

            self._config["images"].update(newField)    

def main():    
    parser = argparse.ArgumentParser() 
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument("-v", "--verbose", action="store_true",  help="Verbose output")      
    optional.add_argument("-r", "--rotation",  help="Image rotation in degrees") 
    optional.add_argument("-c", "--config", help="Path to config file, if none will use annotate.json")      
    required.add_argument("-i", "--image",  help="Full path to the image", required = True)        
    required.add_argument("-x", "--xpos",  help="The x coordinate for the field", required = True)        
    required.add_argument("-y", "--ypos",  help="The y coordinate for the field", required = True)
    required.add_argument("-n", "--name",  help="The name for the field", required = True)

    arguments = parser.parse_args()

    imageManager = IMAGEMANAGER(arguments.verbose, arguments.rotation,  arguments.image, arguments.xpos, arguments.ypos, arguments.config, arguments.name)
    imageManager.run()

if __name__ == "__main__":
    main()