from abc import ABC
import re
from typing import Dict, Union, List


class Params(ABC):
    """
    Класс. Описывает установку и проверку параметров пользователя (язык, валюта).
    """
    @staticmethod
    def check_lang(data: Dict[str, Union[int, str, None, List[Union[int, float]], Dict[str, Union[str, List[str]]]]],
                   text: str) -> str:
        """Проверка флага на установленный пользователем язык"""
        if data['lang_flag'] is False:
            return Params.set_lang(text)

    @staticmethod
    def check_cur(data: Dict[str, Union[int, str, None, List[Union[int, float]], Dict[str, Union[str, List[str]]]]],
                  text: str) -> str:
        """Проверка флага на установленную пользователем валюту"""
        if data['cur_flag'] is False:
            return Params.set_cur(text)

    @staticmethod
    def set_lang(text: str) -> str:
        """Определение языка"""
        if bool(re.search(r'[А-Яа-я]', text)):
            return 'ru_RU'
        return 'en_US'

    @staticmethod
    def set_cur(text: str) -> str:
        """Определение валюты"""
        if bool(re.search(r'[А-Яа-я]', text)):
            return 'RUB'
        return 'USD'
