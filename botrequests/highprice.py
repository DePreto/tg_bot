import requests
import json
from typing import Tuple, Dict, Union


def highprice(user_city_id: str, lang: str, cur: str, hotels_value: int, hotel_url: str, headers: Dict[str, str],
              today: str) -> Union[Tuple[Union[Dict[str, Dict[str, Union[str, None]]], None], Union[str, None]]]:
    """
    HTTP-запрос к Hotels API (rapidapi.com) (запрос вариантов размещения (отелей)).
    :param user_city_id: id локации (города)
    :param lang: язык пользователя
    :param cur: валюта пользователя
    :param hotels_value: кол-во отелей
    :param hotel_url: url-ссылка на объект размещения (отель)
    :param headers: headers
    :param today: актуальная дата
    :return: кортеж, содержаший словарь со сведениями вариантов размещения (отелей) и url-ссылку
    """
    querystring = {"destinationId": user_city_id, "pageNumber": "1", "pageSize": str(hotels_value),
                   "checkIn": today, "checkOut": today, "adults1": "1",
                   "sortOrder": "PRICE_HIGHEST_FIRST", "locale": "{}".format(lang), "currency": cur}
    response = requests.request("GET", hotel_url, headers=headers, params=querystring, timeout=10)
    url = f'https://hotels.com/search.do?destination-id={user_city_id}&q-check-in={today}&q-check-out={today}' \
          f'&q-rooms=1&q-room-0-adults=2&q-room-0-children=0&sort-order={querystring["sortOrder"]}'
    data = json.loads(response.text)
    hotels_list = data['data']['body']['searchResults']['results']
    if not hotels_list:
        return None, None
    hotels_dict = {hotel['name']: {'id': hotel['id'], 'name': hotel['name'], 'address': hotel['address'],
                                   'landmarks': hotel['landmarks'], 'price': hotel['ratePlan']['price'].get('current')
                                   if hotel.get('ratePlan', None) else '-',
                                   'coordinate': '+'.join(map(str, hotel['coordinate'].values()))}
                   for hotel in hotels_list}
    return hotels_dict, url
