#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#shameless copypaste from
#https://programmingadvent.blogspot.ru/2013/06/kmzkml-file-parsing-with-python.html

import codecs
import xml.sax, xml.sax.handler

#local stuff
from marker import Marker

UnwantedChars = ' \r\n\t'

class PlacemarkHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.inName = False # handle XML parser events
        self.inPlacemark = False
        self.mapping = {}
        self.buffer = ''
        self.nameTag = ''

    def startElement(self, name, attributes):
        if name == 'Placemark': # on start Placemark tag
            self.inPlacemark = True
            self.buffer = ''
        if self.inPlacemark:
            if name == 'name': # on start title tag
                self.inName = True # save name text to follow

    def characters(self, data):
        if self.inPlacemark: # on text within tag
            self.buffer += data # save text if in title

    def endElement(self, name):
        self.buffer = self.buffer.strip(UnwantedChars)

        if name == 'Placemark':
            self.inPlacemark = False
            self.nameTag = '' #clear current name
        elif name == 'name' and self.inPlacemark:
            self.inName = False # on end title tag
            self.nameTag = self.buffer.strip(UnwantedChars)
            if self.nameTag == '':
                self.nameTag = 'none'
            self.mapping[self.nameTag] = {}
        elif self.inPlacemark:
            if name in self.mapping[self.nameTag]:
                self.mapping[self.nameTag][name] += self.buffer
            else:
                self.mapping[self.nameTag][name] = self.buffer
        self.buffer = ''

def readFromFile(filename):
    markers = []

    parser = xml.sax.make_parser()
    handler = PlacemarkHandler()
    parser.setContentHandler(handler)

    kml = codecs.open(filename, 'r', 'utf-8')
    parser.parse(kml)
    kml.close()

    names = sorted(handler.mapping.keys())
    for name in names:
        coords = handler.mapping[name]['coordinates'].split(',')

        description = ''
        if 'description' in handler.mapping[name]:
            description = handler.mapping[name]['description']
        else:
            description = 'none'

        marker = Marker()
        marker.lat = float(coords[1])
        marker.lon = float(coords[0])
        marker.name = name
        marker.info = description
        markers.append(marker)
    return markers

if __name__ == '__main__':
    markers = readFromFile('mapKML.kml')
    txt = codecs.open('marks.txt', 'w', 'utf-8')
    for marker in markers:
        txt.write(str(marker.lon) + ' - ' + str(marker.lat) + ' - 0.0 - ' + marker.name + ' - ' + marker.info + '\n')
    txt.close()
