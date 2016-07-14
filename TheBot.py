#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import telepot
from telepot.delegate import per_chat_id, create_open
import time
from pprint import pprint

#for python 3
from urllib import request as req
#for puthon 2
#import urllib2 as req
#for sys.argv[1]
#import sys

#local stuff
from userdb import UserDB

#structure ho hold marker information
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

#get user base object
userdb = UserDB('userdb.db')

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

#Основное тело:
class Handler(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(Handler, self).__init__(seed_tuple, timeout)
        #Создаем локальные переменные на чат
        self._zoom = ''             #Увеличение
        self._isLocSent = False     #Отправил ли пользователь нам Location
        self._request = ''          #Запрос для google static maps

    def on_chat_message(self, msg): #обработчик сообщений
        content_type, chat_type, chat_id = telepot.glance(msg)

        #Здесь просто делаю некий лог_____________________________________________________________________________________________________________________
        """ Try здесь нужен, т.к. если в нике есть emoji,
            то поднимается ошибка UnicodeEncodeError """
        try:
            pprint(time.ctime() + "  " + msg['chat']['username'] + "  " + content_type) # можно поставить pprint(msg), чтобы посмотреть
                                                                                        # как выглядит структура msg (какие данные есть/как обращаться)
        except UnicodeEncodeError:
            print("UnicodeEncodeError. Probably emoji in username")

        except:
            print("Another Error")
        #_________________________________________________________________________________________________________________________________________________

        #check if user meets minimum level of access
        if (userdb.min4Tele(msg['from']['username']) == False):
                print('User ' + msg['from']['username'] + ' tried to access bot, but was rejected')
                self.sender.sendMessage(answerUnknownCommand)
                return

        # Здесь можно обрабатывать команды вида /command
        """if content_type == 'text':
            if msg['text'] == '/help':
                self.sender.sendMessage("")
                return"""
        #

        if (content_type == 'location') and (not self._isLocSent):
            lat0 = float(msg['location']['latitude'])
            lon0 = float(msg['location']['longitude'])

            #form short list of markers nearby to meet google static map API limit of 2048 chars
            localMarkers = []

            for c in markers:
                if c.relevant(lat0, lon0):
                    localMarkers.append(c)

            #make request string for google maps api for picture
            #see docs at https://developers.google.com/maps/documentation/static-maps/intro
            self._request = requestStart + str(lat0) + ',' + str(lon0) + requestEnd
            for c in localMarkers:
                self._request = self._request + c.requestString()
                
            self._isLocSent = True
            self.sender.sendMessage(answerSelectRadius, reply_markup = markup)

        elif self._isLocSent:
            if (content_type == 'text'):
                if msg['text'] in zoomLevel:
                    self._zoom = zoomLevel[msg['text']]
                    response = req.urlopen(self._request.replace("zoom=","zoom="+self._zoom))
                    screen = ("screen.png", response) #В telegram api обязательно нужно, чтобы у файла было название
                    self.sender.sendMessage(answerQueryProcessing)
                    self.sender.sendPhoto(screen)
                    self._isLocSent = False
                    return
                else:
                    self.sender.sendMessage(answerSelectRadius, reply_markup = markup)
                    return
            else:
                self.sender.sendMessage(answerSelectRadius, reply_markup = markup)
                return
        else:
            self.sender.sendMessage(answerUnknownCommand)
            return
#for debug on local machine
TOKEN = input('Provide bot token: ')
#for debug on server
#TOKEN = sys.argv[1]

bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(Handler, timeout=60)),
])
bot.message_loop(run_forever='Listening ...')
