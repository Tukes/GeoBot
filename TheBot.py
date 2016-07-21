#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import datetime
import codecs
from urllib import request

#Telepot
import telepot
from telepot.delegate import per_chat_id, create_open

#local stuff
from userdb import UserDB #to check user access from remote database
from stereo import StereoProjection

#init cartography
stereo = StereoProjection(59.938630, 30.314130)

#structure to hold marker information
class Marker:
    def __init__(self):
        self.lat = 0.0
        self.lon = 0.0
        self.x   = 0.0
        self.y   = 0.0
        self.name = ''
        self.info = ''
    #

    def relevant(self, x0, y0, dist):
        if abs(self.x - x0) <= dist and abs(self.y - y0) <= dist:
            return True
        return False

    def requestString(self):
        return '%7C' + str(self.lat) + ',' + str(self.lon)
    #

markerFile = codecs.open('marks.txt', 'r', 'utf-8')
markerText = markerFile.readlines()
markerFile.close()

markers = []
for c in markerText:
    #TODO better parsing
    coords = c.split(' - ')
    marker = Marker()
    marker.lat = float(coords[1])
    marker.lon = float(coords[0])
    marker.x, marker.y, k = stereo.geoToStereo(marker.lat, marker.lon)
    marker.name = coords[3]
    marker.info = coords[4]
    markers.append(marker)

print('Starting bot with ' + str(len(markers)) + ' points')

#template for request to Google Maps API
RequestStart = 'https://maps.googleapis.com/maps/api/staticmap?center=' #lat, lon
RequestEnd   = '&size=640x640&scale=2&markers=color:red'

#Create inline keyboard
ButtonMinus = {
    'text' : '-',
    'callback_data' : '-'
    }
ButtonPlus = {
    'text' : '+',
    'callback_data' : '+'
    }
ButtonNewScreen = {
    'text' : 'Новый снимок',
    'callback_data' : 'screen'
    }

InlineKeyboard = {
    'inline_keyboard' : [[ButtonMinus, ButtonPlus], [ButtonNewScreen]]
    }

""" sad that zoom should be an integer for google map api. Don't delete this dict for using maybe in future
zoomOptions = {         #the dict, which matches 3 things: zoomLevel, distanceInt, distanceString
    'zoom' : ['14', '14.25', '14.5', '14.75', '15', '15.25', '15.5', '15.75', '16', '16.25', '16.5', '16.75', '17',],
    'distInt' : [2000, 1500, 1300, 1100, 950, 800, 675, 570, 470, 400, 340, 280, 240,],
    'distStr' : ['2км', '1.5км', '1.3км', '1.1км', '950м', '800м', '675м', '570м', '470м', '400м', '340м', '280м', '240м',],
    }"""

#the dict, which matches 3 things: zoomLevel, distanceInt, distanceString
zoomOptions = {
    'zoom'    : ['14',  '15',   '16',   '17'  ],
    'distInt' : [ 2000,  950,    470,    240  ],
    'distStr' : ['2км', '950м', '470м', '240м']
    }

AnswerUnknownCommand    = 'Неизвестная команда.'
AnswerQueryProcessing   = 'Запрос обрабатывается. Пожалуйста подождите.'
AnswerInstructions      = 'Для того, чтобы получить снимок карты с отмеченными на нём метками, пришлите Location (для этого нужно нажать на скрепку(прикрепить) и там выбрать Location). После чего немного подождите.'
AnswerAccessDenied      = 'У вас нет доступа к функциям этого бота.'
AnswerInline            = 'Радиус: {dist}\nМеток в радиусе: {num}\nИспользуйте "+" и "-" для увеличения/уменьшения радиуса и "Новый снимок" для получения снимка карты с новым радиусом.'

