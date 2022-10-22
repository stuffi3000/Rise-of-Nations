import os
import re


fileDir = os.getcwd() +"\\WIP\\"
for filename in os.listdir(fileDir):
    with open(fileDir + filename, 'r', encoding = "utf-8") as f:
        originalFileContents = f.readlines()
        clipIdx0 = -1 #where to cut file
        clipIdx1 = -1
        airWingInFile = False
        endBracketFound = False
        #find air wings
        for idx, line in enumerate(originalFileContents):
            if "fleet = {" in line:
                clipIdx0 = idx
                airWingInFile = True
            if airWingInFile == True and endBracketFound == False and line == "}\n":
                endBracketFound = True
                clipIdx1 = idx
        if airWingInFile:
            print(filename)
            newAirFileContents = originalFileContents[clipIdx0:clipIdx1 + 1]
            updatedFileContents = originalFileContents[:clipIdx0]
            updatedFileContents.extend(originalFileContents[clipIdx1 + 1:])
            print(clipIdx0, clipIdx1)
            #.extend(originalFileContents[clipIdx1 + 1:-1])
            with open(fileDir + filename[:-4] + "_fleet_legacy.txt", 'w', encoding = "utf-8") as f1:
                f.close()
                f1.writelines(newAirFileContents)
                with open(fileDir + filename, 'w', encoding = "utf-8") as f:
                    f.writelines(updatedFileContents)
