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
        self.conn = sqlite3.connect(dbname)
        print('Opened database ' + dbname)

    def __del__(self):
        self.conn.close()
        print('Closed database')

    def id4Tele(self, telegramid):
        cursor = self.conn.execute(
        ' SELECT user.userid'
        ' FROM user'
        ' WHERE user.telegramid = \'' + telegramid + '\'')

        for row in cursor:
            return row[0]

        print ('User @' + telegramid + ' not found')
        return -1

    #most commonly needed method
    #check if user has minimum access
    def min4Tele(self, telegramid):
        cursor = self.conn.execute(
        ' SELECT 1'
        ' FROM user'
        ' WHERE user.telegramid = \'' + telegramid + '\''
        ' AND user.ban = 0'
        ' AND user.access > ' + str(UserAccessUnknown))

        for row in cursor:
            return row[0] == 1 #just in case

        return False #user missed something, no access


#for debug/example only
if __name__ == "__main__":
    users = UserDB('userdb.db')
    print('Admin ID ' + str(users.id4Tele('admin')))
    print('Cheater ID ' + str(users.id4Tele('cheater')))
    print('Will @admin see a map? ' + str(users.min4Tele('admin')))
    print('Will @cheater see a map? ' + str(users.min4Tele('cheater'))) #TODO - make a unittest of this?

