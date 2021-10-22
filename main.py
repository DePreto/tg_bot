import re
import telebot
from decouple import config
from data_manager import *
from dictionary import dictionary, emoji
import traceback
from time import time, ctime, sleep
from typing import Callable
import functools

bot = telebot.TeleBot(config('TOKEN'))


def exc_handler(method: Callable) -> Callable:
    """ Декоратор. Логирует исключение вызванной функции, уведомляет пользователя об ошибке. """
    @functools.wraps(method)
    def wrapped(message: Union[types.Message, types.CallbackQuery]) -> None:
        try:
            method(message)
        except ValueError as exception:
            if isinstance(message, types.CallbackQuery):
                message = message.message
            if exception.__class__.__name__ == 'JSONDecodeError':
                reset_data(message.chat.id)
                exc_handler(method(message))
            else:
                if str(exception) == 'Range Error':
                    bot.send_message(chat_id=message.chat.id,
                                     text=dictionary['rng_err'][get_lang(chat_id=message.chat.id)])
                else:
                    bot.send_message(chat_id=message.chat.id,
                                     text=dictionary['val_err'][get_lang(chat_id=message.chat.id)])
                bot.register_next_step_handler(message=message, callback=exc_handler(method))
        except Exception as exception:
            bot.send_message(chat_id=message.chat.id, text=dictionary['crt_err'][get_lang(chat_id=message.chat.id)])
            with open('errors_log.txt', 'a') as file:
                file.write('\n'.join([ctime(time()), exception.__class__.__name__, traceback.format_exc(), '\n\n']))
            sleep(1)
            start_message(message)

    return wrapped


@bot.message_handler(regexp=r'.*[Пп]ривет.*')
@bot.message_handler(commands=['start', 'hello_world', 'help'])
@exc_handler
def start_message(message: types.Message) -> None:
    """Стартовое сообщение"""
    bot.send_message(chat_id=message.chat.id, text=dictionary['started_message'][get_lang(
        message.chat.id)].format(emoji['low'], emoji['high'], emoji['best'], emoji['history'], emoji['settings']))


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
@exc_handler
def set_func(message: types.Message) -> None:
    """Установка сортирующей функции, определение следующего шага обработчика"""
    set_sorted_func(chat_id=message.chat.id, func=re.search(r'\w+', message.text).group())
    bot.send_message(chat_id=message.chat.id, text=dictionary['ask_for_city'][get_lang(chat_id=message.chat.id)])
    bot.register_next_step_handler(message=message, callback=search_city)


@bot.message_handler(commands=['history'])
@exc_handler
def history(message: types.Message) -> None:
    """Вывод истории поиска"""
    i_history = get_history(message.chat.id)
    if i_history:
        message_list = list()
        for i_query, i_hotels in i_history.items():
            temp = bot.send_message(chat_id=message.chat.id, text='{func}\n\n{hotels}'.format(
                func=i_query, hotels='\n'.join(i_hotels)), parse_mode='HTML', disable_web_page_preview=True)
            message_list.append(str(temp.id))
        else:
            set_message_list(chat_id=message.chat.id, i_key=message_list[-1], i_value=message_list)
            keyword = types.InlineKeyboardMarkup(row_width=2)
            buttons = [types.InlineKeyboardButton(text=text, callback_data=text)
                       for text in dictionary['operations_for_history'][get_lang(chat_id=message.chat.id)]]
            keyword.add(*buttons)
            bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=int(message_list[-1]),
                                          reply_markup=keyword)

    else:
        bot.send_message(chat_id=message.chat.id, text=dictionary['clr_history'][get_lang(chat_id=message.chat.id)])


@bot.callback_query_handler(func=lambda call: any(key in call.message.text for key in
                                                  ['lowprice', 'highprice', 'bestdeal']))
@exc_handler
def operation_for_history(call: types.CallbackQuery) -> None:
    """Обработка сообщений истории поиска (скрыть, очистить)"""
    if call.data in [value[0] for value in dictionary['operations_for_history'].values()]:
        clear_history(call.message.chat.id)
    for i_message_id in get_message_list(chat_id=call.message.chat.id, message_id=call.message.id):
        bot.delete_message(chat_id=call.message.chat.id, message_id=int(i_message_id))


@bot.message_handler(commands='settings')
@exc_handler
def set_settings(message: types.Message) -> None:
    """Вывод Inline клавиатуры с параметрами настроек"""
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


@bot.callback_query_handler(func=lambda call: any(key in call.message.text
                                                  for key in dictionary['set_lang'].values()))
@exc_handler
def change_lang(call: types.CallbackQuery) -> None:
    """Установка языка пользователем"""
    set_lang(chat_id=call.message.chat.id, lang=call.data)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)


@bot.callback_query_handler(func=lambda call: any(key in call.message.text
                                                  for key in dictionary['set_cur'].values()))
@exc_handler
def change_cur(call: types.CallbackQuery) -> None:
    """Установка валюты пользователем"""
    set_cur(chat_id=call.message.chat.id, cur=call.data)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)


