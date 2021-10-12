from decouple import config
from abc import ABC
import requests
import json
from params import Params
import arrow


class Request(ABC):
    city_url = 'https://hotels4.p.rapidapi.com/locations/search'
    hotel_url = 'https://hotels4.p.rapidapi.com/properties/list'
    photo_url = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'

    headers = {
        'x-rapidapi-host': config("RAPIDHOST"),
        'x-rapidapi-key': config("RAPIDAPIKEY")
    }

    @classmethod
    def location_search(cls, message):
        querystring = {"query": message.text, "locale": "{}".format(Params.set_lang(message.text))}
        response = requests.request("GET", cls.city_url, headers=cls.headers, params=querystring)
        data = json.loads(response.text)
        city_list = {', '.join((city['name'], city['caption'][city['caption'].rindex(' ')+1:])): city['destinationId']
                     for city in data['suggestions'][0]['entities']}
        return city_list

    @classmethod
    def hotels_search(cls, manager):
        hotels_data = manager.sorted_func(user_city_id=manager.city_id, lang=manager.lang, cur=manager.cur,
                                          hotels_value=manager.hotels_value, hotel_url=cls.hotel_url,
                                          headers=cls.headers, price_range=manager.price_range,
                                          dist_range=manager.dist_range, today=arrow.utcnow().format("YYYY-MM-DD"))
        return hotels_data

    @classmethod
    def photos_search(cls, manager, hotel_id):
        querystring = {"id": "{}".format(hotel_id)}
        response = requests.request("GET", cls.photo_url, headers=cls.headers, params=querystring)
        data = json.loads(response.text)
        photos_address = data["hotelImages"][:manager.photos_value]
        return photos_address
