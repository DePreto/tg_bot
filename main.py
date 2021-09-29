import requests
import re
import telebot
from decouple import config
from telebot import types
import json
from botrequests import lowprice

# from botrequests import highprice
# from botrequests import bestdeal
# from botrequests import history

bot = telebot.TeleBot(config('TOKEN'))

low_emodji = '\U00002198'
high_emodji = '\U00002197'
best_emodji = '\U00002705'
history_emodji = '\U0001F4D3'
head_emodji = '\U0001F3E8'
point_emodji = '\U0001F4CC'


class Server:
    """Класс сервер. Выполняет запросы, хранит полученную информацию, выполняет извелечение данных."""

    city_url = 'https://hotels4.p.rapidapi.com/locations/search'
    hotel_url = 'https://hotels4.p.rapidapi.com/properties/list'
    photo_url = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'

    headers = {
        'x-rapidapi-host': config("RAPIDHOST"),
        'x-rapidapi-key': config("RAPIDAPIKEY")
    }

    def __init__(self):
        self.cities_data = dict()
        self.hotels_data = dict()
        self.photos_data = list()
        self.address = None
        self.distance = None

    def get_city(self, message):
        Params.check_lang(message)  # устанавливаем язык по умолчанию, если он не не был задан ранее
        Params.check_cur(message)
        querystring = {"query": message.text, "locale": "{}_{}".format(user.lang, user.lang.upper())}
        response = requests.request("GET", self.city_url, headers=self.headers, params=querystring)
        data = json.loads(response.text)
        self.cities_data = {city['name']: city['destinationId'] for city in data['suggestions'][0]['entities']}
        return self.cities_data

    @property
    def get_hotels(self):
        self.hotels_data = user.sorted_func(user_city_id=user.city_id, lang=user.lang, cur=user.cur,
                                            number_of_options=user.number_of_options)
        print(self.hotels_data)
        return self.hotels_data

    def get_photos(self, hotel_id, text):
        querystring = {"id": "{}".format(hotel_id)}
        response = requests.request("GET", self.photo_url, headers=self.headers, params=querystring)
        data = json.loads(response.text)
        data = data["hotelImages"][:user.number_of_photo]
        self.photos_data = list()
        for photo in data:
            if not self.photos_data:
                self.photos_data.append(
                    types.InputMediaPhoto(caption=text, media=photo['baseUrl'].replace('{size}', 'w'),
                                          parse_mode='MarkdownV2'))
            else:
                self.photos_data.append(types.InputMediaPhoto(media=photo['baseUrl'].replace('{size}', 'w')))
        return self.photos_data

    def get_address(self, data):
        self.address = ', '.join([data['address']['streetAddress'], data['address']['locality'],
                                  data['address']['countryName'], data['address']['postalCode']])
        return self.address

    def get_distance(self, data):
        self.distance = ', '.join(['\n{label}: {distance}'.format(label=info['label'], distance=info['distance'])
                                   for info in data['landmarks']])
        return self.distance


class UserChoice:
    def __init__(self):
        self.city_id = None
        self.city_name = None  # TODO
        self.number_of_options = None  # count_hotels
        self.needed_photo = None
        self.number_of_photo = None  # count_photos
        self.cur = None
        self.lang = None
        self.sorted_func = None
        self.flag_advanced_question = False
        self.min_price = None  # TODO
        self.max_price = None  # TODO
        self.min_distance = None  # TODO
        self.max_distance = None  # TODO
        self.history = None  # TODO


class Params:
    @staticmethod
    def check_lang(message):
        if user.lang is None:
            user.lang = Params.set_lang(message.text)

    @staticmethod
    def check_cur(message):
        if user.cur is None:
            user.cur = Params.set_cur(message.text)

    @staticmethod
    def set_lang(text):
        if bool(re.search(r'[А-Яа-я]', text)):
            return 'ru'
        return 'en'

    @staticmethod
    def set_cur(text):
        if bool(re.search(r'[А-Яа-я]', text)):
            return 'RUB'
        return 'USD'


@bot.message_handler(regexp=r'.*[Пп]ривет.*')
@bot.message_handler(commands=['start', 'hello_world'])
def start_message(message):
    bot.send_message(message.chat.id, 'Помоги мне подобрать для тебя самое выгодное предложение (выбери команду): '
                                      '\n\n {} /lowprice - Узнать топ самых дешёвых отелей в городе'
                                      '\n\n {} /highprice - Узнать топ самых дорогих отелей в городе'
                                      '\n\n {} /bestdeal - Узнать топ отелей, наиболее подходящих по цене '
                                      'и расположению от центра (самые дешёвые и находятся ближе всего к центру)'
                                      '\n\n {} /history - Узнать историю поиска отелей'.format(low_emodji,
                                                                                               high_emodji,
                                                                                               best_emodji,
                                                                                               history_emodji))


