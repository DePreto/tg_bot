from decouple import config
from abc import ABC
import requests
import json
from params import Params
import arrow

city_url = 'https://hotels4.p.rapidapi.com/locations/search'
hotel_url = 'https://hotels4.p.rapidapi.com/properties/list'
photo_url = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'


class Request(ABC):

    headers = {
        'x-rapidapi-host': config("RAPIDHOST"),
        'x-rapidapi-key': config("RAPIDAPIKEY")
    }

    @classmethod
    def location_search(cls, message):
        querystring = {"query": message.text, "locale": "{}".format(Params.set_lang(message.text))}
        response = requests.request("GET", city_url, headers=cls.headers, params=querystring)
        data = json.loads(response.text)
        city_list = {', '.join((city['name'], city['caption'][city['caption'].rindex(' ') + 1:])): city['destinationId']
                     for city in data['suggestions'][0]['entities']}
        return city_list

    @classmethod
    def hotels_search(cls, data, sorted_func):
        hotels_data = sorted_func(user_city_id=data['city_id'], lang=data['lang'], cur=data['cur'],
                                  hotels_value=data['hotels_value'], hotel_url=hotel_url,
                                  headers=cls.headers, price_range=data['price_range'],
                                  dist_range=data['dist_range'], today=arrow.utcnow().format("YYYY-MM-DD"))
        return hotels_data

    @classmethod
    def photos_search(cls, data, hotel_id):
        querystring = {"id": "{}".format(hotel_id)}
        response = requests.request("GET", photo_url, headers=cls.headers, params=querystring)
        photo_data = json.loads(response.text)
        photos_address = photo_data["hotelImages"][:data['photos_value']]
        return photos_address
