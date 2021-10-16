import re
import telebot
from decouple import config
from manager import *
from dictionary import dictionary, emoji
import traceback
from time import time, ctime

bot = telebot.TeleBot(config('TOKEN'))


@bot.message_handler(regexp=r'.*[Пп]ривет.*')
@bot.message_handler(commands=['start', 'hello_world', 'help'])
def start_message(message):
    bot.send_message(chat_id=message.chat.id, text=dictionary['started_message'][get_lang(
        message.chat.id)].format(emoji['low'], emoji['high'], emoji['best'], emoji['history'], emoji['settings']))


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def set_sorted_func(message):
    set_sorted_func(chat_id=message.chat.id, func=re.search(r'\w+', message.text).group())
    bot.send_message(chat_id=message.chat.id,
                     text=dictionary['ask_for_city'][get_lang(chat_id=message.chat.id)])
    bot.register_next_step_handler(message=message, callback=search_city)


@bot.message_handler(commands=['history'])
def get_history(message):
    i_history = get_history(message.chat.id)
    if i_history:
        message_list = list()
        for i_query, i_hotels in i_history.items():
            temp = bot.send_message(chat_id=message.chat.id, text='{func}\n\n{hotels}'.format(
                func=i_query, hotels='\n'.join(i_hotels)), parse_mode='HTML', disable_web_page_preview=True)
            message_list.append(str(temp.id))
        else:
            print(message_list)
            set_message_list(chat_id=message.chat.id, i_key=message_list[-1], i_value=message_list)
            keyword = types.InlineKeyboardMarkup(row_width=2)
            buttons = [types.InlineKeyboardButton(text=text, callback_data=text)
                       for text in dictionary['operations_for_history'][get_lang(chat_id=message.chat.id)]]
            keyword.add(*buttons)
            bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=int(message_list[-1]),
                                          reply_markup=keyword)

    else:
        bot.send_message(chat_id=message.chat.id,
                         text=dictionary['clear_history'][get_lang(chat_id=message.chat.id)])


@bot.callback_query_handler(func=lambda call: any(key in call.message.text for key in
                                                  ['lowprice', 'highprice', 'bestdeal']))
def operation_for_history(call):
    if call.data in [value[0] for value in dictionary['operations_for_history'].values()]:
        clear_history(call.message.chat.id)
    for i_message_id in get_message_list(chat_id=call.message.chat.id, message_id=str(call.message.id)):
        bot.delete_message(chat_id=call.message.chat.id, message_id=i_message_id)


@bot.message_handler(commands='settings')
def set_settings(message):
    lang_keyboard, cur_keyboard = types.InlineKeyboardMarkup(row_width=2), types.InlineKeyboardMarkup(row_width=3)
    lang_buttons = [types.InlineKeyboardButton(text=text, callback_data=i_data)
                    for text, i_data in (('RU', 'ru_RU'), ('EN', 'en_US'))]
    cur_buttons = [types.InlineKeyboardButton(text=text, callback_data=text)
                   for text in ('RUB', 'USD', 'EUR')]
    lang_keyboard.add(*lang_buttons), cur_keyboard.add(*cur_buttons)
    bot.send_message(chat_id=message.chat.id, text=dictionary['set_lang'][get_lang(chat_id=message.chat.id)],
                     reply_markup=lang_keyboard)
    bot.send_message(chat_id=message.chat.id, text=dictionary['set_cur'][get_lang(chat_id=message.chat.id)],
                     reply_markup=cur_keyboard)


@bot.callback_query_handler(func=lambda call: any(key in call.message.text for key in dictionary['set_lang'].values()))
def set_lang(call):
    set_lang(chat_id=call.message.chat.id, lang=call.data)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)


@bot.callback_query_handler(func=lambda call: any(key in call.message.text for key in dictionary['set_cur'].values()))
def set_cur(call):
    set_cur(chat_id=call.message.chat.id, cur=call.data)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)


def search_city(message):
    check_params(chat_id=message.chat.id, text=message.text)  # можно убрать отсюда (в функцию get_city_list)
    temp = bot.send_message(chat_id=message.chat.id,
                            text=dictionary['searching'][get_lang(chat_id=message.chat.id)], parse_mode='HTML')
    city_list = get_city_list(message)
    keyboard = types.InlineKeyboardMarkup()
    if not city_list:
        bot.edit_message_text(chat_id=message.chat.id, message_id=temp.id, text=dictionary['no_options'][
            get_lang(chat_id=message.chat.id)], parse_mode='HTML')
    else:
        for city_name, city_id in city_list.items():
            keyboard.add(types.InlineKeyboardButton(text=city_name, callback_data=city_id))
        bot.edit_message_text(chat_id=message.chat.id, message_id=temp.id, text=dictionary['city_results'][
            get_lang(chat_id=message.chat.id)], reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: any(key in call.message.text
                                                  for key in dictionary['city_results'].values()))
def set_city_id(call):
    set_city_id(call.message.chat.id, call.data)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    if flag_advanced_question(call.message.chat.id):
        ask_for_price_range(call.message)
    else:
        ask_for_hotels_value(call.message)


def ask_for_price_range(message):
    bot.send_message(chat_id=message.chat.id,
                     text=dictionary['ask_for_price_range'][get_lang(chat_id=message.chat.id)].format(
                         cur=get_cur(message.chat.id)))
    bot.register_next_step_handler(message, ask_for_dist_range)