class Handler(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(Handler, self).__init__(seed_tuple, timeout)
        self._access = -1  #not verified yet
        self.lat0 = 0.0    #last user coordinates
        self.lon0 = 0.0    #last user coordinates
        self.x0   = 0.0
        self.y0   = 0.0
        self.option = 1    #last user zoom option
        self.editor = None #for editing messages
    #

    def removeInline(self):
        if self.editor is not None:
            self.editor.editMessageReplyMarkup(reply_markup = None)
            self.editor = None
    #

    def sendSimple(self, msg):
        self.removeInline()
        self.sender.sendMessage(msg, reply_markup = None)
    #

    def sendWithInline(self, msg):
        msgHandle = self.sender.sendMessage(msg, reply_markup = InlineKeyboard)
        self.editor = telepot.helper.Editor(self.bot, msgHandle)
    #

    def editInline(self, inlineMsg):
        if self.editor is not None:
            self.editor.editMessageText(inlineMsg, reply_markup = InlineKeyboard)
    #

    def mapRoutine(self):
        #remove inline keyboard from old message if exists
        self.sendSimple(AnswerQueryProcessing)

        #form short list of markers nearby to meet google static map API limit of 2048 chars
        localMarkers = []

        for c in markers:
            if c.relevant(self.x0, self.y0, zoomOptions['distInt'][self.option]):
                localMarkers.append(c)

        #make request string for google maps api for picture
        #see docs at https://developers.google.com/maps/documentation/static-maps/intro
        requestUrl = RequestStart + str(self.lat0) + ',' + str(self.lon0) + '&zoom=' + zoomOptions['zoom'][self.option] + RequestEnd
        for c in localMarkers:
            requestUrl += c.requestString()

        response = request.urlopen(requestUrl)
        screen = ('screen.png', response) #telegram API require filename
        self.sender.sendPhoto(screen)

        self.sendWithInline(AnswerInline.format(dist = zoomOptions['distStr'][self.option], num = len(localMarkers)))
    #

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        teleId = msg['from']['id'] #user id independent of source chat

        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' <' + str(teleId) + '> ' + content_type)

        #ask db for user rights if not cached
        if (self._access < 0):
            self._access = userdb.access4Tele(teleId)
        #

        #check if user meets minimum level of access
        if (self._access <= 0):
            print('User <' + str(teleId) + '> tried to access bot, but was rejected with ' + str(self._access))
            self.sendSimple(AnswerAccessDenied)
            return
        #

        #handle simple /commands
        if content_type == 'text':
            if (msg['text'] == '/start') or (msg['text'] == '/help'):
                self.sendSimple(AnswerInstructions)
                return
        #

        #handle location
        if (content_type == 'location'):

            self.lat0 = float(msg['location']['latitude'])
            self.lon0 = float(msg['location']['longitude'])
            self.x0, self.y0, k = stereo.geoToStereo(self.lat0, self.lon0)

            self.mapRoutine()

            return
        #

        #Nothing happend -> unknownCommand
        self.sendSimple(AnswerUnknownCommand)
    #

    def on_callback_query(self, msg):
        query_id, from_id, data = telepot.glance(msg, flavor = 'callback_query')

        if data == '+' or data == '-':
            needUpdate = False

            if data == '+' and self.option > 0:
                self.option -= 1
                needUpdate = True

            if data == '-' and self.option < 3:
                self.option += 1
                needUpdate = True

            if needUpdate:
                localMarkersCount = 0
                for c in markers:
                    if c.relevant(self.x0, self.y0, zoomOptions['distInt'][self.option]):
                        localMarkersCount += 1

                #Change the info in message with inline keyboard
                self.editInline(AnswerInline.format(dist = zoomOptions['distStr'][self.option], num = localMarkersCount))
        #
        elif data == 'screen':
            self.mapRoutine()
        #

        self.bot.answerCallbackQuery(query_id, text = None)
    #

    def on_close(self, exception):
        self.removeInline()
    #

TOKEN   = sys.argv[1]
DBURL   = sys.argv[2]
DBPORT  = int(sys.argv[3])
DBTOKEN = sys.argv[4]

userdb = UserDB(DBURL, DBPORT, DBTOKEN)

bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(Handler, timeout = 300)),
])
bot.message_loop(run_forever = 'Listening...')
