# allskyannotate

A script to allow annotation of images created by Thomas Jacquin's allsky software - https://github.com/thomasjacquin/allsky

**Please read all of this document before using this script**

**Go Easy this is my first 'proper' Python project ;-)**

This script will allow the following to be overlayed on the captured image

* Text
* Inbuilt data (Such as the Moon's phase)
* Images
* Extra text, as the current allsky softare does
* Data passed on the command line

It is intended to replace the 'extra' text functionality that is a little limited in respect to where text can be placed.

The annotater will work for any camera used.

## Why Write This?
I originally wrote the 'extra' text feature to allow me to display data from my camera, I have several external sensors capturing data. This was fine at the time but as I have added more to my camera I found myself wanting a lot more data to be displayed on each captured image and wanted to use different fonts.
I played around with a few ideas, like imagemagick but found then really quite slow and cumbersom to setup and maintain. I settled on an approach that keeps all of the configuration for the data to be displayed in a single file.

## How does it work?
The idea is quite simple

1) In the saveImageNight script once all of the image processing is complete, but before its been copied to its final locations, call this script passing it the relevant data
2) This script will annotate the image and write it back to allsky
3) The allsky sofware can then continue to process the image

![Data Flow](docimages/flow.png?raw=true "Flow")

# Annotater command line

Before looking at the setup its worth seeing how the annotater runs. The annotater is invoked using the annotater.py script, the installer documented below will automatically add this the the allsky sabe image script.

```usage: annotate.py [-h] [-v] [-d DATA] [-c CONFIG] [-i IMAGE] [-k [KWARGS ...]]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose output
  -d DATA, --data DATA  Path to extra data
  -c CONFIG, --config CONFIG
                        Path to config file, if none will use annotate.json
  -i IMAGE, --image IMAGE
                        Image file to use, if none latest allsky image will be used
  -k [KWARGS ...], --kwargs [KWARGS ...]
                        list of key pair values for field data --kwargs sensor=32.1 date=20211207 231234
```

The options are

| Option | Required? |Description |
| ------ | --------- |----------- |
| -v | No  | Enable more verbose output |
| -d | No  | The path to the datafile containing extra information, see 'Data Files' below |
| -c | No  | The full path to the config file. If not specified annotate.json is used |
| -i | No  | The full path to the image to annotate. If not specified the current allsky image is used |
| -k | No  | List of additional variables, mainly intended to be used for allsk to pass data |

With no options specified the annotated will use the last image captured by the allsky software and the default configuration, annotate.json.

When testing its best to use the -v option as it will tell you if there are any issues. If you see any errors reported when using the -v option these should be fixed.

## Data Files
The annotater can either use the extra data file from allsky or a new file format that you specify on the command line with the -d option. This file is either a json or etxt file with key pair values. This file would be created by any other software you are using.

### json format

```javascript
{
    "fields": {
        "skystate": "Clear",
        "teapot": "Empty"
    }
}
```

### name pair format

```
skystate=Clear
teapot=Empty
```

# Setting things up

## Permissions
Its important that the annotation script can access all of the allsky data and configuration so please ensure that the annotation script is setup as the same user as the allsky software. Normally this will just be the default pi user.

## Dependencies

### Python3
The annotater requires python3 and will **not** run on python2. Python3 does not have to be the default on your system but it must be installed

### Allsky
The allsky software must be setup and working correctly before attempting to install this script.
Please make a backup of any scripts that you change in the allsky software and note that you will have to make the changes again should you update the allsky software

### Python libraries
The code requires several Python libraries. The installer script will install these if not present.

* opencv
* numpy
* ephem
* pillow

## Getting the code
Clone the repository into a location of your choice

```
git clone https://github.com/Alex-developer/allskyannotate.git
```

## Run the installer
An installation script is provided that will automate most of the installation and setup process. To run the script change into the allskyannotate directory and enter

```
./installer/install.sh
```

The installer will guide you through a series of promts to install the annotater. You will also have the option to automatically modify the default allsky scripts to call the annotater at the correct point after an imge has been captured. The installer will make a backup copy of the allsky scripts in case you wish to remove the annotater.

## Copy the default config file
**Only do this step if you did not setup a config during the installation process**

By default the annotater will use a configuration file called annotate.json. When the repository is cloned you will find an empty config file called annotate.json.repo so copy this

```
cp examples/configs/empty-config.json annotate.json
```

## Config Setup
The config is all defined in a json file, by defaulgithubt called annotate.json. The file contains three sections

| Section | Description |
| ------- | ----------- |
| fields  | This defines the fields to display on the allsky captured image |
| images  | This defines any images to display on the allsky captured image |
| fonts   | This section defines any custom fonts you wish to use |

