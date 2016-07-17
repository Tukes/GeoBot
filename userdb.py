#!/usr/bin/env python 
# -*- coding: utf-8 -*-

#for python 3
from urllib import request as req
#for puthon 2
#import urllib2 as req

#class to provision users
class UserDB:
    def __init__(self, dburl):
        self._dburl = dburl

    #check preferred zoom level; return 0 if user cannot see map
    def zoom4Tele(self, telegramid):
        print ('Check access of ' + str(telegramid))
        #debug only
        return 16

    def setZoom4Tele(self, telegramid, zoom):
        print ('Set zoom level of ' + str(telegramid) + ' to ' + str(zoom))

