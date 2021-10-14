import requests
import json


def highprice(user_city_id, lang, cur, hotels_value, hotel_url, headers, today, **kwargs):
    querystring = {"destinationId": user_city_id, "pageNumber": "1", "pageSize": str(hotels_value),
                   "checkIn": today, "checkOut": today, "adults1": "1",
                   "sortOrder": "PRICE_HIGHEST_FIRST", "locale": "{}".format(lang), "currency": cur}
    response = requests.request("GET", hotel_url, headers=headers, params=querystring)
    url = f'https://hotels.com/search.do?destination-id={user_city_id}&q-check-in={today}&q-check-out={today}' \
          f'&q-rooms=1&q-room-0-adults=2&q-room-0-children=0&sort-order={querystring["sortOrder"]}'
    data = json.loads(response.text)
    hotels_list = data['data']['body']['searchResults']['results']
    print(len(hotels_list))
    hotels_dict = {hotel['name']: {'id': hotel['id'], 'name': hotel['name'], 'address': hotel['address'],
                                   'landmarks': hotel['landmarks'], 'price': hotel['ratePlan']['price']['current'],
                                   'coordinate': '+'.join(map(str, hotel['coordinate'].values()))}
                   for hotel in hotels_list}
    return hotels_dict, url
