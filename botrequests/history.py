import arrow


def history(hotels_data, data):
    time = arrow.utcnow().shift(hours=+3).format('YYYY-MM-DD HH:mm')
    result, query_url = hotels_data
    my_list = list()
    for i_hotel, i_data in result.items():
        my_list.append("<a href='{url}'>{name}</a>".format(
            name=i_hotel, url='https://hotels.com/ho' + str(i_data['id'])))
    key = "<a href='{query_url}'>{func} {city_name}</a>\n({time})".format(
        func=data['sorted_func'], query_url=query_url, city_name=data['city_name'], time=time)
    value = my_list
    return key, value
