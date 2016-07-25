#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from hashlib import md5
import datetime
import socket

#class to provision users
class UserDB:
    def __init__(self, dburl, dbport, dbtoken):
        self._dburl = dburl
        self._dbport = dbport
        self._dbtoken = dbtoken

    def access4Tele(self, telegramid): 
        print('Check access of ' + str(telegramid))

        try:
            now = datetime.datetime.utcnow()
            accessToken = md5((eval(self._dbtoken)).encode('utf-8')).hexdigest()
        
            sock = socket.socket()
            sock.connect((self._dburl, self._dbport))
            sock.send(('%s %s' % (accessToken, telegramid)).encode('utf-8'))
            result = sock.recv(1024).decode('utf-8')
            sock.close()
        
            print('Access check returned ' + result)
            return int(result)
        except:
            pass

        print('Access granted by default')
        return 1

