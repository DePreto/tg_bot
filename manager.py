from botrequests import main_request, lowprice, highprice, bestdeal, history
from telebot import types
from params import Params
import json

sorted_functions = {
    'lowprice': lowprice.lowprice,
    'highprice': highprice.highprice,
    'bestdeal': bestdeal.bestdeal,
}

data = {
    'city_list': None,
    'city_id': None,
    'city_name': None,
    'hotels_value': None,
    'needed_photo': None,
    'photos_value': None,
    'price_range': None,
    'dist_range': None,
    'history': dict(),
    'lang': 'ru_RU',
    'lang_flag': False,
    'cur': None,
    'cur_flag': False,
    'flag_advanced_question': None,
    'sorted_func': None,
    'del_message_list': dict()
}


def write_data(user_id, value, key):
    i_data = read_data(user_id)
    with open('database\\' + str(user_id) + '.json', 'w') as file:
        i_data[key] = value
        json.dump(i_data, file, indent=4)


def read_data(user_id):
    try:
        with open('database\\' + str(user_id) + '.json', 'r') as file:
            i_data = json.load(file)
    except FileNotFoundError:
        i_data = data
        with open('database\\' + str(user_id) + '.json', 'w') as file:
            json.dump(i_data, file, indent=4)
    return i_data


def flag_advanced_question(chat_id):
    return read_data(user_id=chat_id)['flag_advanced_question']


def set_message_list(chat_id, i_key, i_value):
    message_list = read_data(user_id=chat_id)['del_message_list']
    message_list[i_key] = i_value
    write_data(user_id=chat_id, value=message_list, key='del_message_list')


def get_message_list(chat_id, message_id):
    message_data = read_data(user_id=chat_id)['del_message_list']
    message_list = message_data.pop(message_id)
    write_data(user_id=chat_id, value=message_data, key='del_message_list')
    return message_list


def get_city_list(message):
    city_list = main_request.Request.location_search(message)
    write_data(message.chat.id, value=city_list, key='city_list')
    return city_list


def get_hotels(user_id):
    i_data = read_data(user_id)
    sorted_func = sorted_functions[i_data['sorted_func']]
    hotels_data = main_request.Request.hotels_search(i_data, sorted_func)
    key, value = history.history(hotels_data, i_data)
    i_history = read_data(user_id)['history']
    i_history[key] = value
    write_data(user_id, value=i_history, key='history')
    return hotels_data


def get_photos(user_id, hotel_id, text):
    i_data = read_data(user_id)
    photos = main_request.Request.photos_search(i_data, hotel_id)
    result = list()
    for i_photo in photos:
        if not result:
            result.append(types.InputMediaPhoto(caption=text, media=i_photo['baseUrl'].replace('{size}', 'w'),
                                                parse_mode='HTML'))
        else:
            result.append(types.InputMediaPhoto(media=i_photo['baseUrl'].replace('{size}', 'w')))
    return result


def check_params(chat_id, text):
    # устанавливаем язык и валюту по умолчанию, если он не был установлен пользователем
    i_data = read_data(user_id=chat_id)
    lang, cur = Params.check_lang(i_data, text), Params.check_cur(i_data, text)
    if lang:
        write_data(user_id=chat_id, value=lang, key='lang')
    if cur:
        write_data(user_id=chat_id, value=cur, key='cur')


def get_lang(chat_id):
    return read_data(user_id=chat_id)['lang']


def set_lang(chat_id, lang):
    write_data(user_id=chat_id, value=lang, key='lang'), write_data(user_id=chat_id, value=True, key='lang_flag')


def get_cur(chat_id):
    return read_data(user_id=chat_id)['cur']


def set_cur(chat_id, cur):
    write_data(user_id=chat_id, value=cur, key='cur'), write_data(user_id=chat_id, value=True, key='cur_flag')


def get_needed_photo(chat_id):
    return read_data(user_id=chat_id)['photo_needed']


def set_needed_photo(chat_id, value):
    write_data(user_id=chat_id, value=value, key='photo_needed')


def set_sorted_func(chat_id, func):
    if func == 'bestdeal':
        write_data(user_id=chat_id, value=True, key='flag_advanced_question')
    else:
        write_data(user_id=chat_id, value=None, key='flag_advanced_question')
    write_data(user_id=chat_id, value=func, key='sorted_func')


def get_history(user_id):
    return read_data(user_id)['history']


def clear_history(user_id):
    write_data(user_id, value=dict(), key='history')


def get_address(i_data):
    return ', '.join(list(filter(lambda x: isinstance(x, str) and len(x) > 2, list(i_data['address'].values()))))


def get_landmarks(i_data):
    return ', '.join(['\n*{label}: {distance}'.format(label=info['label'], distance=info['distance'])
                      for info in i_data['landmarks']])


def get_price_range(chat_id):
    return read_data(user_id=chat_id)['price_range']


def set_price_range(chat_id, value):
    write_data(user_id=chat_id, value=value, key='price_range')


def get_dist_range(chat_id):
    return read_data(user_id=chat_id)['dist_range']


def set_dist_range(chat_id, value):
    write_data(user_id=chat_id, value=value, key='dist_range')


def get_photos_value(chat_id):
    return read_data(user_id=chat_id)['photos_value']


def set_photos_value(chat_id, value):
    if value > 10:
        raise ValueError
    else:
        write_data(user_id=chat_id, value=value, key='photos_value')


def get_city_id(chat_id):
    return read_data(user_id=chat_id)['city_id']


def set_city_id(chat_id, value):
    write_data(user_id=chat_id, value=value, key='city_id')
    city_list = read_data(user_id=chat_id)['city_list']
    for city_name, city_data in city_list.items():
        if city_data == value:
            write_data(user_id=chat_id, value=city_name, key='city_name')


def get_hotels_value(chat_id):
    return read_data(user_id=chat_id)['hotels_value']


def set_hotels_value(chat_id, value):
    if value > 10:
        raise ValueError
    else:
        write_data(user_id=chat_id, value=value, key='hotels_value')

# def registration(cls):  # проверка на зарегистрированного пользователя (чтобы не обнулять настройки и историю поиска)
#     @functools.wraps(cls)
#     def wrapper(user_id, chat_id):
#         if user_id in cls.users:
#             return cls.users[user_id]
#         return cls(user_id, chat_id)
#     return wrapper


# def write_data_decorator(func):
#     def wrapped(*args, **kwargs):
#         key = func.__name__
#         value, user_id = func(*args, **kwargs)
#         with open('database\\' + user_id + '.json', 'w') as file:
#             try:
#                 i_data = json.load(file)
#             except io.UnsupportedOperation:
#                 i_data = data
#
#             i_data[key] = value
#             json.dump(i_data, file)
#
#     return wrapped
#
#
# def read_data_decorator(func):
#     def wrapped(*args, **kwargs):
#         key = func.__name__
#         value, user_id = func(*args, **kwargs)
#         with open('database\\' + user_id + '.json', 'r') as file:
#             i_data = json.load(file)
#             print(i_data)
#         return i_data[key]
#
#     return wrapped