def ask_for_dist_range(message):
    price_range = list(set(map(int, map(lambda string: string.replace(',', '.'),
                                        re.findall(r'\d+[.,\d+]?\d?', message.text)))))
    if len(price_range) != 2:
        bot.send_message(chat_id=message.chat.id,
                         text=dictionary['range_error'][get_lang(chat_id=message.chat.id)])
        bot.register_next_step_handler(message, ask_for_dist_range)
    else:
        set_price_range(chat_id=message.chat.id, value=price_range)
        bot.send_message(chat_id=message.chat.id,
                         text=dictionary['ask_for_dist_range'][get_lang(chat_id=message.chat.id)])
        bot.register_next_step_handler(message, ask_for_hotels_value)


def ask_for_hotels_value(message):
    if flag_advanced_question(message.chat.id):
        dist_range = list(set(map(float, map(lambda string: string.replace(',', '.'),
                                             re.findall(r'\d+[.,\d+]?\d?', message.text)))))
        if len(dist_range) != 2:
            bot.send_message(chat_id=message.chat.id,
                             text=dictionary['range_error'][get_lang(chat_id=message.chat.id)])
            return bot.register_next_step_handler(message, ask_for_hotels_value)
        else:
            set_dist_range(chat_id=message.chat.id, value=dist_range)

    bot.send_message(chat_id=message.chat.id,
                     text=dictionary['hotels_value'][get_lang(chat_id=message.chat.id)])
    bot.register_next_step_handler(message, photo_needed)


def photo_needed(message):
    try:
        set_hotels_value(chat_id=message.chat.id, value=abs(int(message.text)))
    except ValueError:
        bot.send_message(chat_id=message.chat.id,
                         text=dictionary['value_error'][get_lang(chat_id=message.chat.id)])
        bot.register_next_step_handler(message=message, callback=photo_needed)
    else:
        keyboard = types.InlineKeyboardMarkup()
        [keyboard.add(types.InlineKeyboardButton(x, callback_data=x)) for x in
         [dictionary['pos'][get_lang(chat_id=message.chat.id)],
          dictionary['neg'][get_lang(chat_id=message.chat.id)]]]
        bot.send_message(message.chat.id, text=dictionary['photo_needed'][get_lang(chat_id=message.chat.id)],
                         reply_markup=keyboard)


@bot.callback_query_handler(
    func=lambda call: dictionary['photo_needed'][get_lang(chat_id=call.message.chat.id)] in call.message.text)
def set_photo_needed(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    if any(call.data in answer for answer in dictionary['pos'].values()):
        set_needed_photo(chat_id=call.message.chat.id, value=True)
        number_of_photo(call.message)
    else:
        set_needed_photo(chat_id=call.message.chat.id, value=False)
        result(call.message)


def number_of_photo(message):
    bot.send_message(chat_id=message.chat.id,
                     text=dictionary['photos_value'][get_lang(chat_id=message.chat.id)])
    bot.register_next_step_handler(message, result)


def result(message):
    try:
        if get_needed_photo(chat_id=message.chat.id):
            set_photos_value(chat_id=message.chat.id, value=abs(int(message.text)))
    except ValueError:
        bot.send_message(chat_id=message.chat.id,
                         text=dictionary['value_error'][get_lang(chat_id=message.chat.id)])
        bot.register_next_step_handler(message=message, callback=result)
    else:
        temp = bot.send_message(chat_id=message.chat.id,
                                text=dictionary['searching'][get_lang(chat_id=message.chat.id)])

        hotels_dict, search_link = get_hotels(user_id=message.chat.id)
        if hotels_dict:
            bot.edit_message_text(chat_id=message.chat.id, message_id=temp.id,
                                  text=dictionary['ready_to_result'][get_lang(chat_id=message.chat.id)])
            for index, i_data in enumerate(hotels_dict.values()):
                if index + 1 > get_hotels_value(chat_id=message.chat.id):
                    break
                text = dictionary['main_results'][get_lang(chat_id=message.chat.id)].format(
                    name=i_data['name'], address=get_address(i_data), distance=get_landmarks(i_data),
                    price=i_data['price'], e_hotel=emoji['hotel'], e_address=emoji['address'],
                    e_dist=emoji['landmarks'], e_price=emoji['price'], e_link=emoji['link'],
                    link='https://hotels.com/ho' + str(i_data['id']),
                    address_link='https://www.google.ru/maps/place/' + i_data['coordinate'])
                if get_needed_photo(chat_id=message.chat.id):
                    photo_list = get_photos(user_id=message.chat.id, hotel_id=i_data['id'], text=text)
                    bot.send_media_group(chat_id=message.chat.id, media=photo_list)
                else:
                    bot.send_message(message.chat.id, text, parse_mode='HTML', disable_web_page_preview=True)
            bot.send_message(chat_id=message.chat.id,
                             text=dictionary['additionally'][get_lang(chat_id=message.chat.id)].format(
                                 link=search_link), parse_mode='MarkdownV2', disable_web_page_preview=True)
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=temp.id,
                                  text=dictionary['no_options'][get_lang(chat_id=message.chat.id)])


while True:
    try:
        bot.polling()
    except Exception as exc:
        with open('errors_log.txt', 'a') as file:
            file.write('\n'.join([ctime(time()), exc.__class__.__name__, traceback.format_exc(), '\n\n']))
