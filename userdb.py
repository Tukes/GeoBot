#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import sqlite3
import pprint

#class to provision users
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


#for debug/example only
users = UserDB('userdb.db')
print ('Admin ID ' + str(users.id4Tele('admin')))
print ('Cheater ID ' + str(users.id4Tele('cheater')))