### Fonts
The annotater is capable of displaying information using TruType fonts. There is a vast collection of these availble online, https://www.dafont.com for example.
To install the fonts first find the TrueType font you wish to use and copy it into the fonts folder.

An example fonts ection of the config might look liek the following

```javascript
    "fonts": {
        "fontbig": {
            "fontPath": "fonts/Comfortaa-Regular.ttf",
            "fontSize": 60
        },
        "font1": {
            "fontPath": "fonts/Comfortaa-Regular.ttf",
            "fontSize": 24
        },
        "font3": {
            "fontPath": "fonts/Comfortaa-Regular.ttf",
            "fontSize": 20
        },
        "moon": {
            "fontPath": "fonts/moon_phases.ttf",
            "fontSize": 48
        },
        "we": {
            "fontPath": "fonts/DS-DIGI.TTF",
            "fontSize": 16
        },
        "we1": {
            "fontPath": "fonts/DS-DIGI.TTF",
            "fontSize": 32
        }
    }
```
Each entry in the fonts section specifies a font name that can then be applied to a field definition. Looking at each of the fonts entries in a little more detail

```javascript
        "fontbig": { <!-- The name of this font entry. This Must be unique -->
            "fontPath": "fonts/Comfortaa-Regular.ttf", <!-- The path to the font file -->
            "fontSize": 60 <! -->- The size of the font
        }
```

Fonts should be installed in the fonts directory. The annotater will support any TrueType font. 

If you are not comfortable editing the json files then a script is available in the scripts directory to install fonts for you. To run the script cd into the script directory and run the addfont.py script. The script takes several arguments

```
usage: addfont.py [-h] [-v] [-c CONFIG] -f FONT

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -f FONT, --font FONT  The URL of the font on daFont.com. Make sure ints the font page uRL NOT a search page url

optional arguments:
  -v, --verbose         Verbose output
  -c CONFIG, --config CONFIG
                        Path to config file, if none will use annotate.json
```

For most users the only option required is the -f option which specifies the URL to the font on dafont.com. An example might look like

```
./addfont.py -f https://www.dafont.com/chernobyl.font
```

This will download the font and then prompt you for two sets of entries. The first is the names you wish to use as a comma seperated list and the second the sizes you require for each name. Since a font from dafont may contain more than one font, light/bold etc, you will be prompted for these values for each font found in the download. If you do not wish to use a specific font just hit enter when prmompted for the names.

Once you have entered the data and its been validated the fonts selected will be installed in the fonts folder and the config file updated.

### Images
The annotater is capable of adding images to the frame catured by the allsky software. I use this to add a small compass to my images indicating North and also to add a small signature.

An example images section might look like

```javascript
    "images": {
        "compass": {
            "position": {
                "x": 1800,
                "y": 100
            },
            "rotate": 10,
            "image": "images/compass150.png"
        },
        "signature": {
            "position": {
                "x": 1540,
                "y": 1800
            },
            "image": "images/signature.png"
        } 
    }
```

In the above example two images will be added to every frame captured by the AllSky Software. The first is a compass at 1800,100 rotated by 10 degrees and the second a signature added at 1540, 1800.

The images typically reside in the images folder inside the annotater main folder but can be anywhere as long as a full path to the image is provided.

Care should be taken when adding images to make sure they do not go outside the bounds of the main image.

If you are not comfortable editing the config the a script is available in the scripts directory to assist in adding images. The script is called addimages.py

```
usage: addimage.py [-h] [-v] [-r ROTATION] [-c CONFIG] -i IMAGE -x XPOS -y YPOS -n NAME

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -i IMAGE, --image IMAGE
                        Full path to the image
  -x XPOS, --xpos XPOS  The x coordinate for the field
  -y YPOS, --ypos YPOS  The y coordinate for the field
  -n NAME, --name NAME  The name for the field

optional arguments:
  -v, --verbose         Verbose output
  -r ROTATION, --rotation ROTATION
                        Image rotation in degrees
  -c CONFIG, --config CONFIG
                        Path to config file, if none will use annotate.json
```

The script takes several parameters some optional and some mandatory. 

| Option | Required? |Description |
| ------ | --------- |----------- |
| -i | Yes | The FULL path to the image file |
| -x | Yes | The x coordinate in the image  |
| -y | Yes | The y coordinate in the image |
| -r | No  | The rotation of the image in degrees |
| -v | No  | Enable more verbose output |

### Fields
Fields are the data that is added to the image. There are four sources of data that can be added

* From the AllSky software
* From an extra text file
* passed on the command line to the annotater
* inbuilt fields

#### Extra Text
Since most people will be migrating from using the Extra Text feature in allsky the first type of field allows for the extra text to be added to the images easily.

