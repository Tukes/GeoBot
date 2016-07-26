#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#shameless copypaste from
#https://programmingadvent.blogspot.ru/2013/06/kmzkml-file-parsing-with-python.html

import codecs
import xml.sax, xml.sax.handler

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

parser = xml.sax.make_parser()
handler = PlacemarkHandler()
parser.setContentHandler(handler)

kml = codecs.open('mapKML.kml', 'r', 'utf-8')
parser.parse(kml)
kml.close()

txt = codecs.open('marks.txt', 'w', 'utf-8')
names = sorted(handler.mapping.keys())
for name in names:
        coords = handler.mapping[name]['coordinates'].split(',')
        description = ''
        if 'description' in handler.mapping[name]:
            description = handler.mapping[name]['description']
        else:
            description = 'none'
        txt.write(coords[0] + ' - ' + coords[1]+ ' - ' + coords[2]+ ' - ' + name + ' - ' + description + '\n')
txt.close()
