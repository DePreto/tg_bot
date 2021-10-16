from abc import ABC
import re


class Params(ABC):
    @staticmethod
    def check_lang(data, text):
        if data['lang_flag'] is False:
            return Params.set_lang(text)

    @staticmethod
    def check_cur(data, text):
        if data['cur_flag'] is False:
            return Params.set_cur(text)

    @staticmethod
    def set_lang(text):
        if bool(re.search(r'[А-Яа-я]', text)):
            return 'ru_RU'
        return 'en_US'

    @staticmethod
    def set_cur(text):
        if bool(re.search(r'[А-Яа-я]', text)):
            return 'RUB'
        return 'USD'
