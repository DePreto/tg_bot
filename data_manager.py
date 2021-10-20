"""
Модуль data_manager.py
Описывает взаимодействие с базой данных пользователей (формат JSON) и модулем botrequests.
"""
from typing import Union, List, Tuple, Dict, Any

from botrequests import main_request, lowprice, highprice, bestdeal, history
from telebot import types
from params import Params
import json
import os

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


def write_data(user_id: int, value: Union[int, str, List[Union[int, float]], Dict[str, Union[str, List[str]]], bool,
                                          None], key: str) -> None:
    """
    Запись данных пользователя в БД.
    :param user_id: user id
    :param key: ключ
    :param value: значение
    """
    i_data = read_data(user_id)
    with open(os.path.join('database', str(user_id)+'.json'), 'w') as file:
        i_data[key] = value
        json.dump(i_data, file, indent=4)


def read_data(user_id: int) -> Dict[str, Union[int, str, None, List[Union[int, float]], Dict[str,
                                                                                             Union[str, List[str]]]]]:
    """
    Чтение данных пользователя из БД.
    :param user_id: user id
    :return: данные пользователя
    """
    try:
        with open(os.path.join('database', str(user_id)+'.json'), 'r') as file:
            i_data = json.load(file)
    except FileNotFoundError:
        i_data = data
        with open(os.path.join('database', str(user_id)+'.json'), 'w') as file:
            json.dump(i_data, file, indent=4)
    return i_data


def reset_data(user_id: int) -> None:
    """
    Сброс данных пользователя (json файла).
    :param user_id: user_id
    """
    with open(os.path.join('database', str(user_id)+'.json'), 'w') as file:
        json.dump(data, file, indent=4)


def flag_advanced_question(chat_id: int) -> Union[bool, None]:
    """
    Геттер для получения значения флага на доп. вопросы пользователя.
    :param chat_id: chat id
    :return: значение флага на доп.вопросы пользователя
    """
    return read_data(user_id=chat_id)['flag_advanced_question']


def set_message_list(chat_id: int, i_key: str, i_value: List[str]) -> None:
    """
    Сеттер для установления списка отправленных ботом сообщений, содержащих информацию об истории поиска.
    :param chat_id: chat_id
    :param i_key: id головного сообщения (call) (содержащего кнопки выбора)
    :param i_value: список сообщений, содержащих информацию об истории поиска в рамках одного запроса
    """
    message_list = read_data(user_id=chat_id)['del_message_list']
    message_list[i_key] = i_value
    write_data(user_id=chat_id, value=message_list, key='del_message_list')


def get_message_list(chat_id: int, message_id: int) -> List[str]:
    """
    Геттер для получения списка отправленных ботом сообщений, содержащий информацию о истории поиска.
    :param chat_id: chat id
    :param message_id: id головного сообщения (call) (содержащего кнопки выбора)
    :return: список сообщений, содержащих информацию об истории поиска в рамках одного запроса
    """
    message_data = read_data(user_id=chat_id)['del_message_list']
    message_list = message_data.pop(str(message_id))
    write_data(user_id=chat_id, value=message_data, key='del_message_list')
    return message_list


def get_city_list(message: types.Message) -> Dict[str, str]:
    """
    Выполнение HTTP-запроса, обработка данных, содержащих варианты локаций (городов).
    :param message: message
    :return: словарь локаций (городов)
    """
    city_dict = main_request.location_search(message)
    write_data(user_id=message.chat.id, value=city_dict, key='city_list')
    return city_dict


def get_hotels(user_id: int) -> Tuple[Union[Dict[str, Dict[str, Union[str, None]]], None], Union[str, None]]:
    """
    Выполнение HTTP-запроса, обработка данных, содержащих варианты размещения (отелей).
    :param user_id: user id
    :return: словарь вариантов размещения (отелей)
    """
    i_data = read_data(user_id=user_id)
    sorted_func = sorted_functions[i_data['sorted_func']]
    hotels_data = main_request.hotels_search(data=i_data, sorted_func=sorted_func)
    if hotels_data[0]:
        key, value = history.history(hotels_data=hotels_data, user_data=i_data)
        i_history = read_data(user_id=user_id)['history']
        i_history[key] = value
        write_data(user_id=user_id, value=i_history, key='history')
        return hotels_data
    return None, None


