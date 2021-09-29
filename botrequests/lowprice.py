import requests
import json
from main import Server


def lowprice(user_city_id, lang, cur, number_of_options):
    querystring = {"destinationId": user_city_id, "pageNumber": "1", "pageSize": str(number_of_options), "checkIn": "2021-09-16",
                   "checkOut": "2021-09-17", "adults1": "1", "sortOrder": "PRICE", "locale": "{}_{}".format(lang, lang.upper()), "currency": cur}
    response = requests.request("GET", Server.hotel_url, headers=Server.headers, params=querystring)
    data = json.loads(response.text)
    hotels_list = data['data']['body']['searchResults']['results']
    hotels_dict = {hotel['name']: {'id': hotel['id'], 'name': hotel['name'], 'address': hotel['address'],
                                   'landmarks': hotel['landmarks'], 'price': hotel['ratePlan']['price']['current']}
                   for hotel in hotels_list}
    return hotels_dict
