# ZWO Camera examples

## Example 1

![ZWO Example 1](../docimages/zwo-example1.png?raw=true "Example 1")

The example above was captured on my AllSky Camer wich uses a ZWO ASI178MM and a lot of custom hardware to create the extra data.

The image was annotated using the following config file.

```javascript
{
    "fields": {
        "file": {
            "file": "/home/pi/allsky/extra.txt",
            "position": {
                "x": 25,
                "y": 155
            },
            "colour": "#666666",
            "font": "default"
        },
        "moonlabel": {
            "variable": "",
            "label": "Moon Phase",
            "position": {
                "x": 1700,
                "y": 230
            },
            "colour": "#444444",
            "font": "moonbigfont"
        },
        "moonphase": {
            "variable": "^moonphase",
            "label": "",
            "position": {
                "x": 1890,
                "y": 233
            },
            "colour": "#444444",
            "font": "moonbig"
        },
        "moonillumination": {
            "variable": "^moonillumination",
            "label": "Illumination: ",
            "position": {
                "x": 1730,
                "y": 270
            },
            "colour": "#444444",
            "font": "default"
        },
        "moonazimuth": {
            "variable": "^moonazimuth",
            "label": "Azimuth: ",
            "position": {
                "x": 1760,
                "y": 300
            },
            "colour": "#444444",
            "font": "default"
        },
        "moonelevation": {
            "variable": "^moonelevation",
            "label": "Elevation: ",
            "position": {
                "x": 1790,
                "y": 330
            },
            "colour": "#444444",
            "font": "default"
        }
    },
    "images": {
        "compass": {
            "position": {
                "x": 1800,
                "y": 10
            },
            "rotate": 10,
            "image": "images/compass200.png"
        },
        "signature": {
            "position": {
                "x": 1818,
                "y": 1968
            },
            "image": "images/signature-small.png"
        }
    },
    "fonts": {
        "moon": {
            "fontPath": "fonts/moon_phases.ttf",
            "fontSize": 20
        },
        "moonbig": {
            "fontPath": "fonts/moon_phases.ttf",
            "fontSize":32
        },
        "default": {
            "fontPath": "fonts/Roboto-Medium.ttf",
            "fontSize":20
        },
        "moonbigfont": {
            "fontPath": "fonts/Roboto-Medium.ttf",
            "fontSize": 32
        }
    }
}

```