```
"file": {
    "file": "",
    "position": {
        "x": 10,
        "y": 220
    },
    "colour": "red",
    "font": "font3"
}
```

In the above example the extra text is displayed starting at 10,220 (pixels) in the captured image using font3, this is defined in the fonts section and coloured red.

The file entry is blank which means the annoater will look at he AllSky config to find the extra text file. You can also specify a FULL path to the file here, see the previous notes about permissions on files.

**NOTE: The Extra Text feature was never implemented on the pi HQ camera so if you are using one you will need to specify the path to the file in the 'file' setting**

The colour field supports a lot of different ways of specifying the colour, see the colours section below.

#### Other Fields
The annotater is also capable of adding information from an external source or via its internal data. The external source is intended to be a replacement for the 'Extra Text' feature in allsky. Whilst this can still be used, see above, if you are in control of the extra data the new way of doing it is far more flexible.

In this first example we will look at using a data field provoided from the data file specified using the -d option when running the annotater.

```javascript
"skystate": {
    "variable": "%skystate",
    "label": "Sky State: ",
    "position": {
        "x": 10,
        "y": 1940
    },
    "colour": "#6f2232",
    "font": "font3"
}
```
This example is displaying the 'skystate' variable from the data file. Looking at the fields 

| field | Description |
| ------- | ----------- |
| variable  | The variable name to use. The % indicates that this is from the external data source or commad line |
| label  | The label for the field. This can be blank if no label is required |
| Position   | This specifies the position on the image to display the field |
| colour | This specifies the colour of the field, see the 'colouurs' section below |
| font | This specifies the name in the fonts entry for the font to use |

This second example is displaying an internal field. Internal fields are data that the annotater generates automatically and makes avaialble.

```
"moonphase": {
    "variable": "^moonphase",
    "label": "",
    "position": {
        "x": 200,
        "y": 1790
    },
    "colour": "white",
    "font": "moon"
}
```
The only real difference between this and the previous example is the 'variable'. In this case it is prefixed with a ^ indicating that its an internal variable.

Available internal variables. At present the only variables available relate to the Moon and the calculation use the lat/lon defined in the main allsk configuration

| variable | Description |
| ------- | ----------- |
| ^moonphase  | Special variable to be used with the Moon font to display the Moon Phase |
| ^moonillumination | The percentage of the Moon illuminated |
| ^moonazimuth | The Azimuth of the Moon |
| ^moonelevation | The Moons elevation |

The last example is using a field to display a label with no data

```
        "moonlabel": {
            "variable": "",
            "label": "Moon Phase",
            "position": {
                "x": 10,
                "y": 1800
            },
            "colour": "#950740",
            "font": "font1"
        }
```

The only real difference with this example is the variable is empty and a label defined.

#### Fields Script
As with the other config sections a basic helper script is provided to add fields.

```
usage: addfield.py [-h] [-v] [-i FILE] [-c CONFIG] [-l LABEL] -f FIELD -a VARIABLE -x XPOS -y YPOS -r COLOUR -o FONT

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -f FIELD, --field FIELD
                        The name of the field to add/edit
  -a VARIABLE, --variable VARIABLE
                        The name of the variable to display
  -x XPOS, --xpos XPOS  The x coordinate for the field
  -y YPOS, --ypos YPOS  The y coordinate for the field
  -r COLOUR, --colour COLOUR
                        The colour of the field
  -o FONT, --font FONT  The font name to use

optional arguments:
  -v, --verbose         Verbose output
  -i FILE, --file FILE  Filename for extra text
  -c CONFIG, --config CONFIG
                        Path to config file, if none will use annotate.json
  -l LABEL, --label LABEL
                        The fields label
```

#### Checking the configuration
A script is provided in the scripts directory that will do basic validation of the configuration file. To run it change to the scripts directory and enter

```
./validate.py
```

The script will run thru the configuration and report on any issues. There are two types of issues reported

| Issue | Notes |
| ----- | ----------- |
| ERROR  | This is an issue that will prevent the annotater runnign so **must** be fixed |
| WARNING | There is a problem with the config but it will nto prevent the annotater from running |

Example output from the validation script

