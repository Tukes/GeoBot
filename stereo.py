#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import math

def _xi_(phi, e):
    sinPhi = math.sin(phi)
    eSinPhi = e * sinPhi
    result = (1.0 - eSinPhi)/(1.0 + eSinPhi)
    result = math.pow(result, e)
    result = ((1.0 + sinPhi)/(1.0 - sinPhi)) * result
    result = math.sqrt(result)
    result = 2.0 * math.atan(result)
    result = result - (math.pi / 2.0)
    return result

def _m_(phi, e):
    eSinPhi = e * math.sin(phi)
    result = (math.cos(phi))/(math.sqrt(1.0 - (eSinPhi * eSinPhi)))
    return result

class StereoProjection:
    def __init__(self, lat0, lon0): #shirota-dolgota phi-lambda N&E - positive, S&W - negative
        self.lat0 = math.radians(lat0)
        self.lon0 = math.radians(lon0)
        self.a = 6378206.4
        self.e = 0.0822719
        self.k0 = 0.9999

        self.m0 = _m_(self.lat0, self.e)

        xi0 = _xi_(self.lat0, self.e)
        self.sinXi0 = math.sin(xi0)
        self.cosXi0 = math.cos(xi0)

    def geoToStereo(self, lat1, lon1):
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)

        xi1 = _xi_(lat1, self.e)
        m1 = _m_(lat1, self.e)

        sinXi1 = math.sin(xi1)
        cosXi1 = math.cos(xi1)
        
        dLambda = lon1 - self.lon0
        sinDLambda = math.sin(dLambda)
        cosDLambda = math.cos(dLambda)

        A = (2.0 * self.a * self.k0 * self.m0)/(self.cosXi0 * (1.0 + self.sinXi0 * sinXi1 + self.cosXi0 * cosXi1 * cosDLambda))

        x = A * cosXi1 * sinDLambda
        y = A * (self.cosXi0 * sinXi1 - self.sinXi0 * cosXi1 * cosDLambda)
        k = (A * cosXi1)/(self.a * m1)

        return (x, y, k)
        

if __name__ == "__main__":
    stereo = StereoProjection(40.0, -100.0)
    x, y, k = stereo.geoToStereo(30.0, -90.0)
    print(str(x))
    print(str(y))
    print(str(k))

