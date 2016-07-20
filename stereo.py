#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import math

def mapDegreeToRad(degreeString):
    parts = degreeString.split("-")
    degree = float(parts[0]) + (float(parts[1]) / 60.0) + (float(parts[2]) / 360.0)
    return math.radians(degree)

def xi(phi, e):
    sinPhi = math.sin(phi)
    eSinPhi = e * sinPhi
    result = ((1.0 + sinPhi)/(1.0 - sinPhi))*((1.0 - eSinPhi)/(1.0 + eSinPhi))
    result = math.pow(result, e / 2.0)
    result = 2.0 * math.atan2(result)
    result = result - (math.pi / 2.0)
    return result

class StereoProjection:
    def __init__(self, lat0Str, lon0Str): #shirota-dolgota phi-lambda
        self.lat0 = mapDegreeToRad(lat0Str)
        self.lon0 = mapDegreeToRad(lon0Str)

    def geoToStereo(latStr, lonStr):
        lat1 = mapDegreeToRad(latStr)
        lon1 - mapDegreeToRad(lonStr)

        #define ellipsoid parameters
        #Clarke 1866 for sake of numeric examples
        a = 6378206.4
        e = 0.0822719
        k0 = 0.9999
        #Regular WGS-84
        #TODO a
        #TODO e
        #TODO k0

        xi0 = xi(self.lat0, e)
        xi1 = xi(lat1, e)


if __name__ == "__main__":
    stereo = StereoProjection("59-56-00", "30-19-00") #TODO define simple format for deg-min-sec
    print(str(stereo.lat0))
    print(str(stereo.lon0))