```
Attempting To Load Config File From /home/pi/allskyannotate/annotate.json
Config File Loaded From /home/pi/allskyannotate/annotate.json

Config Info
-----------
Fields : 13
Images : 2
Fonts  : 6

Checking Fonts
--------------
Checked Font fontbig Font Installed, Font Used, Font Size OK
Checked Font font1 Font Installed, Font Used, Font Size OK
Checked Font font3 Font Installed, Font Used, Font Size OK
Checked Font moon Font Installed, Font Used, Font Size OK
Warning Checked Font we Font Installed, Font Not Used, Font Size OK
Warning Checked Font we1 Font Installed, Font Not Used, Font Size OK

Checking Images
---------------
Image /home/pi/allskyannotate/images/compass150.png Found OK, Position Found
Image /home/pi/allskyannotate/images/signature.png Found OK, Position Found

Checking Fields
---------------
Checked Field date, Position Found, Variable Valid, Font valid
Checked Field sensor temp, Position Found, Variable Valid, Font valid
Checked Field exposure, Position Found, Variable Valid, Font valid
Checked Field gain, Position Found, Variable Valid, Font valid
ERROR Checked Field brightness, Position Found, Variable Valid, Font Name 'font31' Not found in the fonts section
Checked Field file, Position Found, Variable Valid, Font valid
Checked Field moonlabel, Position Found, Variable Valid, Font valid
Checked Field moonphase, Position Found, Variable Valid, Font valid
Checked Field moonillumination, Position Found, Variable Valid, Font valid
Checked Field moonazimuth, Position Found, Variable Valid, Font valid
Checked Field moonelevation, Position Found, Variable Valid, Font valid
Checked Field skystate, Position Found, Variable Valid, Font valid
Checked Field date1, Position Found, Variable Valid, Font valid

Results
-------
Error: There are errors in your configuration. These will prevent the annotater from running and must be fixed
Warning: There are warnings in your configuration. These will not prevent the annotater from running but should be fixed
```

#### Colours
Hexadecimal color specifiers, given as #rgb, #rgba, #rrggbb or #rrggbbaa, where r is red, g is green, b is blue and a is alpha (also called ‘opacity’). For example, #ff0000 specifies pure red, and #ff0000cc specifies red with 80% opacity (cc is 204 in decimal form, and 204 / 255 = 0.8).

RGB functions, given as rgb(red, green, blue) where the color values are integers in the range 0 to 255. Alternatively, the color values can be given as three percentages (0% to 100%). For example, rgb(255,0,0) and rgb(100%,0%,0%) both specify pure red.

Hue-Saturation-Lightness (HSL) functions, given as hsl(hue, saturation%, lightness%) where hue is the color given as an angle between 0 and 360 (red=0, green=120, blue=240), saturation is a value between 0% and 100% (gray=0%, full color=100%), and lightness is a value between 0% and 100% (black=0%, normal=50%, white=100%). For example, hsl(0,100%,50%) is pure red.

Hue-Saturation-Value (HSV) functions, given as hsv(hue, saturation%, value%) where hue and saturation are the same as HSL, and value is between 0% and 100% (black=0%, normal=100%). For example, hsv(0,100%,100%) is pure red. This format is also known as Hue-Saturation-Brightness (HSB), and can be given as hsb(hue, saturation%, brightness%), where each of the values are used as they are in HSV.

Common HTML color names. The ImageColor module provides some 140 standard color names, based on the colors supported by the X Window system and most web browsers. color names are case insensitive. For example, red and Red both specify pure red.

# Testing
The best way to test is to keep things simple to start with. 

- Run the install script but **DO NOT** allow the installer to modify the allsky save script.
  - Setup te annoatet.json config as required
  - Run the annotate.py script with the -v option and check the resulting image
  - Fix any issues and repeat the above steps untill you are happy
- Re run the installer and modify the allsky scripts

# Performance
Performance is important as the annotater runs inline withe the main allsky software. I have tried to optimise the code as much as possible.

Some statistics from a Pi4B with 8 Gig of RAM

| Benchmark | Time |
| ------- | ----------- |
| Replacement for default extra text functionality in allksy  | 0.39 Seconds |
| 13 Fields, 2 Images and 6 Fonts | 0.50 Seconds |

# Debugging tips

## Displaying more verbose output from the annotater

The best way to debug any issues is to use the verbose logging mode of the annotater. To enable this find the following bit of code in the allsky saveimageNight script

```
# Run the image annotation script. Added by the annotater installer on Sun 26 Dec 21:26:45 GMT 2021
if [[ -x "/home/pi/allskyannotate/annotate.py" ]]
then
  /home/pi/allskyannotate/annotate.py
fi
```

And change it to add a -v to the annotate.py

```
# Run the image annotation script. Added by the annotater installer on Sun 26 Dec 21:26:45 GMT 2021
if [[ -x "/home/pi/allskyannotate/annotate.py" ]]
then
  /home/pi/allskyannotate/annotate.py -v
fi
```

Then tail the allsk log file

# Uninstalling
If you wish to remove the annotater then run the uninstall script from the annotater directory

```
./installer/uninstall.py
```

The uninstaller will replace the allsky save image script with the backup made during the installation. It will NOT remove the annotater code or directory.

# Upgrading AllSky

After ugrading allsky its very **IMPORTANT** that you re run the installer