def get_photos(user_id: int, hotel_id: int, text: str) -> List[types.InputMediaPhoto]:
    """
    Выполнение HTTP-запроса, обработка данных, содержащих фото вариантов размещения (отелей).
    :param user_id: user id
    :param hotel_id: hotel id
    :param text: информация об отеле
    :return: список фото варианта размещения (отеля)
    """
    i_data = read_data(user_id)
    photos = main_request.photos_search(i_data, hotel_id)
    result = list()
    for i_photo in photos:
        if not result:
            result.append(types.InputMediaPhoto(caption=text, media=i_photo['baseUrl'].replace('{size}', 'y'),
                                                parse_mode='HTML'))
        else:
            result.append(types.InputMediaPhoto(media=i_photo['baseUrl'].replace('{size}', 'y')))
    return result


def check_params(chat_id: int, text: str) -> None:
    """
    Установка языка и вылюты в соответствии с языком отправленного сообщения,
    в случае, если они не установлены пользователем по умолчанию.
    :param chat_id: chat id
    :param text: сообщение пользователя
    """
    i_data = read_data(user_id=chat_id)
    lang, cur = Params.check_lang(i_data, text), Params.check_cur(i_data, text)
    if lang:
        write_data(user_id=chat_id, value=lang, key='lang')
    if cur:
        write_data(user_id=chat_id, value=cur, key='cur')


def get_lang(chat_id: int) -> str:
    """
    Геттер для получения языка пользователя.
    :param chat_id: chat id
    :return: язык пользователя
    """
    return read_data(user_id=chat_id)['lang']


def set_lang(chat_id: int, lang: str) -> None:
    print(type(chat_id))
    """
    Сеттер для установления языка пользователя.
    :param chat_id: chat id
    :param lang: язык пользователя
    """
    write_data(user_id=chat_id, value=lang, key='lang'), write_data(user_id=chat_id, value=True, key='lang_flag')


def get_cur(chat_id: int) -> Union[bool, None]:
    """
    Геттер для получения валюты пользователя.
    :param chat_id: chat id
    :return: валюта пользователя
    """
    return read_data(user_id=chat_id)['cur']


def set_cur(chat_id: int, cur: str) -> None:
    """
    Сеттер для установления валюты пользователя.
    :param chat_id: chat id
    :param cur: валюта пользователя
    """
    write_data(user_id=chat_id, value=cur, key='cur'), write_data(user_id=chat_id, value=True, key='cur_flag')


def get_needed_photo(chat_id: int) -> Union[bool, None]:
    """
    Геттер для получения значения флага необходимости вывода фото.
    :param chat_id: chat id
    :return: значение флага необходимости вывода фото
    """
    return read_data(user_id=chat_id)['needed_photo']


def set_needed_photo(chat_id: int, value: Union[bool, None]) -> None:
    """
    Сеттер для установления значения флага необходимости вывота фото.
    :param chat_id: chat id
    :param value: значение флага необходимости выода фото
    """
    write_data(user_id=chat_id, value=value, key='needed_photo')


def set_sorted_func(chat_id: int, func: str) -> None:
    """
    Сеттер для установления сортирующей функции (функции выполнения HTTP-запроса (поиска вариантов размещения (отелей)).
    :param chat_id: chat id
    :param func: сортирующая функция (функция выполнения HTTP-запроса)
    """
    if func == 'bestdeal':
        write_data(user_id=chat_id, value=True, key='flag_advanced_question')
    else:
        write_data(user_id=chat_id, value=None, key='flag_advanced_question')
    write_data(user_id=chat_id, value=func, key='sorted_func')


def get_history(user_id: int) -> Dict[str, List[str]]:
    """
    Геттер для получения истории поиска пользователя.
    :param user_id: user_id
    :return: словарь истории поиска
    """
    return read_data(user_id)['history']


