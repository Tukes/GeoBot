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
    result = 2.0 * math.atan(result)
    result = result - (math.pi / 2.0)
    return result

def m(phi, e):
    eSinPhi = e * math.sin(phi)
    result = (math.cos(phi))/(math.pow(1.0 - (eSinPhi * eSinPhi), 0.5))
    return result

def printRadians(rad):
    print(str(math.degrees(rad)))

class StereoProjection:
    def __init__(self, lat0Str, lon0Str): #shirota-dolgota phi-lambda
        self.lat0 = mapDegreeToRad(lat0Str)
        self.lon0 = mapDegreeToRad(lon0Str)

    def geoToStereo(self, latStr, lonStr):
        lat1 = mapDegreeToRad(latStr)
        lon1 = mapDegreeToRad(lonStr)

        #define ellipsoid parameters
        #Clarke 1866 for sake of numeric examples
        a = 6378206.4
        e = 0.0822719
        k0 = 0.9999
        #Regular WGS-84
        #TODO a
        #TODO e
        #TODO k0

        #TODO move to ctor all wtf0
        xi0 = xi(self.lat0, e)
        xi1 = xi(lat1, e)

        m0 = m(self.lat0, e)
        m1 = m(lat1, e)

        printRadians(xi1)
        printRadians(xi0)
        print(str(m1))
        print(str(m0))

        cosXi1 = math.cos(xi1)
        sinXi1 = math.sin(xi1)

        sinXi0 = math.sin(xi0)
        cosXi0 = math.cos(xi0)
        
        dLambda = lon1 - self.lon0
        sinDLambda = math.sin(dLambda)
        cosDLambda = math.cos(dLambda)

        A = (2.0 * a * k0 * m1)/(cosXi1 * (1.0 - sinXi1 * sinXi0 + cosXi1 * cosXi0 * cosDLambda))

        x = A * cosXi0 * sinDLambda
        y = A * (cosXi1 * sinXi0 - sinXi1 * cosXi0 * cosDLambda)
        k = (A * cosXi0)/(a * m0)
        
        print(str(A))

        return (x, y, k)
        

if __name__ == "__main__":
    stereo = StereoProjection("59-56-00", "30-19-00") #TODO define simple format for deg-min-sec
    print(str(stereo.lat0))
    print(str(stereo.lon0))
    x, y, k = stereo.geoToStereo("30-00-00", "90-00-00")
    print(str(x))
    print(str(y))
    print(str(k))

