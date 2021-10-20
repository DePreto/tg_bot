import arrow
from typing import Tuple, Dict, Union, List


def history(hotels_data: Union[Tuple[Union[Dict[str, Dict[str, Union[str, None]]], None], Union[str, None]]],
            user_data: Dict[str, Union[int, str, None, List[Union[int, float]], Dict[str, Union[str,
                                                                                                List[str]]]]]) -> Tuple:
    """
    Логирование результатов поиска вариантов размещения (отелей).
    :param hotels_data: кортеж, содержаший словарь со сведениями вариантов размещения (отелей) и url-ссылку
    :param user_data:
    :return:
    """
    time = arrow.utcnow().shift(hours=+3).format('YYYY-MM-DD HH:mm:ss')
    result, query_url = hotels_data
    my_list = list()
    for i_hotel, i_data in result.items():
        my_list.append("<a href='{url}'>{name}</a>".format(
            name=i_hotel, url='https://hotels.com/ho' + str(i_data['id'])))
    key = "<a href='{query_url}'>{func} {city_name}</a>\n({time})".format(
        func=user_data['sorted_func'], query_url=query_url, city_name=user_data['city_name'], time=time)
    value = my_list
    return key, value
