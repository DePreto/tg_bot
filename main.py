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


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def initial(message):
    manager.user = User(user_id=message.from_user.id, chat_id=message.chat.id)
    manager.set_sorted_func(func=re.search(r'\w+', message.text).group())
    bot.send_message(chat_id=message.chat.id, text=dictionary['ask_for_city'][manager.lang])
    bot.register_next_step_handler(message=message, callback=search_city)


@bot.message_handler(commands=['history'])
def get_history(message):
    history = manager.get_history(message.chat.id)
    if history:
        message_list = list()
        for i_query, i_hotels in history.items():
            temp = bot.send_message(chat_id=message.chat.id, text='{func}\n\n{hotels}'.format(
                func=i_query, hotels='\n'.join(i_hotels)
            ), parse_mode='HTML', disable_web_page_preview=True)
            message_list.append(temp)
        else:
            manager.message_list = message_list
            keyword = types.InlineKeyboardMarkup(row_width=2)
            buttons = [types.InlineKeyboardButton(text=text, callback_data=text)
                       for text in dictionary['operations_for_history'][manager.lang]]
            keyword.add(*buttons)
            bot.edit_message_reply_markup(chat_id=message_list[-1].chat.id, message_id=message_list[-1].id,
                                          reply_markup=keyword)

    else:
        bot.send_message(chat_id=message.chat.id, text='Ваша история пуста!')


@bot.callback_query_handler(func=lambda call: any(key in call.message.text for key in
                                                  ['lowprice', 'highprice', 'bestdeal']))
def operation_for_history(call):
    if call.data in [value[0] for value in dictionary['operations_for_history'].values()]:
        manager.clear_history(call.message.chat.id)
    for i_message in manager.message_list:
        bot.delete_message(chat_id=i_message.chat.id, message_id=i_message.id)


@bot.message_handler(commands='settings')
def set_settings(message):
    lang_keyboard, cur_keyboard = types.InlineKeyboardMarkup(row_width=2), types.InlineKeyboardMarkup(row_width=3)
    lang_buttons = [types.InlineKeyboardButton(text=text, callback_data=data)
                    for text, data in (('RU', 'ru_RU'), ('EN', 'en_US'))]
    cur_buttons = [types.InlineKeyboardButton(text=text, callback_data=text)
                   for text in ('RUB', 'USD', 'EUR')]
    lang_keyboard.add(*lang_buttons), cur_keyboard.add(*cur_buttons)
    bot.send_message(chat_id=message.chat.id, text=dictionary['set_lang'][manager.lang], reply_markup=lang_keyboard)
    bot.send_message(chat_id=message.chat.id, text=dictionary['set_cur'][manager.lang], reply_markup=cur_keyboard)


@bot.callback_query_handler(func=lambda call: any(key in call.message.text for key in dictionary['set_lang'].values()))
def set_lang(call):
    manager.set_lang(lang=call.data)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)


@bot.callback_query_handler(func=lambda call: any(key in call.message.text for key in dictionary['set_cur'].values()))
def set_cur(call):
    manager.set_cur(cur=call.data)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)


