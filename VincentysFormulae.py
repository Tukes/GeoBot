from math import sin
from math import cos
from math import sqrt
from math import pi
from math import atan
from math import tan

"""For debug
lat1 = 59.8709786
lat2 = 59.868941
lon1 = 29.9198099
lon2 = 29.919967
"""

#see https://en.wikipedia.org/wiki/Vincenty%27s_formulae
def distance(lat1, lon1, lat2, lon2):
    lat1 = lat1*pi/180
    lat2 = lat2*pi/180
    lon1 = lon1*pi/180
    lon2 = lon2*pi/180
    
    f = 1/298.257223563
    a = 6378137
    b = 6356752.314245
    U1 = atan((1-f)*tan(lat1))
    U2 = atan((1-f)*tan(lat2))
    L = lon2 - lon1
    lamb = L
    
    """
    cosSa = 0
    cos2dm = 0
    cosd = 0
    sind = 0
    d = 0
    """
    #while lamb > pow(10, -12):
    sind = sqrt(pow(cos(U2)*sin(lamb), 2) + pow(cos(U1)*sin(U2) - sin(U1)*cos(U2)*cos(lamb), 2))
    cosd = sin(U1)*sin(U2)+cos(U1)*cos(U2)*cos(lamb)
    d = atan(sind/cosd)
    sina = (cos(U1)*cos(U2)*sin(lamb))/sind
    cosSa = 1 - pow(sina, 2)
    cos2dm = cosd - (2*sin(U1)*sin(U2))/cosSa
    C = (f/16)*cosSa*(5+f*(4-3*cosSa))
    lamb = L + (1-C)*f*sina*(d+C*sind*(cos2dm+C*cosd*(-1+2*cos2dm)))
    #
    
    uS = cosSa*(a*a-b*b)/(b*b)
    A = 1+(uS/16384)*(4096+uS*(-768+uS*(320-175*uS)))
    B = (uS/1024)*(256+uS*(-128+uS*(74-47*uS)))
    deltaD = B*sind*(cos2dm+0.25*B*(cosd*(-1+2*cos2dm*cos2dm) - (1/6)*B*cos2dm*(-3+4*sind*sind)*(-3+4*cos2dm*cos2dm)))
    s = b*A*(d-deltaD)

    return s

#for debug
#print(distance(lat1, lon1, lat2, lon2))
