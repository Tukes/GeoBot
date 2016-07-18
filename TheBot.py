#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import telepot
from telepot.delegate import per_chat_id, create_open
import time
from pprint import pprint
from VincentysFormulae import distance #to get distance by lat and lon of two points

#for python 3
from urllib import request as req
#for puthon 2
#import urllib2 as req
#for sys.args
#import sys

#structure ho hold marker information
class Marker:
    def __init__(self):
        self.lat = 0.0
        self.lon = 0.0
        self.hei = 0.0
        self.name = ''
        self.info = ''

    def relevant(self, lat0, lon0, dist):
        if (distance(self.lat, self.lon, lat0, lon0) + 20) < dist: #plus 20 because of inaccuracy 
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


#Creating an inline keyboard
bMinus = {
    'text' : '-',
    'callback_data' : '-',
    }
bPlus = {
    'text' : '+',
    'callback_data' : '+',
    }
newScreen = {
    'text' : 'Новый снимок',
    'callback_data' : 'screen',
    }

inlineKeyboard = {
    'inline_keyboard' : [[bMinus, bPlus], [newScreen]]
    }
###

""" sad that zoom should be an integer for google map api. Don't delete this dict for using maybe in future
zoomOptions = {         #the dict, which matches 3 things: zoomLevel, distanceInt, distanceString 
    'zoom' : ['14', '14.25', '14.5', '14.75', '15', '15.25', '15.5', '15.75', '16', '16.25', '16.5', '16.75', '17',],
    'distInt' : [2000, 1500, 1300, 1100, 950, 800, 675, 570, 470, 400, 340, 280, 240,],
    'distStr' : ['2км', '1.5км', '1.3км', '1.1км', '950м', '800м', '675м', '570м', '470м', '400м', '340м', '280м', '240м',],
    }"""

zoomOptions = {         #the dict, which matches 3 things: zoomLevel, distanceInt, distanceString 
    'zoom' : ['14', '15', '16', '17',],
    'distInt' : [2000, 950, 470, 240,],
    'distStr' : ['2км', '950м', '470м',  '240м',],
    }

answerUnknownCommand = 'Неизвестная команда.' 
answerQueryProcessing = 'Запрос обрабатывается. Пожалуйста подождите.'
answerInstructions = 'Для того, чтобы получить снимок карты с отмеченными на нём метками, пришлите Location (для этого нужно нажать на скрепку(прикрепить) и там выбрать Location). После чего немного подождите.'

