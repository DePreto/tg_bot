import re
import telebot
from decouple import config
from telebot import types
from manager import Manager, User
from dictionary import dictionary, emoji
import traceback
from time import time, ctime, sleep

bot = telebot.TeleBot(config('TOKEN'))
manager = Manager()


@bot.message_handler(regexp=r'.*[Пп]ривет.*')
@bot.message_handler(commands=['start', 'hello_world', 'help'])
def start_message(message):
    bot.send_message(chat_id=message.chat.id, text=dictionary['started_message'][manager.lang].format(
        emoji['low'], emoji['high'], emoji['best'], emoji['history'], emoji['settings']))


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal', 'history'])
def initial(message):
    manager.user = User(user_id=message.from_user.id, chat_id=message.chat.id)
    manager.set_sorted_func(func=re.search(r'\w+', message.text).group())
    bot.send_message(chat_id=message.chat.id, text=dictionary['ask_for_city'][manager.lang])
    bot.register_next_step_handler(message=message, callback=search_city)


@bot.message_handler(commands='settings')
def set_settings(message):
    lang_keyboard = types.InlineKeyboardMarkup(row_width=2)
    cur_keyboard = types.InlineKeyboardMarkup(row_width=3)
    lang_buttons = [types.InlineKeyboardButton(text=text, callback_data=data)
                    for text, data in (('RU', 'ru_RU'), ('EN', 'en_US'))]
    cur_buttons = [types.InlineKeyboardButton(text=text, callback_data=text)
                   for text in ('RUB', 'USD', 'EUR')]
    lang_keyboard.add(*lang_buttons)
    cur_keyboard.add(*cur_buttons)
    bot.send_message(chat_id=message.chat.id, text=dictionary['set_lang'][manager.lang], reply_markup=lang_keyboard)
    bot.send_message(chat_id=message.chat.id, text=dictionary['set_cur'][manager.lang], reply_markup=cur_keyboard)


@bot.callback_query_handler(func=lambda call: any(key in call.message.text for key in dictionary['set_lang'].values()))
def set_lang(call):
    manager.set_lang(call.data)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)


@bot.callback_query_handler(func=lambda call: any(key in call.message.text for key in dictionary['set_cur'].values()))
def set_cur(call):
    manager.set_cur(call.data)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)


def search_city(message):
    manager.check_params(message)
    temp = bot.send_message(chat_id=message.chat.id, text=dictionary['searching'][manager.lang], parse_mode='HTML')
    city_list = manager.get_city_list(message)
    keyboard = types.InlineKeyboardMarkup()
    if not city_list:
        bot.edit_message_text(chat_id=message.chat.id, message_id=temp.id, text=dictionary['error'][manager.lang],
                              parse_mode='HTML')
    else:
        for city_name, city_id in city_list.items():
            keyboard.add(types.InlineKeyboardButton(text=city_name, callback_data=city_id))
        bot.edit_message_text(chat_id=message.chat.id, message_id=temp.id,
                              text=dictionary['city_results'][manager.lang], reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: any(key in call.message.text
                                                  for key in dictionary['city_results'].values()))
def set_city_id(call):
    manager.city_id = call.data
    if manager.flag_advanced_question:
        pass  # TODO
    else:
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
        ask_for_hotels_value(call.message)


def ask_for_hotels_value(message):
    bot.send_message(chat_id=message.chat.id, text=dictionary['hotels_value'][manager.lang])
    bot.register_next_step_handler(message, photo_needed)


def photo_needed(message):
    try:
        manager.hotels_value = int(message.text)
    except ValueError:
        bot.send_message(chat_id=message.chat.id, text=dictionary['value_error'][manager.lang])
        bot.register_next_step_handler(message=message, callback=photo_needed)
    else:
        manager.hotels_value = int(message.text)
        keyboard = types.InlineKeyboardMarkup()
        [keyboard.add(types.InlineKeyboardButton(x, callback_data=x)) for x in [dictionary['pos'][manager.lang],
                                                                                dictionary['neg'][manager.lang]]]
        bot.send_message(message.chat.id, text=dictionary['photo_needed'][manager.lang],
                         reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: dictionary['photo_needed'][manager.lang] in call.message.text)
def set_photo_needed(call):
    if manager.flag_advanced_question:
        pass  # TODO реализация дополнительных запросов
    else:
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
        if any(call.data in answer for answer in dictionary['pos'].values()):
            manager.user.needed_photo = True
            number_of_photo(call.message)
        else:
            manager.user.needed_photo = False
            result(call.message)


def number_of_photo(message):
    bot.send_message(chat_id=message.chat.id, text=dictionary['photos_value'][manager.lang])
    bot.register_next_step_handler(message, result)


def result(message):
    try:
        if manager.user.needed_photo:
            manager.photos_value = int(message.text)
    except ValueError:
        bot.send_message(chat_id=message.chat.id, text=dictionary['value_error'][manager.lang])
        bot.register_next_step_handler(message=message, callback=result)
    else:
        temp = bot.send_message(chat_id=message.chat.id, text=dictionary['searching'][manager.lang])
        hotels_dict, search_link = manager.get_hotels()
        bot.edit_message_text(chat_id=message.chat.id, message_id=temp.id,
                              text=dictionary['ready_to_result'][manager.lang])
        if hotels_dict:
            for data in hotels_dict.values():
                text = dictionary['main_results'][manager.lang].format(
                    name=data['name'], address=manager.get_address(data), distance=manager.get_landmarks(data),
                    price=data['price'], e_hotel=emoji['hotel'], e_address=emoji['address'], e_dist=emoji['landmarks'],
                    e_price=emoji['price'], e_link=emoji['link'], link='https://hotels.com/ho' + str(data['id']),
                    address_link='https://www.google.ru/maps/place/'+data['coordinate'])
                if manager.user.needed_photo:
                    photo_list = manager.get_photos(data['id'], text)
                    bot.send_media_group(chat_id=message.chat.id, media=photo_list)
                else:
                    bot.send_message(message.chat.id, text, parse_mode='HTML')
            bot.send_message(chat_id=message.chat.id,
                             text=dictionary['additionally'][manager.lang].format(link=search_link),
                             parse_mode='MarkdownV2')


while True:
    try:
        bot.polling()
    except BaseException as exc:
        with open('errors_log.txt', 'a') as file:
            file.write('\n'.join([ctime(time()), exc.__class__.__name__, traceback.format_exc(), '\n\n']))
        re_message = bot.send_message(chat_id=manager.user.chat_id, text=dictionary['critical_error'][manager.lang])
        sleep(2)
        start_message(re_message)
