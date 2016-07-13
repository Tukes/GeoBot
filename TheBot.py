#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import telepot
from telepot.delegate import per_chat_id, create_open
import time
from urllib import request as req   #На сервере использую: import urllib2 as req 
from pprint import pprint     #Для красивого вывода в консоль/лог

"""
    Первые две строчки здесь, чтобы на сервере он не выдавал ошибку
    SyntaxERROR: Non ASCII characte
    при встрече кириллических символов
"""

#Загружаем список координат маркеров и формируем список вида [[,],[,],[,],...]
In = open('parsed.txt', 'r')
In_txt = In.readlines()
In.close()
markers = []
for c in In_txt:
    markers.append(c.split(','))

available_zoom = ('14','15','16','17') #будет использовать в одном if

#Для составления запроса к google static maps, для получения картинки с метками
start = "https://maps.googleapis.com/maps/api/staticmap?center=" #lat, lon
end = "&zoom=&size=640x640&scale=2&markers=color:red"


"""
    Далее грязь -.- Создаю кнопки и кастомную клавиатуру вручную
    по документации Telegram api, в Telepot, вроде, есть метод
    для создания клавиатур, здесь стоит им воспользоваться
    b14, b15, b16, b17 - кнопки, markup - клавиатура
"""
b14 = {
    'text' : '14',
    'request_contact' : False,
    'request_location' : False,
    }
b15 = {
    'text' : '15',
    'request_contact' : False,
    'request_location' : False,
    }
b16 = {
    'text' : '16',
    'request_contact' : False,
    'request_location' : False,
    }
b17 = {
    'text' : '17',
    'request_contact' : False,
    'request_location' : False,
    }
markup = {
    'keyboard' : [[b14, b15], [b16, b17]],
    'resize_keyboard' : True,
    'one_time_keyboard' : True,
    'selective' : True,
    }

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


        # Здесь можно обрабатывать команды вида /command
        """if content_type == 'text':
            if msg['text'] == '/help':
                self.sender.sendMessage("")
                return"""
        #

        if (content_type == 'location') and (not self._isLocSent):
            lat = msg['location']['latitude']
            lon = msg['location']['longitude']
            c_markers = []
            """ По поводу c_markers. В api google static map, есть ограничение
                URL-адреса Google Static Maps API должны содержать не более 2048 символов.
                В следствие чего, необходимо выбрать только те маркеры, которые будут видны
                пользователю """

            for c in markers:
                if (abs(float(c[0])- lon)<=0.025) and (abs(float(c[1])- lat)<=0.015):
                    c_markers.append(c)
            # Числа 0.025 и 0.015 выбирал примерно. Открыл карту, отдалил
            # примерно как при увеличении 14 и в ручную посчитал разницу
            # между верхней границей и нижней - широта, аналогично для долготы

            # Далее составляю запрос (https://developers.google.com/maps/documentation/static-maps/intro?hl=ru)
            self._request = start + str(lat) + ',' + str(lon) + end
            for c in c_markers:
                self._request = self._request + '%7C' + c[1] + ',' + c[0]
                
            self._isLocSent = True
            self.sender.sendMessage("Введите число от 14 до 17, чтобы выбрать увеличение.", reply_markup = markup)

        elif self._isLocSent:
            if (content_type == 'text'):
                if msg['text'] in available_zoom:
                    self._zoom = msg['text']
                    response = req.urlopen(self._request.replace("zoom=","zoom="+self._zoom))
                    screen = ("screen.png", response) #В telegram api обязательно нужно, чтобы у файла было название
                    self.sender.sendMessage("Запрос обрабатывается. Пожалуйста подождите.")
                    self.sender.sendPhoto(screen)
                    self._sizeb = False
                    return
                else:
                    self.sender.sendMessage("Введите число от 14 до 17, чтобы выбрать увеличение.", reply_markup = markup)
                    return
            else:
                self.sender.sendMessage("Введите число от 14 до 17, чтобы выбрать увеличение.", reply_markup = markup)
                return
        else:
            self.sender.sendMessage("Неизвестная команда. Пожалуйста пришлите своё местоположение")
            return

TOKEN = input("Введите Token: ") #Или TOKEN = sys.argv[1] для сервера
bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(Handler, timeout=60)),
])
bot.message_loop(run_forever='Listening ...')
