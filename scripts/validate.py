#!/usr/bin/python

import os
import argparse
from agbase import AGBASE

class CONFIGMANAGER(AGBASE):

    def __init__(self, verbose, configFile):
        verbose = True
        super().__init__(configFile, verbose)

    def run(self):
        haveErrors = False
        haveWarnings = False

        self._log("Attempting To Load Config File From " + self._configFile)
        result = self._loadConfigFile(True)
        if result == "":
            self._log("Config File Loaded From " + self._configFile)
        else:
            self._log(result)
            exit(1)

        self._log("")
        self._log("Config Info")
        self._log("-----------")
        self._log("Fields : " + str(len(self._config["fields"])))
        self._log("Images : " + str(len(self._config["images"])))
        self._log("Fonts  : " + str(len(self._config["fonts"])))                
        self._log("")
        self._log("Checking Fonts")
        self._log("--------------")        
        for index, name in enumerate(self._config["fonts"]):
            fontReadable = False
            fontPath = os.path.join(self._scriptPath, self._config["fonts"][name]["fontPath"])
            if self._isFileReadable(fontPath):
                fontReadable = True

            fontSizeFound = False
            if "fontSize" in self._config["fonts"][name]:
                if type(self._config["fonts"][name]["fontSize"]) is int:
                    fontSizeFound = True

            fontUsed = False
            for field in self._config["fields"]:
                if "font" in self._config["fields"][field] and self._config["fields"][field]["font"] == name:
                    fontUsed = True
                    break
        
            fontInfo = "Checked Font " + name + " "
            if fontReadable:
                fontInfo = fontInfo + "Font Installed, "
            else:
                fontInfo = fontInfo + "Font NOT Installed ("+fontPath+"), "

            if fontUsed:
                fontInfo = fontInfo + "Font Used, "
            else:
                fontInfo = fontInfo + "Font Not Used, "

            if fontSizeFound:
                fontInfo = fontInfo + "Font Size OK"
            else:
                fontInfo = fontInfo + "Font Size Is Missing Or Invalid"

            prefix = ""
            if fontUsed and not fontReadable:
                prefix = "Error "
                haveErrors = True
            else:
                if not fontSizeFound:
                    prefix = "Error "
                    haveErrors = True
                else:
                    if not fontUsed:
                        prefix = "Warning "
                        haveWarnings = True

            self._log(prefix + fontInfo)

        self._log("")
        self._log("Checking Images")
        self._log("---------------")     
        for index, name in enumerate(self._config["images"]):
            imagePath = self._config["images"][name]["image"]
            imageFound = False
            if self._isFileReadable(imagePath):
                imageFound = True
            else:
                imagePath = os.path.join(self._scriptPath, self._config["images"][name]["image"])
                if self._isFileReadable(imagePath):
                    imageFound = True

            positionFound = False
            if "position" in self._config["images"][name]:
                position = self._config["images"][name]["position"]
                if "x" in position and "y" in position:
                    positionFound = True

            if positionFound:
                posText = ", Position Found"
            else:
                posText = ", Position Invalid or Missing"

            if imageFound:
                if positionFound:
                    self._log("Image " + imagePath + " Found OK" + posText)
                else:
                    self._log("ERROR Image " + imagePath + " Found OK" + posText)
                    haveErrors = True
            else:
                self._log("ERROR Cannot Find Image " + imagePath  + posText)
                haveErrors = True

        self._log("")
        self._log("Checking Fields")
        self._log("---------------")                   
        for index, name in enumerate(self._config["fields"]):
            field = self._config["fields"][name]

            fontFound = True
            if "font" in field:
                if field["font"] not in self._config["fonts"]:
                    fontFound = False
                    haveErrors = True

            positionFound = False
            if "position" in field:
                position = field["position"]
                if "x" in position and "y" in position:
                    positionFound = True

            if positionFound:
                posText = ", Position Found"
            else:
                posText = ", Position Invalid or Missing"

            variableValid = True
            if "variable" in field:
                if field["variable"] != "":
                    variableValid = self._isVariableValid(field["variable"])
            
            if variableValid:
                variableStr = ", Variable Valid"
            else:
                variableStr = ", Unknown Intenal VAriable " + field["variable"]

            if fontFound:
                fontStr = ", Font valid"
            else:
                fontStr = ", Font Name '" + field["font"] + "' Not found in the fonts section"

            errorType = ""
            if not fontFound or not positionFound or not variableValid:
                errorType = "ERROR "
                haveErrors = True

            fieldStr = "Checked Field " + name
            self._log(errorType + fieldStr + posText + variableStr + fontStr)

        self._log("")
        self._log("Results")
        self._log("-------")             
        if haveErrors:
            self._log("Error: There are errors in your configuration. These will prevent the annotater from running and must be fixed")
        if haveWarnings:
            self._log("Warning: There are warnings in your configuration. These will not prevent the annotater from running but should be fixed")
        if not haveWarnings and not haveErrors:
            self._log("OK: Congratulations the configuration all lookss ok")


def main():    
    parser = argparse.ArgumentParser() 
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument("-v", "--verbose", action="store_true",  help="Verbose output")      
    optional.add_argument("-c", "--config", help="Path to config file, if none will use annotate.json")   

    arguments = parser.parse_args()

    configManager = CONFIGMANAGER(arguments.verbose, arguments.config)
    configManager.run()

if __name__ == "__main__":
    main()