#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import sqlite3
import pprint

UserAccessUnknown  = 0
UserAccessUser     = 1
UserAccessMod      = 2
UserAccessSuperMod = 3
UserAccessAdmin    = 4

#class to provision users
#TODO consider all IDs as attack vectors
class UserDB:
    def __init__(self, dbname):
        self.conn = sqlite3.connect(dbname, check_same_thread = False) #TODO while it is read-only; later use rw mutex?
        print('Opened database ' + dbname)

    def __del__(self):
        self.conn.close()
        print('Closed database')

    def id4Tele(self, telegramid):
        cursor = self.conn.execute(
        ' SELECT user.userid'
        ' FROM user'
        ' WHERE user.telegramid = ' + str(telegramid))

        for row in cursor:
            return int(row[0])

        return -1

    #most commonly needed method
    #check preferred zoom level; return -1 if user cannot see map
    def zoom4Tele(self, telegramid):
        cursor = self.conn.execute(
        ' SELECT user.zoom'
        ' FROM user'
        ' WHERE user.telegramid = ' + str(telegramid) +
        ' AND user.ban = 0'
        ' AND user.access > ' + str(UserAccessUnknown))

        for row in cursor:
            return int(row[0])

        return -1 #user missed something, no access

    def setZoom4Tele(self, telegramid, zoom):
        self.conn.execute(
        ' UPDATE user'
        ' SET zoom = ' + str(zoom) +
        ' WHERE user.telegramid = ' + str(telegramid))
        self.conn.commit()

    def addUser(self, telegramid, telegramname, access = UserAccessUser):
        self.conn.execute(
        ' INSERT INTO user (telegramid, telegramname, access)'
        ' VALUES (' + str(telegramid) + ', \'' + telegramname + '\',' + str(access) + ')')
        self.conn.commit()


#for debug/example only
if __name__ == "__main__":
    users = UserDB('userdb.db')
    print('<1/@admin> internal ID ' + str(users.id4Tele(1)))
    print('<567/@cheater> internal ID ' + str(users.id4Tele(567)))
    print('Will <1/@admin> see a map? ' + str(users.zoom4Tele(1) > 0))
    print('Will <567/@cheater> see a map? ' + str(users.zoom4Tele(567) > 0)) #TODO - make a unittest of this?
    print('<1/@admin> prefers zoom level ' + str(users.zoom4Tele(1)))