@bot.message_handler(commands=['lowprice'])
def set_sorted_func(message):
    ask_for_city(message, lowprice.lowprice)


# @bot.message_handler(commands=['highprice'])
# def set_sorted_func(message):
#     ask_for_city(message, highprice.highprice)


# @bot.message_handler(commands=['bestdeal'])
# def set_sorted_func(message):
#     ask_for_city(message, bestdeal.bestdeal)


# @bot.message_handler(commands=['history'])
# def set_sorted_func(message):
#     pass
#     # user.sorted_func = lowprice.lowprice  # TODO


def ask_for_city(message, func):
    global user, server, params
    user = UserChoice()
    server = Server()
    params = Params()
    user.sorted_func = func
    bot.send_message(message.chat.id, 'В каком городе будем искать?')
    bot.register_next_step_handler(message, send_city_list)


@bot.callback_query_handler(func=lambda call: "Предлагаю для поиска следующие варианты" in call.message.text)
def start_message(call):
    user.city_id = call.data
    if user.flag_advanced_question:
        pass  # TODO
    else:
        bot.edit_message_text(text=call.data, chat_id=call.message.chat.id, message_id=call.message.id,
                              reply_markup=None)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
        ask_for_hotels_value(call.message)


@bot.callback_query_handler(func=lambda call: "Необходимость загрузки и вывода фотографий" in call.message.text)
def start_message(call):
    if user.flag_advanced_question:
        pass  # TODO
    else:
        bot.edit_message_text(text="Наличие фото - {}".format(call.data), chat_id=call.message.chat.id,
                              message_id=call.message.id, reply_markup=None)
        if call.data == "Да":
            user.needed_photo = True
            number_of_photo(call.message)
        else:
            result(call.message)


def send_city_list(message):
    # TODO проверка сообщения, если не город > предупредить и снова ask_for_city()
    keyboard = types.InlineKeyboardMarkup()
    for city_name, city_id in server.get_city(message).items():
        keyboard.add(types.InlineKeyboardButton(city_name, callback_data=city_id))

    bot.send_message(message.chat.id, text='Предлагаю для поиска следующие варианты'
                                           '\n(нажми на интересующий вариант):', reply_markup=keyboard)


def price_range(message):
    pass  # TODO
    bot.register_next_step_handler(message, distance_range)


def distance_range(message):
    pass  # TODO
    bot.register_next_step_handler(message, ask_for_hotels_value)


def ask_for_hotels_value(message):
    bot.send_message(message.chat.id, 'Количество отелей для вывода (не более 10):', message.text)
    bot.register_next_step_handler(message, photo_needed)


def photo_needed(message):
    # TODO проверка на количество отелей, если нет > number_of_options()
    user.number_of_options = int(message.text)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Да', callback_data='Да'))
    keyboard.add(types.InlineKeyboardButton('Нет!', callback_data='Нет'))
    bot.send_message(message.chat.id, text='Необходимость загрузки и вывода фотографий для каждого отеля (“Да/Нет”)',
                     reply_markup=keyboard)


def number_of_photo(message):
    bot.send_message(message.chat.id, 'Введите количество фото для отображения (не более 10):', message.text)
    bot.register_next_step_handler(message, result)


def result(message):
    if message.text.isdigit():
        user.number_of_photo = int(message.text)
    hotels_dict = server.get_hotels
    for data in hotels_dict.values():
        address = server.get_address(data)
        distance = server.get_distance(data)
        text = "\n{head}{name}{head}" \
               "\n{point}{address}" \
               "\n{point}Расстояние до достопримечательностей: {distance}" \
               "\n{point}Цена: {price}" \
               "\n[Отзывы]({url_1})" \
               "\n[Страница на hotels.com]({url_2))".format(name=data['name'], address=address, distance=distance,
                                              price=data['price'], head=head_emodji, point=point_emodji,
                                              url_1=3, url_2=4)
        if user.needed_photo:
            photo_list = server.get_photos(data['id'], text)
            bot.send_media_group(chat_id=message.chat.id, media=photo_list)
        else:
            bot.send_message(message.chat.id, text)


if __name__ == '__main__':
    bot.polling()
