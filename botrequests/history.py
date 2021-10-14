import arrow


history_data = dict()


def history(func):
    def wrapped(manager, user_id):
        func_name = manager.sorted_func.__name__
        time = arrow.utcnow().shift(hours=+3).format('YYYY-MM-DD HH:mm:ss')
        result, query_url = func(manager, user_id)
        my_list = list()
        for i_hotel, i_data in result.items():
            my_list.append("<a href='{url}'>{name}</a>".format(
                name=i_hotel, url='https://hotels.com/ho' + str(i_data['id'])))
        history_data[user_id] = dict()
        history_data[user_id]["<a href='{query_url}'>{func}</a> ({time})".format(
            func=func_name, query_url=query_url, time=time)] = my_list
        return result, query_url
    return wrapped
