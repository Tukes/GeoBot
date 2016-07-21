#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

def _m_xi_(phi, e):
    sinPhi = math.sin(phi)
    eSinPhi = e * sinPhi

    m = math.cos(phi) / math.sqrt(1.0 - eSinPhi * eSinPhi)

    xi = (1.0 - eSinPhi) / (1.0 + eSinPhi)
    xi = math.pow(xi, e)
    xi = xi * (1.0 + sinPhi) / (1.0 - sinPhi)
    xi = math.sqrt(xi)
    xi = 2.0 * math.atan(xi) - math.pi / 2.0
    return (m, xi)

class StereoProjection:
    #shirota-dolgota phi-lambda N&E - positive, S&W - negative
    def __init__(self, lat0, lon0, a = None, e = None, k0 = None):
        self.lat0 = math.radians(lat0)
        self.lon0 = math.radians(lon0)

        #defaul is WGS-84
        if a == None:
            self.a = 6378137.0
            b = 6356752.314140
            self.e = math.sqrt(1 - b * b / self.a / self.a)
            self.k0 = 1.0
        else:
            self.a = a
            self.e = e
            self.k0 = k0

        self.m0, xi0 = _m_xi_(self.lat0, self.e)

        self.sinXi0 = math.sin(xi0)
        self.cosXi0 = math.cos(xi0)

    def geoToStereo(self, lat1, lon1):
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)

        m1, xi1 = _m_xi_(lat1, self.e)

        sinXi1 = math.sin(xi1)
        cosXi1 = math.cos(xi1)

        dLambda = lon1 - self.lon0
        sinDLambda = math.sin(dLambda)
        cosDLambda = math.cos(dLambda)

        A = 2.0 * self.a * self.k0 * self.m0 / self.cosXi0 / (1.0 + self.sinXi0 * sinXi1 + self.cosXi0 * cosXi1 * cosDLambda)

        x = A * cosXi1 * sinDLambda
        y = A * (self.cosXi0 * sinXi1 - self.sinXi0 * cosXi1 * cosDLambda)
        k = A * cosXi1 / self.a / m1

        return (x, y, k)


if __name__ == "__main__":
    #do the book numeric examples
    print("Example on page 313")
    stereo = StereoProjection(40.0, -100.0, 6378206.4, 0.0822719, 0.9999)
    x, y, k = stereo.geoToStereo(30.0, -90.0)
    print(str(x))
    print(str(y))
    print(str(k))
    print("Book gives 971630.8 -1063049.3 1.0121248")

    #Saint-Pete with WGS-84
    print("Find distance to Rif fort")
    stereo = StereoProjection(59.938630, 30.314130)
    #around Rif fort
    x, y, k = stereo.geoToStereo(60.033175, 29.638552)
    print(str(x))
    print(str(y))
    print(str(k))
    distance = math.sqrt(x * x + y * y)
    print(str(distance / 1000.0) + "km")
    print("Should be around 39 km")

