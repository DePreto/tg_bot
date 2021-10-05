import requests
import re
import json
from decouple import config
from botrequests import lowprice, highprice, bestdeal, history
from abc import ABC
from telebot import types
import functools


sorted_functions = {
    'lowprice': lowprice.lowprice,
    'highprice': highprice,  # TODO
    'bestdeal': bestdeal,  # TODO
    'history': history  # TODO
}


def registration(cls):  # TODO проверка на уже зарегистрированного пользователя (чтобы не обнулять настройки и историю поиска)
    @functools.wraps(cls)
    def wrapper(user_id, chat_id):
        if user_id in cls.users:
            return cls.users[user_id]
        else:
            return cls(user_id, chat_id)
    return wrapper


class Manager:
    def __init__(self):
        self.user = None
        self.lang = 'ru_RU'
        self.lang_flag = False
        self.cur = 'RUB'
        self.cur_flag = False
        self.city_list = None
        self.flag_advanced_question = None
        self.sorted_func = None

    def get_city_list(self, message):
        self.city_list = Request.location_search(message)
        return self.city_list

    def check_params(self, message):
        Params.check_lang(self, message)  # устанавливаем язык по умолчанию, если он не не был задан ранее
        Params.check_cur(self, message)  # устанавливаем валюту по умолчанию, если она не была задана ранее

    def get_hotels(self):
        hotels_data = Request.hotels_search(self)
        return hotels_data

    def get_photos(self, hotel_id, text):
        photos = Request.photos_search(self, hotel_id)
        result = list()
        for i_photo in photos:
            if not result:
                result.append(types.InputMediaPhoto(caption=text, media=i_photo['baseUrl'].replace('{size}', 'w'),
                                                    parse_mode='HTML'))
            else:
                result.append(types.InputMediaPhoto(media=i_photo['baseUrl'].replace('{size}', 'w')))
        return result

    def set_lang(self, lang):
        self.lang_flag = True
        self.lang = lang

    def set_cur(self, cur):
        self.cur_flag = True
        self.cur = cur

    def set_sorted_func(self, func):
        self.sorted_func = sorted_functions[func]

    @staticmethod
    def get_address(data):
        address = ', '.join([data['address']['streetAddress'], data['address']['locality'],
                             data['address']['countryName'], data['address']['postalCode']])
        return address

    @staticmethod
    def get_landmarks(data):
        distance = ', '.join(['\n*{label}: {distance}'.format(label=info['label'], distance=info['distance'])
                              for info in data['landmarks']])
        return distance

    @property
    def photos_value(self):
        return self.user.photos_value

    @photos_value.setter
    def photos_value(self, value):
        if value > 10:
            raise ValueError
        else:
            self.user.photos_value = value

    @property
    def city_id(self):
        return self.user.city_id

    @city_id.setter
    def city_id(self, value):
        self.user.city_id = value

    @property
    def hotels_value(self):
        return self.user.hotels_value

    @hotels_value.setter
    def hotels_value(self, value):
        if value > 10:
            raise ValueError
        else:
            self.user.hotels_value = value


@registration
class User:
    users = dict()

    def __init__(self, user_id, chat_id):
        self.id = user_id
        self.chat_id = chat_id
        self.city_id = None
        self.city_name = None
        self.hotels_value = None
        self.needed_photo = None
        self.photos_value = None
        self.history = None
        self.users[self.id] = self


class Request(ABC):
    city_url = 'https://hotels4.p.rapidapi.com/locations/search'
    hotel_url = 'https://hotels4.p.rapidapi.com/properties/list'
    photo_url = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'

    headers = {
        'x-rapidapi-host': config("RAPIDHOST"),
        'x-rapidapi-key': config("RAPIDAPIKEY")
    }

    @classmethod
    def location_search(cls, message):
        querystring = {"query": message.text, "locale": "{}".format(Params.set_lang(message.text))}
        response = requests.request("GET", cls.city_url, headers=cls.headers, params=querystring)
        data = json.loads(response.text)
        print(data)
        city_list = {', '.join((city['name'], city['caption'][city['caption'].rindex(' ')+1:])): city['destinationId']
                     for city in data['suggestions'][0]['entities']}
        return city_list

    @classmethod
    def hotels_search(cls, manager):
        hotels_data = manager.sorted_func(user_city_id=manager.city_id, lang=manager.lang, cur=manager.cur,
                                          hotels_value=manager.hotels_value, hotel_url=cls.hotel_url,
                                          headers=cls.headers)
        return hotels_data

    @classmethod
    def photos_search(cls, manager, hotel_id):
        querystring = {"id": "{}".format(hotel_id)}
        response = requests.request("GET", cls.photo_url, headers=cls.headers, params=querystring)
        data = json.loads(response.text)
        photos_address = data["hotelImages"][:manager.photos_value]
        return photos_address


class Params(ABC):
    @staticmethod
    def check_lang(manager, message):
        if manager.lang_flag is False:
            manager.lang = Params.set_lang(message.text)

    @staticmethod
    def check_cur(manager, message):
        if manager.cur_flag is False:
            manager.cur = Params.set_cur(message.text)

    @staticmethod
    def set_lang(text):
        if bool(re.search(r'[А-Яа-я]', text)):
            return 'ru_RU'
        return 'en_US'

    @staticmethod
    def set_cur(text):
        if bool(re.search(r'[А-Яа-я]', text)):
            return 'RUB'
        return 'USD'
