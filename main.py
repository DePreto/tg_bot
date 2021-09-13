import telebot

bot = telebot.TeleBot(token='1980472787:AAFySb4u26INxgG4Ggnbulf0CvvBKvfZWjc')


@bot.message_handler(commands=['start', 'hello-world'])
def start_message(message):
    bot.send_message(message.chat.id, 'Добро пожаловать! Этот бот умеет...')


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.send_message(message.chat.id, message.text)


bot.polling()
