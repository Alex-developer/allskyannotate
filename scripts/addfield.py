#!/usr/bin/python3

import os
import argparse
import json
from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit.shortcuts import message_dialog

from agbase import AGBASE

class FIELDMANAGER(AGBASE):

    _field = None
    _file = None 
    _variable = None
    _xpos = None
    _ypos = None
    _colour = None
    _font = None 
    _label = ""

    def __init__(self,verbose, field, label, file, variable, xpos, ypos, colour, font, configFile):
        
        super().__init__(configFile, verbose)

        self._font = font
        self._file = file
        self._variable = variable
        self._xpos = xpos
        self._ypos = ypos
        self._colour = colour
        self._field = field
        self._label = label

    def run(self):
        if self._loadConfigFile():
            if self._validateData():
                if self._checkFieldExists(self._field, "fields"):
                    self._updateField()
                    self._saveConfigFile()

    def _validateData(self):
        result = True
        if self._font not in self._config["fonts"]:
            fonts =  ", ".join(self._config["fonts"])
            message_dialog(title="Error",text="The font (" + self._font + ") Does Not Exist. Please check the spelling or setup the font\nInstalled fonts are " + fonts,).run()
            result = False
        return result

    def _updateField(self):
        if self._field in self._config["fields"]:
            self._config["fields"][self._field]["variable"] = self._variable
            self._config["fields"][self._field]["label"] = self._label
            self._config["fields"][self._field]["colour"] = self._colour
            self._config["fields"][self._field]["font"] = self._font            
            self._config["fields"][self._field]["position"]["x"] = self._xpos
            self._config["fields"][self._field]["position"]["y"] = self._ypos               
        else: 
            newField  = {
                self._field: {
                    "variable" : self._variable,
                    "label" : self._label,
                    "position" : {
                        "x": self._xpos,
                        "y": self._ypos
                    }
                }
            }
            if (self._colour is not None):
                
                newField[self._field].update({"colour" : self._colour})

            if (self._font is not None):
                newField[self._field].update({"font" : self._font})

            self._config["fields"].update(newField)

def main():    
    parser = argparse.ArgumentParser() 
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument("-v", "--verbose", action="store_true",  help="Verbose output")      
    optional.add_argument("-i", "--file",  help="Filename for extra text") 
    optional.add_argument("-c", "--config", help="Path to config file, if none will use annotate.json")      
    optional.add_argument("-l", "--label", help="The fields label")      
    required.add_argument("-f", "--field",  help="The name of the field to add/edit", required = True)        
    required.add_argument("-a", "--variable",  help="The name of the variable to display", required = True)        
    required.add_argument("-x", "--xpos",  help="The x coordinate for the field", required = True)        
    required.add_argument("-y", "--ypos",  help="The y coordinate for the field", required = True)        
    required.add_argument("-r", "--colour",  help="The colour of the field", required = True)        
    required.add_argument("-o", "--font",  help="The font name to use", required = True)        

    arguments = parser.parse_args()

    fieldManager = FIELDMANAGER(arguments.verbose, arguments.field,  arguments.label, arguments.file, arguments.variable, arguments.xpos, arguments.ypos, arguments.colour, arguments.font, arguments.config)
    fieldManager.run()

if __name__ == "__main__":
    main()