#!/usr/bin/env python 
# -*- coding: utf-8 -*-

#structure to hold marker information
class Marker:
    def __init__(self):
        self.lat = 0.0
        self.lon = 0.0
        self.x   = 0.0
        self.y   = 0.0
        self.name = ''
        self.info = ''
    #

    def relevant(self, x0, y0, dist):
        if abs(self.x - x0) <= dist and abs(self.y - y0) <= dist:
            return True
        return False

    def requestString(self):
        return '%7C' + str(self.lat) + ',' + str(self.lon)
    #
