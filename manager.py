from botrequests import main_request, lowprice, highprice, bestdeal, history
from telebot import types
from params import Params
import functools


sorted_functions = {
    'lowprice': lowprice.lowprice,
    'highprice': highprice.highprice,
    'bestdeal': bestdeal.bestdeal,
    'history': history  # TODO
}


def registration(cls):  # проверка на зарегистрированного пользователя (чтобы не обнулять настройки и историю поиска)
    @functools.wraps(cls)
    def wrapper(user_id, chat_id):
        if user_id in cls.users:
            return cls.users[user_id]
        return cls(user_id, chat_id)
    return wrapper


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
        self.price_range = None
        self.dist_range = None
        self.history = None
        self.users[self.id] = self


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
        self.city_list = main_request.Request.location_search(message)
        return self.city_list

    def check_params(self, message):
        Params.check_lang(self, message)  # устанавливаем язык по умолчанию, если он не не был задан ранее
        Params.check_cur(self, message)  # устанавливаем валюту по умолчанию, если она не была задана ранее

    def get_hotels(self):
        hotels_data = main_request.Request.hotels_search(self)
        return hotels_data

    def get_photos(self, hotel_id, text):
        photos = main_request.Request.photos_search(self, hotel_id)
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
        if func == 'bestdeal':
            self.flag_advanced_question = True
        else:
            self.flag_advanced_question = None
        self.sorted_func = sorted_functions[func]

    @staticmethod
    def get_address(data):
        address = ', '.join(list(filter(lambda x: isinstance(x, str) and len(x) > 2, list(data['address'].values()))))
        return address

    @staticmethod
    def get_landmarks(data):
        distance = ', '.join(['\n*{label}: {distance}'.format(label=info['label'], distance=info['distance'])
                              for info in data['landmarks']])
        return distance

    @property
    def price_range(self):
        return self.user.price_range

    @price_range.setter
    def price_range(self, value):
        self.user.price_range = value

    @property
    def dist_range(self):
        return self.user.dist_range

    @dist_range.setter
    def dist_range(self, value):
        self.user.dist_range = value

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