#Основное тело:
class Handler(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(Handler, self).__init__(seed_tuple, timeout)
        #Создаем локальные переменные на чат
        self._request = ''          #Запрос для google static maps
        self.lat0 = 0.0             #because now we need to store lat0 and lon0
        self.lon0 = 0.0
        self.option = 1    #replaces zoom. 0-3, 1 is for zoom = 15, dist = 950
        self.editor = None #for editing messages
        self.localMarkersCount = 0 #I need it, trust me. Ohh, I mean it's needed to remove inlineKeyboard when new screen is requested. Otherwise, UnboundLocalError: local variable 'localMarkersCount' gonna be raised 

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
            print("Another Error. Probably no @nickname")
        #_________________________________________________________________________________________________________________________________________________


        # Здесь можно обрабатывать команды вида /command
        if content_type == 'text':
            if (msg['text'] == '/start') or (msg['text'] == '/help'):
                self.sender.sendMessage(answerInstructions)
                return
        #

        if (content_type == 'location'):
             #remove inline keyboard from old message if exists
            if self.editor is not None:
                self.editor.editMessageText('Радиус: ' + zoomOptions['distStr'][self.option] + '\nМетки в радиусе: ' + str(self.localMarkersCount) + '\nИспользуйте "+" и "-" для увеличения/уменьшения радиуса и "Новый снимок" для получения снимка карты с новым радиусом.')

            self.sender.sendMessage(answerQueryProcessing)
            self.lat0 = float(msg['location']['latitude'])
            self.lon0 = float(msg['location']['longitude'])

            #form short list of markers nearby to meet google static map API limit of 2048 chars
            localMarkers = []
            self.localMarkersCount = 0
            
            for c in markers:
                if c.relevant(self.lat0, self.lon0, zoomOptions['distInt'][self.option]):
                    localMarkers.append(c)
                    self.localMarkersCount += 1 #sad that you cant use self.localMarkersCount++ in python :c

            #make request string for google maps api for picture
            #see docs at https://developers.google.com/maps/documentation/static-maps/intro
            self._request = requestStart + str(self.lat0) + ',' + str(self.lon0) + requestEnd
            for c in localMarkers:
                self._request = self._request + c.requestString()

            response = req.urlopen(self._request.replace("zoom=","zoom="+zoomOptions['zoom'][self.option]))
            screen = ("screen.png", response) #В telegram api обязательно нужно, чтобы у файла было название
            self.sender.sendPhoto(screen)
            #self.editor to sent edit message
            sentMessage = self.sender.sendMessage('Радиус: ' + zoomOptions['distStr'][self.option] + '\nМеток в радиусе: ' + str(self.localMarkersCount) + '\nИспользуйте "+" и "-" для увеличения/уменьшения радиуса и "Новый снимок" для получения снимка карты с новым радиусом.', reply_markup = inlineKeyboard)
            self.editor = telepot.helper.Editor(bot, sentMessage)
            return

        #Nothing happend -> unknownCommand
        self.sender.sendMessage(answerUnknownCommand)


    def on_callback_query(self, data):
        if data['data'] == '+':
            if self.option > 0:
                self.option -= 1 #Yap, small paradox -.- Minus here because I am originally made a zoomOptions[''][i+1]  radius less than zoomOptions[''][i]. Whoops. And I am too lazy to fix it .-. So there is a paradox^^
                self.localMarkersCount = 0
                for c in markers:
                    if c.relevant(self.lat0, self.lon0, zoomOptions['distInt'][self.option]):
                        self.localMarkersCount += 1

                #Change the info in message with inline keyboard
                self.editor.editMessageText('Радиус: ' + zoomOptions['distStr'][self.option] + '\nМеток в радиусе: ' + str(self.localMarkersCount) + '\nИспользуйте "+" и "-" для увеличения/уменьшения радиуса и "Новый снимок" для получения снимка карты с новым радиусом.', reply_markup = inlineKeyboard)
            return
        
        elif data['data'] == '-':
            if self.option < 3:
                self.option += 1
                self.localMarkersCount = 0
                for c in markers:
                    if c.relevant(self.lat0, self.lon0, zoomOptions['distInt'][self.option]):
                        self.localMarkersCount += 1

                #Change the info in message with inline keyboard
                self.editor.editMessageText('Радиус: ' + zoomOptions['distStr'][self.option] + '\nМеток в радиусе: ' + str(self.localMarkersCount) + '\nИспользуйте "+" и "-" для увеличения/уменьшения радиуса и "Новый снимок" для получения снимка карты с новым радиусом.', reply_markup = inlineKeyboard)
            return
        
        elif data['data'] == 'screen':
            #Remove inline keyboard in message with inline keyboard
            self.editor.editMessageText('Радиус: ' + zoomOptions['distStr'][self.option] + '\nМеток в радиусе: ' + str(self.localMarkersCount) + '\nИспользуйте "+" и "-" для увеличения/уменьшения радиуса и "Новый снимок" для получения снимка карты с новым радиусом.')

            self.sender.sendMessage(answerQueryProcessing)
            
            localMarkers = []
            self.localMarkersCount = 0
            
            for c in markers:
                if c.relevant(self.lat0, self.lon0, zoomOptions['distInt'][self.option]):
                    localMarkers.append(c)
                    self.localMarkersCount += 1
            self._request = requestStart + str(self.lat0) + ',' + str(self.lon0) + requestEnd
            for c in localMarkers:
                self._request = self._request + c.requestString()

            response = req.urlopen(self._request.replace("zoom=","zoom="+zoomOptions['zoom'][self.option]))
            screen = ("screen.png", response)
            self.sender.sendPhoto(screen)

            #new message to edit
            sentMessage = self.sender.sendMessage('Радиус: ' + zoomOptions['distStr'][self.option] + '\nМеток в радиусе: ' + str(self.localMarkersCount) + '\nИспользуйте "+" и "-" для увеличения/уменьшения радиуса и "Новый снимок" для получения снимка карты с новым радиусом.', reply_markup = inlineKeyboard)
            self.editor = telepot.helper.Editor(bot, sentMessage)
            return

    def on_close(self, exception):
        #remove inline keyboard on timeout if exists
        if self.editor is not None:
            self.editor.editMessageText('Радиус: ' + zoomOptions['distStr'][self.option] + '\nМеток в радиусе: ' + str(self.localMarkersCount) + '\nИспользуйте "+" и "-" для увеличения/уменьшения радиуса и "Новый снимок" для получения снимка карты с новым радиусом.')
            




#for debug on local machine or raw_input for debug on server
TOKEN = input("Введите Token: ")
#for running on server
#TOKEN = sys.argv[1]

bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(Handler, timeout=300)),
])
bot.message_loop(run_forever='Listening ...')
