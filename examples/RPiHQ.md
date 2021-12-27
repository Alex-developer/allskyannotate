# RPiHQ Camera examples

## Example 1

![RPiHQ Example 1](../docimages/RPiHQ-example1.png?raw=true "Example 1")

The example above was captured on my RPiHQ camera. This is currently sitting on my desk hence the rather odd image !

The image was annotated using the following config file.

```javascript
{
    "fields": {
        "file": {
            "file": "/home/pi/allskyannotate/testdata/extra.txt",
            "position": {
                "x": 20,
                "y": 420
            },
            "colour": "#666666",
            "font": "default"
        },
        "moonlabel": {
            "variable": "",
            "label": "Moon Phase",
            "position": {
                "x": 20,
                "y": 2750
            },
            "colour": "#cccccc",
            "font": "default"
        },
        "moonphase": {
            "variable": "^moonphase",
            "label": "",
            "position": {
                "x": 250,
                "y": 2755
            },
            "colour": "white",
            "font": "moon"
        },
        "moonillumination": {
            "variable": "^moonillumination",
            "label": "Ilimunation: ",
            "position": {
                "x": 20,
                "y": 2810
            },
            "colour": "#cccccc",
            "font": "default"
        },
        "moonazimuth": {
            "variable": "^moonazimuth",
            "label": "Azimuth: ",
            "position": {
                "x": 20,
                "y": 2860
            },
            "colour": "#cccccc",
            "font": "default"
        },
        "moonelevation": {
            "variable": "^moonelevation",
            "label": "Elevation: ",
            "position": {
                "x": 20,
                "y": 2910
            },
            "colour": "#cccccc",
            "font": "default"
        }                
    },
    "images": {
        "compass": {
            "position": {
                "x": 3800,
                "y": 100
            },
            "rotate": 10,
            "image": "images/compass150.png"
        }        
    },
    "fonts": {
        "moon": {
            "fontPath": "fonts/moon_phases.ttf",
            "fontSize": 36
        },
        "default": {
            "fontPath": "fonts/Roboto-Medium.ttf",
            "fontSize": 36
        }
    }
}
```