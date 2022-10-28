from dataclasses import replace
import os
import re
import copy

fileDir = "WIP\\"
for filename in os.listdir(fileDir):
    if not "_air_legacy.txt" in filename and not "_naval" in filename:
        print(filename)
        with open(fileDir + filename, 'r', encoding = "utf-8") as f:
            originalFileContents = f.readlines()
            clipIdx = []
            airProductionInFile = False
            endBracketFound = False
            numIndents = -1
            productionStartIdx = -1 
            productionSectionReached = False
            aircraftEquipmentList = ['fighter_equipment', 'bomber_equipment', 'CAS_equipment','carrier_' ]
            #find air production
            for idx, line in enumerate(originalFileContents):
                if 'instant_effect' in line:
                    productionSectionReached = True
                if productionSectionReached:
                    aircraftInLine = 'fighter_equipment' in line or 'bomber_equipment' in line or 'CAS_equipment' in line or 'carrier' in line
                    #production in single line
                    if 'add_equipment_production' in line and aircraftInLine and '{' in line and '}' in line and idx > productionStartIdx:
                        clipIdx.append(idx)
                        airProductionInFile = True
                    elif (not 'add_equipment_production' in line) and '\t\t' in line and aircraftInLine and idx > productionStartIdx:
                        clipIdx.append(idx)
                        airProductionInFile = True
                        #go back and go forward to find the start and end of the production
                        idx2 = idx
                        while 'add_equipment_production' not in originalFileContents[idx2]:
                            idx2 -= 1
                            if idx - idx2 > 10:
                                print(idx, idx2)
                                raise Exception
                            clipIdx.append(idx2)
                        bracketCount = 0
                        #go forward and find the end of production
                        idx3 = idx
                        while True:
                            if '}' in originalFileContents[idx3]:
                                bracketCount += 1
                                if bracketCount == 2:
                                    break
                            idx3 += 1
                            clipIdx.append(idx3)
                            if idx3 > idx+10:
                                break

            outFileName = fileDir + filename[:-4] + "_air_legacy.txt"
            clipIdx = list(set(clipIdx))
            clipIdx.sort()
            #if airProductionInFile and not outFileName in os.listdir(fileDir) and not "_air_legacy.txt" in filename:
            if airProductionInFile and not "_air_legacy.txt" in filename and not "_naval_legacy.txt" in filename:
                newAirFileContents = ['instant_effect = {\n']
                updatedFileContents = []
                for index in clipIdx:
                    newAirFileContents.append(originalFileContents[index])
                for index1, textLine in enumerate(originalFileContents):
                    if index1 not in clipIdx:
                        updatedFileContents.append(textLine)
                newAirFileContents.append('}\n')
                with open(outFileName, 'a', encoding = "utf-8") as f1:
                    f.close()
                    f1.writelines(newAirFileContents)
                    with open(fileDir + filename, 'w', encoding = "utf-8") as f:
                        f.writelines(updatedFileContents)   
