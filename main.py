import requests
import re
import telebot

bot = telebot.TeleBot(token='1980472787:AAFySb4u26INxgG4Ggnbulf0CvvBKvfZWjc')


@bot.message_handler(regexp=r'.*[Пп]ривет.*')
@bot.message_handler(commands=['start', 'hello_world'])
def start_message(message):
    bot.send_message(message.chat.id, 'Добро пожаловать! Этот бот умеет...')


# @bot.message_handler(func=lambda m: True)  # реализация эхо-бота
# def echo_all(message):
#     bot.send_message(message.chat.id, message.text)


# @bot.message_handler(commands=['lowprice'])
# def search_for_lowprice(message):
#     bot.send_message(message.chat.id, func())


# @bot.message_handler(commands=['highprice'])
# def search_for_highprice(message):
#     bot.send_message(message.chat.id, 'Добро пожаловать! Этот бот умеет... Для какого города будем искать варианты?')


# @bot.message_handler(commands=['bestdeal'])
# def search_for_highprice(message):
#     bot.send_message(message.chat.id, 'Добро пожаловать! Этот бот умеет... Для какого города будем искать варианты?')
#
#
# @bot.message_handler(commands=['history'])
# def search_for_highprice(message):
#     bot.send_message(message.chat.id, 'Добро пожаловать! Этот бот умеет... Для какого города будем искать варианты?')


# def is_cyrillic(text):
#     return bool(re.search(r'[А-Яа-я]', text))


# user_city = input('В каком городе будем искать?')
# if is_cyrillic(user_city):
#     lang = 'ru'
# else:
#     lang = 'en'


# connect with hotels api
# url = "https://hotels4.p.rapidapi.com/locations/search"
# querystring = {"query":user_city,"locale":"{}_{}".format(lang, lang.upper())}
# headers = {
#     'x-rapidapi-host': "hotels4.p.rapidapi.com",
#     'x-rapidapi-key': "20a52d50b2msh71870d486f6cff2p181bf8jsn4c8e8894ae35"
#     }
# response = requests.request("GET", url, headers=headers, params=querystring)
# print(response.text)

if __name__ == '__main__':
    bot.polling()
