import requests
import json


def lowprice(user_city_id, lang, cur, hotels_value, hotel_url, headers, today, **kwargs):
    querystring = {"destinationId": user_city_id, "pageNumber": "1", "pageSize": str(hotels_value),
                   "checkIn": today, "checkOut": today, "adults1": "1", "sortOrder": "PRICE",
                   "locale": "{}".format(lang), "currency": cur}
    response = requests.request("GET", hotel_url, headers=headers, params=querystring)
    print(response.url)
    # url = 'https://ru.hotels.com/search.do?' + response.text
    url = f'https://ru.hotels.com/search.do?destination-id={user_city_id}&q-check-in={today}&q-check-out={today}' \
          f'&q-rooms=1&q-room-0-adults=2&q-room-0-children=0&sort-order={querystring["sortOrder"]}'
    data = json.loads(response.text)
    hotels_list = data['data']['body']['searchResults']['results']
    if not hotels_list:
        return None, None
    hotels_dict = {hotel['name']: {'id': hotel['id'], 'name': hotel['name'], 'address': hotel['address'],
                                   'landmarks': hotel['landmarks'], 'price': hotel['ratePlan']['price']['current'],
                                   'coordinate': '+'.join(map(str, hotel['coordinate'].values()))}
                   for hotel in hotels_list}
    return hotels_dict, url
