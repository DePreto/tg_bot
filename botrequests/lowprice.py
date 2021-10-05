import requests
import json


def lowprice(user_city_id, lang, cur, hotels_value, hotel_url, headers):
    querystring = {"destinationId": user_city_id, "pageNumber": "1", "pageSize": str(hotels_value),
                   "checkIn": "2021-09-16", "checkOut": "2021-09-17", "adults1": "1", "sortOrder": "PRICE",
                   "locale": "{}".format(lang), "currency": cur}
    response = requests.request("GET", hotel_url, headers=headers, params=querystring)
    url = 'https://ru.hotels.com/search.do' + response.url.lstrip('https://hotels4.p.rapidapi.com/properties/list')
    data = json.loads(response.text)
    hotels_list = data['data']['body']['searchResults']['results']
    hotels_dict = {hotel['name']: {'id': hotel['id'], 'name': hotel['name'], 'address': hotel['address'],
                                   'landmarks': hotel['landmarks'], 'price': hotel['ratePlan']['price']['current'],
                                   'coordinate': '+'.join(map(str, hotel['coordinate'].values()))}
                   for hotel in hotels_list}
    return hotels_dict, url