def clear_history(user_id: int) -> None:
    """
    Очистка истории поиска пользователя.
    :param user_id: user id
    """
    write_data(user_id, value=dict(), key='history')


def get_address(i_data: Dict[str, Any]) -> str:
    """
    Геттер для получения обработанного адреса варианта размещения (отеля).
    :param i_data: данные варианта размещения (отеля)
    :return: адрес варианта размещения (отеля)
    """
    return ', '.join(list(filter(lambda x: isinstance(x, str) and len(x) > 2, list(i_data['address'].values()))))


def get_landmarks(i_data: Dict[str, Any]) -> str:
    """
    Геттер для получения обработанных ориентиров варианта размещения (отеля).
    :param i_data: данные варианта размещения (отеля)
    :return: ориентиры варианта размещения (отеля)
    """
    return ', '.join(['\n*{label}: {distance}'.format(label=info['label'], distance=info['distance'])
                      for info in i_data['landmarks']])


def get_price_range(chat_id: int) -> List[int]:
    """
    Геттер для получения ценового диапазона пользователя.
    :param chat_id: chat id
    :return: ценовой диапазон пользователя
    """
    return read_data(user_id=chat_id)['price_range']


def set_price_range(chat_id: int, value: List[int]) -> None:
    """
    Сеттер для получения ценового диапазона пользователя.
    :param chat_id: chat id
    :param value: ценовой диапазон пользователя
    """
    write_data(user_id=chat_id, value=value, key='price_range')


def get_dist_range(chat_id: int) -> List[float]:
    """
    Геттер для получения диапазона расстояния пользователя.
    :param chat_id: chat id
    :return: ценовой диапазон пользователя
    """
    return read_data(user_id=chat_id)['dist_range']


def set_dist_range(chat_id: int, value: List[float]) -> None:
    """
    Сеттер для установления диапазона расстояния пользователя.
    :param chat_id: chat id
    :param value: диапазон расстояния пользователя
    """
    write_data(user_id=chat_id, value=value, key='dist_range')


def get_photos_value(chat_id: int) -> Union[int, None]:
    """
    Геттер для получения кол-ва фото для каждого варианта размещения (отеля).
    :param chat_id: chat_id
    :return: кол-во фото для каждого варианта размещения (отеля)
    """
    return read_data(user_id=chat_id)['photos_value']


def set_photos_value(chat_id: int, value: int) -> None:
    """
    Сеттер для установления кол-ва фото для каждого варианта размещения (отеля).
    :param chat_id: chat id
    :param value: кол-во фото для каждого варианта размещения (отеля)
    """
    if value > 10:
        raise ValueError('Value Error')
    else:
        write_data(user_id=chat_id, value=value, key='photos_value')


def get_hotels_value(chat_id: int) -> Union[int, None]:
    """
    Геттер для получения кол-ва запрашиваемых вариантов размещения (отелей) пользователя.
    :param chat_id: chat id
    :return: кол-во запрашиваемых вариантов размещения (отелей) пользователя
    """
    return read_data(user_id=chat_id)['hotels_value']


def set_hotels_value(chat_id: int, value: int) -> None:
    """
    Сеттер для установления кол-ва запрашиваемых вариантов размещения (отелей) пользователя.
    :param chat_id: chat id
    :param value: кол-во запрашиваемых вариантов размещения (отелей) пользователя
    """
    if value > 10:
        raise ValueError('Value Error')
    else:
        write_data(user_id=chat_id, value=value, key='hotels_value')


def get_city_id(chat_id: int) -> str:
    """
    Геттер для получения id искомого города пользователя.
    :param chat_id: chat id
    :return: id искомого города
    """
    return read_data(user_id=chat_id)['city_id']


def set_city(chat_id: int, value: str) -> None:
    """
    Сеттер для установления id и имени искомого города пользователем.
    :param chat_id: chat id
    :param value: id искомого города
    """
    write_data(user_id=chat_id, value=value, key='city_id')
    city_list = read_data(user_id=chat_id)['city_list']
    for city_name, city_data in city_list.items():
        if city_data == value:
            write_data(user_id=chat_id, value=city_name, key='city_name')
