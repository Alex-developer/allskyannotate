#!/usr/bin/python

import os
import argparse
import json
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import pathlib
from agbase import AGBASE

class FONT(AGBASE):
    _use = False
    _name = None
    _sizes = None
    _names = None

    def __init__(self, use, name, sizes):
        self._use = use
        self._name = name
        self._sizes = sizes

    @property
    def use(self):
        return self._use

    @use.setter
    def use(self, value):
        self._use = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def sizes(self):
        return self._sizes

    @sizes.setter
    def sizes(self, value):
        self._sizes = value

    @property
    def names(self):
        return self._names

    @names.setter
    def names(self, value):
        self._names = value


class FONTMANAGER(AGBASE):
    _scriptPath = None
    _font = None
    _fontName = None
    _downloadURL = None

    _zipFile = None
    _fonts = []

    def __init__(self, verbose, font, configFile):
        super().__init__(configFile, verbose)

        self._font = font

        self._log("NOTICE: Config file set to " + self._configFile)        
        self._log("INIT: font URL - " + self._font)

    def run(self):
        if self._loadConfigFile():
            self._createDownloadURL()
            if self._downloadFont():
                self._getUserInput()
                self._processFonts()
                self._saveConfigFile()

    def _createDownloadURL(self):
        fontURL = self._font.replace("https://www.dafont.com/","")
        fontName = fontURL.replace(".font","")
        fontName = fontName.replace("-","_")

        self._downloadURL = "https://dl.dafont.com/dl/?f=" + fontName

        self._log("INFO: generated Download URL - " + self._downloadURL)

    def _downloadFont(self):
        result = True
        self._log("INFO: Starting Font Download")
        url = urlopen(self._downloadURL)     
        self._zipFile = ZipFile(BytesIO(url.read()))
        for contained_file in self._zipFile.namelist():
            file_extension = pathlib.Path(contained_file).suffix
            if file_extension.lower() in [".ttf", ".otf"]:
                self._fonts.append( FONT(False, contained_file, 0) )
        if len(self._fonts) == 0:
            self._log("ERROR: No fonts found in the download file")
            result = False
        else:
            foundFonts = ""
            sep = ""
            for font in self._fonts:
                if foundFonts != "":
                    sep = ", "
                foundFonts = foundFonts + sep + font.name
            self._log("INFO: " + str(len(self._fonts)) + " Font(s) Found In Download - " + foundFonts)
        return result

    def _getUserInput(self):
        # CHECK IF FONTS ALREADY INSTALLED
        for font in self._fonts:
            entering = True
            while entering:
                os.system('clear')
                print("You will now be prompted to enter the names and sizes you require for each font found.")
                print("If you do not want to use a font then just hit <Enter> on the names prompt")
                print("Each font name MUST be unique across all fonts installed.")
                print("Details for " + font.name)
                print("")
                namesText = input("Enter the names you would like to use for this font as a comma seperated list: ")
                namesArray = namesText.split(",")
                nameCheck = self._checkNames(namesArray)
                if nameCheck == "":
                    print("")
                    if namesText != "":
                        sizesText = input("Enter the font size you would like for each name as a comma seperated list: ")
                        
                        sizesArray = sizesText.split(",")

                        if len(namesArray) == len(sizesArray):
                            font.names = namesArray
                            font.sizes = sizesArray
                            font.use = True
                            entering = False
                        else:
                            input("ERROR: You entered " + str(len(namesArray)) + " names and " + str(len(sizesArray)) + " sizes. Hit <Enter> to try again.")
                    else:
                        entering = False
                else:
                    input("ERROR: The name " + nameCheck + " has already been used. Hit <Enter> to try again.")

    def _checkNames(self, names):
        result = ""
        for index, font in enumerate(self._config["fonts"]):
            if font in names:
                result = font
                break
        
        return result
            
    def _processFonts(self):
        for font in self._fonts:
            if font.use:
                self._log("INFO: Processing " + font.name + " Creating entries for " + "  ".join(font.names) + " at Sizes " + " ".join(font.sizes))
                for index, name in enumerate(font.names):
                    self._config["fonts"].update({name: {"fontPath": os.path.join("fonts", font.name), "fontSize":  int(font.sizes[index])}})
                    fontData = self._zipFile.read(font.name)
                    fontPath = os.path.join(self._scriptPath, "fonts", font.name)
                    with open(fontPath, "wb") as binary_file:
                        binary_file.write(fontData)
            else:
                self._log("INFO: Ignoring font " + font.name + " as no names or sizes specified")
            
def main():    
    parser = argparse.ArgumentParser() 
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument("-v", "--verbose", action="store_true",  help="Verbose output")      
    optional.add_argument("-c", "--config", help="Path to config file, if none will use annotate.json")        
    required.add_argument("-f", "--font",  help="The URL of the font on daFont.com. Make sure ints the font page uRL NOT a search page url", required=True)        
    arguments = parser.parse_args()

    fontManager = FONTMANAGER(arguments.verbose, arguments.font, arguments.config)
    fontManager.run()

if __name__ == "__main__":
    main()