#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import telepot
from telepot.delegate import per_chat_id, create_open
import time
import sys

#for python 3
#for puthon 2
#import urllib2 as req

#local stuff
from userdb import UserDB

#structure to hold marker information
class Marker:
    def __init__(self):
        self.lat = 0.0
        self.lon = 0.0
        self.hei = 0.0
        self.name = ''
        self.info = ''

    #todo remove magic numbers
    def relevant(self, lat0, lon0):
        if (abs(self.lon - lon0) <= 0.025) and (abs(self.lat - lat0) <= 0.015):
            return True
        return False

    def requestString(self):
        return '%7C' + str(self.lat) + ',' + str(self.lon)

#Load markers from file, format lon,lat,hei\nlon,lat,hei ...
#TODO skip manual parsing
#TODO add command to reload
#TODO rights to reload?
markerFile = open('marks.txt', 'r')
markerText = markerFile.readlines()
markerFile.close()

markers = []
for c in markerText:
    coords = c.split(' - ') #TODO better parsing
    marker = Marker()
    marker.lat = float(coords[1])
    marker.lon = float(coords[0])
    marker.hei = float(coords[2])
    marker.name = coords[3]
    marker.info = coords[4]
    markers.append(marker)


#Для составления запроса к google static maps, для получения картинки с метками
requestStart = "https://maps.googleapis.com/maps/api/staticmap?center=" #lat, lon
requestEnd = "&zoom=&size=640x640&scale=2&markers=color:red"

"""
    Далее грязь -.- Создаю кнопки и кастомную клавиатуру вручную
    по документации Telegram api, в Telepot, вроде, есть метод
    для создания клавиатур, здесь стоит им воспользоваться
    b14, b15, b16, b17 - кнопки, markup - клавиатура
"""
b14 = {
    'text' : '5км',
    'request_contact' : False,
    'request_location' : False,
    }
b15 = {
    'text' : '1.2км',
    'request_contact' : False,
    'request_location' : False,
    }
b16 = {
    'text' : '700м',
    'request_contact' : False,
    'request_location' : False,
    }
b17 = {
    'text' : '300м',
    'request_contact' : False,
    'request_location' : False,
    }
markup = {
    'keyboard' : [[b17, b16], [b15, b14]],
    'resize_keyboard' : True,
    'one_time_keyboard' : True,
    'selective' : True,
    }

zoomLevel = {            #replaces availableZoom and converts userFriendly radius to zoomLevel
    u'300м' : '17',      #u' ', here 'u' is needed for working on server and doesn't break 
    u'700м' : '16',      #debugging on local machine
    u'1.2км' : '15',
    u'5км' : '14',
    }

answerSelectRadius = 'Выберете интересующий вас радиус'
answerUnknownCommand = 'Неизвестная команда. Пожалуйста пришлите своё местоположение' #Should be changed if new features provided
answerQueryProcessing = 'Запрос обрабатывается. Пожалуйста подождите.'

class Handler(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(Handler, self).__init__(seed_tuple, timeout)
        self._zoom = -1 #not verified yet
        self._teleId = -1 #not known yet

    def on_close(self, exception):
        if (self._teleId > 0) and (self._zoom > 0):
            userdb.setZoom4Tele(self._teleId, self._zoom)
        print('Closing instance for ' + str(self._teleId))

    def on_chat_message(self, msg): #обработчик сообщений
        content_type, chat_type, chat_id = telepot.glance(msg)

        #get them once, reuse through all routine
        self._teleId = msg['from']['id']
        teleUsername = ''

        if ('username' in msg['from']):
            teleUsername = msg['from']['username']

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ' <' + str(self._teleId) + "/@" + teleUsername + "> " + content_type)

        #ask db for user rights if not cached
        if (self._zoom < 0):
            self._zoom = userdb.zoom4Tele(self._teleId)

        #check if user meets minimum level of access
        if (self._zoom <= 0):
            print('User <' + str(self._teleId) + "/@" + teleUsername + '> tried to access bot, but was rejected with ' + str(self._zoom))
            self.sender.sendMessage(answerUnknownCommand, reply_markup = markup)
            return

        # Здесь можно обрабатывать команды вида /command
        if content_type == 'text':
            if (msg['text'] == '/start') or (msg['text'] == '/help'):
                self.sender.sendMessage("Для того, чтобы получить снимок карты с отмеченными на нём метками, пришлите Location (для этого нужно нажать на скрепку(прикрепить) и там выбрать Location), затем задайте интересующий вас радиус (300м, 700м, 1.2км или же 5км). После чего немного подождите.")
                return
        #

        if (content_type == 'location'):
            lat0 = float(msg['location']['latitude'])
            lon0 = float(msg['location']['longitude'])

            #form short list of markers nearby to meet google static map API limit of 2048 chars
            localMarkers = []

            for c in markers:
                if c.relevant(lat0, lon0):
                    localMarkers.append(c)

            #make request string for google maps api for picture
            #see docs at https://developers.google.com/maps/documentation/static-maps/intro
            request = requestStart + str(lat0) + ',' + str(lon0) + requestEnd
            for c in localMarkers:
                request = request + c.requestString()

            self.sender.sendMessage(answerQueryProcessing)
            response = req.urlopen(request.replace("zoom=","zoom="+str(self._zoom)))

            screen = ("screen.png", response) #filename mandatory in telegram API
            self.sender.sendPhoto(screen, reply_markup = markup)

            return

        elif (content_type == 'text'):
                if msg['text'] in zoomLevel:
                    self._zoom = int(zoomLevel[msg['text']])
                    return
 
        self.sender.sendMessage(answerSelectRadius, reply_markup = markup)

#for debug on local machine
TOKEN = input('Provide bot token: ')
DBURL = input('Provide user DB URL: ')
#for debug on server
#TOKEN = sys.argv[1]
#DBURL = sys.argv[2]

userdb = UserDB(DBURL)
bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(Handler, timeout=300)),
])
bot.message_loop(run_forever='Listening ...')

