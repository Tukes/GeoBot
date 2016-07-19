#!/usr/bin/env python 
# -*- coding: UTF-8 -*-

import re

Input = open('mapKML.kml', 'r')
inputString = Input.read()
Input.close()

Output = open('marks.txt', 'w')

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
    Output.write(coords[0] + " - " + coords[1]+ " - " + coords[2]+ " - " + name + " - " + description + "\n")

Output.close()
