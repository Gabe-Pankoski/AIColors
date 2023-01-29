import openai
import time
import os
from PIL import ImageDraw, Image

openai.api_key = None

def setApiKey():
    openai.api_key = input("Enter your OpenAI API key: ")

class colorPalette:
    def __init__(self, colors:list = [], names:list = []):
        # Do not allow colors without names
        if len(colors) != len(names):
            raise Exception("Colors and names must be the same length")
        self.colors = colors
        self.names = names
    
    def colorCount(self):
        return len(self.colors)

    def addColor(self, color, name):
        self.colors.append(color)
        self.names.append(name)
    
    def removeColor(self, color, name):
        self.colors.remove(color)
        self.names.remove(name)
    
    def __str__(self):
        out = ""
        for i in range(len(self.colors)):
            out += f"{self.names[i]}: {self.colors[i]}\n"
        return out

    def __repr__(self):
        return self.__str__()

class AIColors:
    def __init__(self, palette:colorPalette = None):
        self.palette = palette
        self.name = None

    def _setName(self, name):
        self.name = name

    def _prompt(self, colorName):
        return f"Give a hexadecimal color that goes with the name: \"{colorName}\", output should be: \"#RRGGBB\""
    
    def _altPrompt(self, colorName):
        return f"Give a hexadecimal color that goes with the name: \"{colorName}\", complimenting the colors {self.palette.names} output should be: \"#RRGGBB\""

    def _palettePrompt(self, paletteName):
        return f"Give a palette of six thematically-fitting, appropriately-paired colors, in Hex output \"#RRGGBB\", with a name, fitted to the theme: \"{paletteName}\". Arrange colors in a gradient, Output format, as list: Name - #RRGGBB output:"

    def getNameForPalette(self):
        prompt = f"Give a name for the palette: {self.palette}"
        name = openai.Completion.create(model="text-davinci-003", prompt=prompt, temperature=0, max_tokens=250)
        self.name = name["choices"][0]["text"].strip()
        time.sleep(0.5)

    def getPalette(self, paletteName):
        if self.palette == None:
            self.palette = colorPalette()
        else:
            self.palette = colorPalette()
        prompt = self._palettePrompt(paletteName)
        palette = openai.Completion.create(model="text-davinci-003", prompt=prompt, temperature=0, max_tokens=250)
        # palette is being returned as a list of strings, each string is a color STR - #RRGGBB\n
        palette = palette["choices"][0]["text"].strip()
        palette = palette.split("\n")
        for color in palette:
            # remove any , . or ; at the end of the string
            name, colorCode = color.split(" - ")
            name = name.strip("1234567890. ")
            colorCode = colorCode.strip(",.;:")
            self.palette.addColor(color=colorCode, name=name)
        self._setName(paletteName)
        time.sleep(0.5)

    def addColor(self, name):
        if self.palette == None:
            self.palette = colorPalette()
            prompt = self._prompt(name)
        else:
            prompt = self._altPrompt(name)
        colorCode = openai.Completion.create(model="text-davinci-003", prompt=prompt, temperature=0, max_tokens=50)
        colorCode = colorCode["choices"][0]["text"].strip()
        self.palette.addColor(colorCode, name)
        time.sleep(0.5)

    def removeColor(self, name):
        self.palette.removeColor(name)

    def savePalette(self, filename):
        with open(filename, "w") as f:
            f.write(self.__str__())
    
    def loadPalette(self, filename):
        with open(filename, "r") as f:
            lines = f.readlines()
        for line in lines:
            name, color = line.split(":")
            self.palette.addColor(color, name)

    def savePaletteImage(self):
        img = Image.new("RGB", (500 * self.palette.colorCount(), 500))
        draw = ImageDraw.Draw(img)
        for i in range(self.palette.colorCount()):
            draw.rectangle([(500 * i, 0), (500 * (i + 1), 500)], fill=self.palette.colors[i])
            # if color is too dark, write name in white
            # place text in center of rectangle
            if int(self.palette.colors[i][1:3], 16) < 128 and int(self.palette.colors[i][3:5], 16) < 128 and int(self.palette.colors[i][5:7], 16) < 128:
                draw.text((500 * i + 200, 250), self.palette.names[i], fill="white", anchor="mm", align="center")
            else:
                draw.text((500 * i + 200, 250), self.palette.names[i], fill="black", anchor="mm", align="center")
            
        # Write palette name in top-left corner
        draw.text((0, 0), self.name, fill="black")
        img.save(f"{self.name}.png")
    

    def __str__(self):
        return self.palette.__str__()

    def __repr__(self):
        return self.__str__()

if __name__ == "__main__":
    setApiKey()
    ai = AIColors()
    ai.getPalette("Old Newspaper")
    ai.savePaletteImage()
