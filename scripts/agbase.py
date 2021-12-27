import os
import json
import signal
from pathlib import Path
from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit.shortcuts import message_dialog

class AGBASE():
    _configFile = None
    _config = None
    _verbose = None
    _variables = {"^moonphase", "^moonillumination", "^moonazimuth", "^moonelevation"}

    def __init__(self, configFile, verbose):

        self._verbose = verbose
        self._scriptPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._configFile = os.path.join(self._scriptPath, "annotate.json")
        if configFile is not None:           
            if self._isFileReadable(configFile):
                self._configFile = configFile

        signal.signal(signal.SIGINT, self._signalHandler)

    def _signalHandler(self, signum, frame):
        self._log("Aborting")
        exit(130)

    def _log(self, text):
        if self._verbose:
            print(text)

    def _isFileReadable(self, fileName):
        """ Check if a file is readable """
        if os.path.exists(fileName):
            if os.path.isfile(fileName):
                return os.access(fileName, os.R_OK)
            else:
                return False 
        else:
            return False 

    def _isFileWriteable(self, fileName):
        """ Check if a file exists and can be written to """
        if os.path.exists(fileName):
            if os.path.isfile(fileName):
                return os.access(fileName, os.W_OK)
            else:
                return False 
        else:
            return False 

    def _loadConfigFile(self, silent=False):
        if not silent:
            result = True
        else:
            result = ""

        try:
            if self._isFileReadable(self._configFile):
                if self._isFileWriteable(self._configFile):
                    with open(self._configFile) as file:
                        self._config = json.load(file)
                
                    if len(self._config["fields"]) == 0 and len(self._config["images"]) == 0:
                        if not silent:
                            self._log("WARNING: Config file (" + self._configFile + ") is empty. Did you create a config file? Nothing to do so ABORTING")
                            result = False
                        else:
                            result = "WARNING: Config file (" + self._configFile + ") is empty. Did you create a config file? Nothing to do so ABORTING"
                else:
                    if not silent:
                        self._log("ERROR: Config File not writeable " + self._configFile)
                        result = False
                    else:
                        result = "ERROR: Config File not writeable " + self._configFile
            else:
                if not silent:
                    self._log("ERROR: Config File not readable " + self._configFile)
                    result = False
                else:
                    result = "ERROR: Config File not readable " + self._configFile
        except ValueError:
            if not silent:
                result = False
            else:
                result = "Error loading JSON Configuration File. Please check that it is valid JSON"

        return result

    def _saveConfigFile(self):
        with open(self._configFile, 'w') as file:
            json.dump(self._config, file)  

    def _checkFieldExists(self, field, type):
        result = True
        if field in self._config[type]:
            result = yes_no_dialog(title="Field Already Exists", text="This field (" + field + ") already exists. Would you like to update it?").run()
        
        return result

    def _isVariableValid(self, variable):
        result = True
        if variable[0] == "^":
            if variable not in self._variables:
                result = False
        
        return result