def search_city(message):
    manager.check_params(message)
    temp = bot.send_message(chat_id=message.chat.id, text=dictionary['searching'][manager.lang], parse_mode='HTML')
    city_list = manager.get_city_list(message)
    keyboard = types.InlineKeyboardMarkup()
    if not city_list:
        bot.edit_message_text(chat_id=message.chat.id, message_id=temp.id, text=dictionary['no_options'][manager.lang],
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
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    if manager.flag_advanced_question:
        ask_for_price_range(call.message)
    else:
        ask_for_hotels_value(call.message)


def ask_for_price_range(message):
    bot.send_message(chat_id=message.chat.id, text=dictionary['ask_for_price_range'][manager.lang].format(
        cur=manager.cur))
    bot.register_next_step_handler(message, ask_for_dist_range)


def ask_for_dist_range(message):
    price_range = set(map(int,
                          map(lambda string: string.replace(',', '.'), re.findall(r'\d+[.,\d+]?\d?', message.text))))
    if len(price_range) != 2:
        bot.send_message(chat_id=message.chat.id, text=dictionary['range_error'][manager.lang])
        bot.register_next_step_handler(message, ask_for_dist_range)
    else:
        manager.price_range = price_range
        bot.send_message(chat_id=message.chat.id, text=dictionary['ask_for_dist_range'][manager.lang])
        bot.register_next_step_handler(message, ask_for_hotels_value)


def ask_for_hotels_value(message):
    if manager.flag_advanced_question:
        dist_range = set(map(float,
                             map(lambda string: string.replace(',', '.'), re.findall(r'\d+[.,\d+]?\d?', message.text))))
        if len(dist_range) != 2:
            bot.send_message(chat_id=message.chat.id, text=dictionary['range_error'][manager.lang])
            return bot.register_next_step_handler(message, ask_for_hotels_value)
        else:
            manager.dist_range = dist_range

    bot.send_message(chat_id=message.chat.id, text=dictionary['hotels_value'][manager.lang])
    bot.register_next_step_handler(message, photo_needed)


def photo_needed(message):
    try:
        manager.hotels_value = abs(int(message.text))
    except ValueError:
        bot.send_message(chat_id=message.chat.id, text=dictionary['value_error'][manager.lang])
        bot.register_next_step_handler(message=message, callback=photo_needed)
    else:
        keyboard = types.InlineKeyboardMarkup()
        [keyboard.add(types.InlineKeyboardButton(x, callback_data=x)) for x in [dictionary['pos'][manager.lang],
                                                                                dictionary['neg'][manager.lang]]]
        bot.send_message(message.chat.id, text=dictionary['photo_needed'][manager.lang],
                         reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: dictionary['photo_needed'][manager.lang] in call.message.text)
def set_photo_needed(call):
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
            manager.photos_value = abs(int(message.text))
    except ValueError:
        bot.send_message(chat_id=message.chat.id, text=dictionary['value_error'][manager.lang])
        bot.register_next_step_handler(message=message, callback=result)
    else:
        temp = bot.send_message(chat_id=message.chat.id, text=dictionary['searching'][manager.lang])

        hotels_dict, search_link = manager.get_hotels(user_id=message.chat.id)
        if hotels_dict:
            bot.edit_message_text(chat_id=message.chat.id, message_id=temp.id,
                                  text=dictionary['ready_to_result'][manager.lang])
            for index, data in enumerate(hotels_dict.values()):
                if index + 1 > manager.hotels_value:
                    break
                text = dictionary['main_results'][manager.lang].format(
                    name=data['name'], address=manager.get_address(data), distance=manager.get_landmarks(data),
                    price=data['price'], e_hotel=emoji['hotel'], e_address=emoji['address'],
                    e_dist=emoji['landmarks'], e_price=emoji['price'], e_link=emoji['link'],
                    link='https://hotels.com/ho' + str(data['id']),
                    address_link='https://www.google.ru/maps/place/' + data['coordinate'])
                if manager.user.needed_photo:
                    photo_list = manager.get_photos(data['id'], text)
                    bot.send_media_group(chat_id=message.chat.id, media=photo_list)
                else:
                    bot.send_message(message.chat.id, text, parse_mode='HTML', disable_web_page_preview=True)
            bot.send_message(chat_id=message.chat.id, text=dictionary['additionally'][manager.lang].format(
                    link=search_link), parse_mode='MarkdownV2', disable_web_page_preview=True)
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=temp.id,
                                  text=dictionary['no_options'][manager.lang])


while True:
    try:
        bot.polling()
    except Exception as exc:
        with open('errors_log.txt', 'a') as file:
            file.write('\n'.join([ctime(time()), exc.__class__.__name__, traceback.format_exc(), '\n\n']))
        re_message = bot.send_message(chat_id=manager.user.chat_id, text=dictionary['critical_error'][manager.lang])
        sleep(2)
        start_message(re_message)