@exc_handler
def search_city(message: types.Message) -> None:
    """Проверка параметров настроек, обработка запроса пользователя по поиску города,
    вывод Inline клавиатуры с результатами"""
    check_params(chat_id=message.chat.id, text=message.text)
    temp = bot.send_message(chat_id=message.chat.id,
                            text=dictionary['search'][get_lang(chat_id=message.chat.id)], parse_mode='HTML')
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
@exc_handler
def city_handler(call: types.CallbackQuery) -> None:
    """Обработка данных искомого города (id, name), определение следующего шага обработчика"""
    set_city(call.message.chat.id, call.data)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    if flag_advanced_question(call.message.chat.id):
        ask_for_price_range(call.message)
    else:
        ask_for_hotels_value(call.message)


@exc_handler
def ask_for_price_range(message: types.Message) -> None:
    """Запрос ценового диапазона у пользователя, определение следующего шага обработчика"""
    bot.send_message(chat_id=message.chat.id, text=dictionary['ask_price'][get_lang(
        chat_id=message.chat.id)].format(cur=get_cur(message.chat.id)))
    bot.register_next_step_handler(message, ask_for_dist_range)


@exc_handler
def ask_for_dist_range(message: types.Message) -> None:
    """Обработка значений ценового диапазона пользователя, запрос диапазона дистанции,
    определение следующего шага обработчика"""
    price_range = list(set(map(int, map(lambda string: string.replace(',', '.'),
                                        re.findall(r'\d+[.,\d+]?\d?', message.text)))))
    if len(price_range) != 2:
        raise ValueError('Range Error')
    else:
        set_price_range(chat_id=message.chat.id, value=price_range)
        bot.send_message(chat_id=message.chat.id, text=dictionary['ask_dist'][get_lang(chat_id=message.chat.id)])
        bot.register_next_step_handler(message, ask_for_hotels_value)


@exc_handler
def ask_for_hotels_value(message: types.Message) -> None:
    """Обработка значений диапазона дистанции пользователя, запрос количества отелей,
    определение следующего шага обработчика"""
    if flag_advanced_question(message.chat.id):
        dist_range = list(set(map(float, map(lambda string: string.replace(',', '.'),
                                             re.findall(r'\d+[.,\d+]?\d?', message.text)))))
        if len(dist_range) != 2:
            raise ValueError('Range Error')
        else:
            set_dist_range(chat_id=message.chat.id, value=dist_range)

    bot.send_message(chat_id=message.chat.id, text=dictionary['hotels_value'][get_lang(chat_id=message.chat.id)])
    bot.register_next_step_handler(message, photo_needed)


@exc_handler
def photo_needed(message: types.Message) -> None:
    """Обработка значения кол-ва отелей пользователя, запрос необходимости вывода фото в виде Inline клавитуары"""
    set_hotels_value(chat_id=message.chat.id, value=abs(int(message.text)))
    keyboard = types.InlineKeyboardMarkup()
    [keyboard.add(types.InlineKeyboardButton(x, callback_data=x)) for x in
     [dictionary['pos'][get_lang(chat_id=message.chat.id)], dictionary['neg'][get_lang(chat_id=message.chat.id)]]]
    bot.send_message(message.chat.id, text=dictionary['photo_needed'][get_lang(chat_id=message.chat.id)],
                     reply_markup=keyboard)


@bot.callback_query_handler(
    func=lambda call: dictionary['photo_needed'][get_lang(chat_id=call.message.chat.id)] in call.message.text)
@exc_handler
def set_photo_needed(call: types.CallbackQuery) -> None:
    """Обработка ответа пользователя о необходимости вывода фото, определение хода действий."""
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    if any(call.data in answer for answer in dictionary['pos'].values()):
        set_needed_photo(chat_id=call.message.chat.id, value=True)
        number_of_photo(call.message)
    else:
        set_needed_photo(chat_id=call.message.chat.id, value=False)
        result(call.message)


@exc_handler
def number_of_photo(message: types.Message) -> None:
    """Запрос кол-ва фото у пользователя, определение следующего шага обработчика"""
    bot.send_message(chat_id=message.chat.id,
                     text=dictionary['photos_value'][get_lang(chat_id=message.chat.id)])
    bot.register_next_step_handler(message, result)


@exc_handler
def result(message: types.Message) -> None:
    """Обработка значения кол-ва фото, выполнение поиска вариантов, представление результатов"""
    if get_needed_photo(chat_id=message.chat.id):
        set_photos_value(chat_id=message.chat.id, value=abs(int(message.text)))
    temp = bot.send_message(chat_id=message.chat.id, text=dictionary['search'][get_lang(chat_id=message.chat.id)])
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
                photo_list = get_photos(user_id=message.chat.id, hotel_id=int(i_data['id']), text=text)
                for i_size in ['z', 'y', 'd', 'n', '_']:
                    try:
                        bot.send_media_group(chat_id=message.chat.id, media=photo_list)
                        break
                    except telebot.apihelper.ApiTelegramException:
                        photo_list = [types.InputMediaPhoto(caption=obj.caption, media=obj.media[:-5] + f'{i_size}.jpg',
                                                            parse_mode=obj.parse_mode) for obj in photo_list]
            else:
                bot.send_message(message.chat.id, text, parse_mode='HTML', disable_web_page_preview=True)

        bot.send_message(chat_id=message.chat.id, text=dictionary['additionally'][get_lang(
            chat_id=message.chat.id)].format(
            link=search_link), parse_mode='MarkdownV2', disable_web_page_preview=True)
    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=temp.id,
                              text=dictionary['no_options'][get_lang(chat_id=message.chat.id)])


bot.polling()
