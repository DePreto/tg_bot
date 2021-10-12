emoji = {'low': '\U00002198', 'high': '\U00002197', 'best': '\U00002705', 'history': '\U0001F4D3',
         'hotel': '\U0001F3E8', 'address': '\U0001F4CD', 'price': '\U0001F4B0', 'landmarks': '\U0001F3AF',
         'link': '\U0001F4CE', 'settings': '\U0001F527'}

dictionary = {
    'started_message': {
        'ru_RU': 'Помоги мне подобрать для тебя самое выгодное предложение (выбери команду): '
                 '\n\n {} /lowprice - Узнать топ самых дешёвых отелей в городе'
                 '\n\n {} /highprice - Узнать топ самых дорогих отелей в городе'
                 '\n\n {} /bestdeal - Узнать топ отелей, наиболее подходящих по цене '
                 'и расположению от центра (самые дешёвые и находятся ближе всего к центру)'
                 '\n\n {} /history - Узнать историю поиска отелей'
                 '\n\n {} /settings (по желанию) - Установить параметры поиска (язык, валюта)',
        'en_US': 'Help me find the best offer for you (choose a command): '
                 '\n\n {} /lowprice - Find out the top cheapest hotels in the city'
                 '\n\n {} /highprice - Find out the top most expensive hotels in the city'
                 '\n\n {} /bestdeal - Find out the top hotels most suitable for the price '
                 'and location from the center (the cheapest and are closest to the center)'
                 '\n\n {} /history - Find out the history of hotel search'
                 '\n\n {} /settings (optional) - Set search parameters (language, currency)'
    },
    'set_lang': {
        'ru_RU': 'Установить язык по умолчанию:',
        'en_US': 'Set the default language:'
    },
    'set_cur': {
        'ru_RU': 'Установить валюту по умолчанию:',
        'en_US': 'Set the default currency:',
    },
    'searching': {
        'ru_RU': 'Выполняю поиск...',
        'en_US': 'Searching...'
    },
    'ask_for_city': {
        'ru_RU': 'Какой город Вас интересует?',
        'en_US': 'Which city are you interested in?'
    },
    'hotels_value': {
        'ru_RU': 'Сколько объектов смотрим? (не более 10)',
        'en_US': 'How many hotels are we looking at? (no more than 10)'
    },
    'photo_needed': {
        'ru_RU': 'Интересуют фотографии объектов?',
        'en_US': 'Interested in photos of the object?'
    },
    'photos_value': {
        'ru_RU': 'Хорошо, сколько фотографий по каждому объекту?',
        'en_US': 'Well, how many photos for each object?'
    },
    'city_results': {
        'ru_RU': 'Предлагаю немного уточнить запрос:',
        'en_US': 'I propose to clarify the request:'
    },
    'pos': {
        'ru_RU': 'Да',
        'en_US': 'Yes'
    },
    'neg': {
        'ru_RU': 'Нет',
        'en_US': 'No'
    },
    'ready_to_result': {
        'ru_RU': 'Я нашёл для тебя следующие варианты...',
        'en_US': 'I found the following options for you...'
    },
    'main_results': {
        'ru_RU': "\n\n{e_hotel}{name}{e_hotel}"
                 "\n\n{e_address}<a href='{address_link}'>{address}</a>"
                 "\n\n{e_dist}Ориентиры: {distance}"
                 "\n\n{e_price}Цена: {price} за одну ночь"
                 "\n\n{e_link}<a href='{link}'>Подробнее на hotels.com</a>",
        'en_US': "\n\n{e_hotel}{name}{e_hotel}"
                 "\n\n{e_address}<a href='{address_link}'>{address}</a>"
                 "\n\n{e_dist}Landmarks: {distance}"
                 "\n\n{e_price}Price: {price} per night"
                 "\n\n{e_link}<a href='{link}'>More на hotels.com</a>"
    },
    'additionally': {
        'ru_RU': 'Не нашли подходящий вариант?\nЕщё больше отелей по вашему запросу\\: [смотреть]({link})'
                 '\nХотите продолжить работу с ботом? /help',
        'en_US': "Didn't find a suitable option?\nMore hotels on your request\\: [view]({link})"
                 "\nDo you want to continue working with the bot? /help"
    },
    'value_error': {
        'ru_RU': 'Необходимо ввести целое число (не более 10):',
        'en_US': 'You must enter an integer (no more than 10):'
        },
    'critical_error': {
        'ru_RU': 'Что-то пошло не так, перезагружаюсь...',
        'en_US': 'Something went wrong, restart...'
    },
    'range_error': {
        'ru_RU': 'Необходимо ввести два целых положительных отличных друг от друга числа:',
        'en_US': 'It is necessary to enter two positive integers that are different from each other:'
    },
    'ask_for_price_range': {
        'ru_RU': 'Уточните ценовой диапазон ({cur}):'
                 '\n(Например: "от 1000 до 2000", "1000-2000", "1000 2000")',
        'en_US': 'Specify the price range ({cur}):'
                 '\n(As example: "from 1000 to 2000", "1000-2000", "1000 2000")'
    },
    'ask_for_dist_range': {
        'ru_RU': 'Уточните диапазон расстояния, на котором находится отель от центра (км):'
                 '\n(Например: "от 1 до 3" / "1-3" / "1 3")',
        'en_US': 'Specify the range of the distance at which the hotel is located from the center (mile)'
                 '\n(As example: "from 1 to 3" / "1-3" / "1 3"'
    },
    'no_options': {
        'ru_RU': 'По вашему запросу ничего не найдено...\n/help',
        'en_US': 'Nothing was found for your query...\n/help'
    }
}
