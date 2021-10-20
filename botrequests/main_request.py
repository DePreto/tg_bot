"""
Модуль main_request.py
Описывает взаимодействие с Hotels API (rapidapi.com).
"""

from decouple import config
from telebot import types
from typing import Callable, Dict, List, Tuple, Union, Any
import requests
import json
from params import Params
import arrow
import re

city_url = 'https://hotels4.p.rapidapi.com/locations/search'
hotel_url = 'https://hotels4.p.rapidapi.com/properties/list'
photo_url = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'

headers = {
    'x-rapidapi-host': config("RAPIDHOST"),
    'x-rapidapi-key': config("RAPIDAPIKEY")
}


def location_search(message: types.Message) -> Dict[str, str]:
    """
    Выполнение HTTP-запроса к Hotels API (rapidapi.com) (Поиск локаций (городов)).
    :param message: сообщение пользователя
    :return: словарь, содержащий сведения локаций (городов)
    """

    querystring = {"query": message.text, "locale": "{}".format(Params.set_lang(message.text))}
    response = requests.request("GET", city_url, headers=headers, params=querystring, timeout=10)
    data = json.loads(response.text)

    city_dict = {', '.join((city['name'], re.findall('(\\w+)[\n<]', city['caption']+'\n')[-1])): city['destinationId']
                 for city in data['suggestions'][0]['entities']}
    return city_dict


def hotels_search(data: Dict[str, Union[int, str, None, List[Union[int, float]], Dict[str, Union[str, List[str]]]]],
                  sorted_func: Callable) -> \
        Union[Tuple[Union[Dict[str, Dict[str, Union[str, None]]], None], Union[str, None]]]:
    """
    Выполнение HTTP-запроса к Hotels API (rapidapi.com) (поиск вариантов размещения (отелей)).
    :param data: данные пользователя
    :param sorted_func: функция, выполняющая http-запрос
    :return: кортеж, содержаший словарь со сведениями вариантов размещения (отелей) и url-ссылку
    """
    if data['sorted_func'] == 'bestdeal':
        hotels_data = sorted_func(user_city_id=data['city_id'], lang=data['lang'], cur=data['cur'],
                                  hotels_value=data['hotels_value'], hotel_url=hotel_url,
                                  headers=headers, price_range=data['price_range'],
                                  dist_range=data['dist_range'], today=arrow.utcnow().format("YYYY-MM-DD"))
    else:
        hotels_data = sorted_func(user_city_id=data['city_id'], lang=data['lang'], cur=data['cur'],
                                  hotels_value=data['hotels_value'], hotel_url=hotel_url,
                                  headers=headers, today=arrow.utcnow().format("YYYY-MM-DD"))
    return hotels_data


def photos_search(data: Dict[str, Union[int, str, None, List[Union[int, float]], Dict[str, Union[str, List[str]]]]],
                  hotel_id: int) -> List[Dict[str, Union[str, Any]]]:
    """
    Выполнение HTTP-запроса к Hotels API (rapidapi.com) (поиск фото).
    :param data: данные пользователя
    :param hotel_id: hotel id
    :return: список url-адресов фото варианта размещения (отеля)
    """

    querystring = {"id": "{}".format(hotel_id)}
    response = requests.request("GET", photo_url, headers=headers, params=querystring, timeout=10)
    photo_data = json.loads(response.text)
    photos_address = photo_data["hotelImages"][:data['photos_value']]
    return photos_address
