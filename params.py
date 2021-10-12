from abc import ABC
import re


class Params(ABC):
    @staticmethod
    def check_lang(manager, message):
        if manager.lang_flag is False:
            manager.lang = Params.set_lang(message.text)

    @staticmethod
    def check_cur(manager, message):
        if manager.cur_flag is False:
            manager.cur = Params.set_cur(message.text)

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
