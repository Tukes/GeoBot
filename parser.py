#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import re
from pprint import pprint

Input = open('mapKML.kml', 'r')
Output = open('marks.txt', 'w')
inputString = Input.read()
pattern = r'<Placemark>(.*?)</Placemark>'
placemarksList = re.findall(pattern, inputString, flags=re.DOTALL)
for c in placemarksList:
    name = re.findall(r'<name>(.*?)</name>', c)[0]
    if name == '':
        name = 'none'
    description = re.findall(r'<description><!\[CDATA\[(.*?)\]\]></description>', c)
    if description == []:
        description = 'none'
    else:
        description = description[0]
    coords = re.findall(r'<coordinates>(.*?)</coordinates>', c)[0].split(',')
    print(coords[0] + " - " + coords[1]+ " - " + coords[2]+ " - " + name + " - " + description, file=Output)
Input.close()
Output.close()
