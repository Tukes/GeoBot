#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import math

def mapDegreeToRad(degreeString):
    parts = degreeString.split("-")
    degree = float(parts[0]) + (float(parts[1]) / 60.0) + (float(parts[2]) / 360.0)
    return math.radians(degree)

class StereoProjection:
    def __init__(self, lat0Str, lon0Str):
        self.lat0 = mapDegreeToRad(lat0Str)
        self.lon0 = mapDegreeToRad(lon0Str)

if __name__ == "__main__":
    stereo = StereoProjection("59-56-00", "30-19-00") #TODO define simple format for deg-min-sec
    print(str(stereo.lat0))
    print(str(stereo.lon0))

