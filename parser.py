#!/usr/bin/env python 
# -*- coding: ASCII -*-

import re

#for debuging on local machine
#Input = open('mapKML.kml', 'r', encoding="utf8")
#for running on server
Input = open('mapKML.kml', 'r')
Output = open('marks.txt', 'w')
inputString = Input.read()
pattern = r'<Placemark>(.*?)</Placemark>'
placemarksList = re.findall(pattern, inputString, flags=re.DOTALL)
for c in placemarksList:
    nameT = re.findall(r'<name>(.*?)</name>', c)
    if nameT == []:
        name = 'none'
    elif nameT[0] == '':
        name = 'none'
    else:
        name = nameT[0]
    descriptionT = re.findall(r'<description><!\[CDATA\[(.*?)\]\]></description>', c)
    if descriptionT == []:
        description = 'none'
    else:
        description = descriptionT[0]
    coords = re.findall(r'<coordinates>(.*?)</coordinates>', c)[0].split(',')
    #for debuging on local machine
    #print(coords[0] + " - " + coords[1]+ " - " + coords[2]+ " - " + name + " - " + description, file=Output)
    #for running on server
    Output.write(coords[0] + " - " + coords[1]+ " - " + coords[2]+ " - " + name + " - " + description + "\n")
Input.close()
Output.close()
