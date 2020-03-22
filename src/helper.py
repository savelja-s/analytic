import json
import logging
import os
import time
from json import JSONDecodeError
import requests
from src.db import Db


class Helper:
    logger: logging = None

    # def log(func, *args, **kwargs):
    #     logger = logging.getLogger(func.__module__)
    #
    #     def decorator(self, *args, **kwargs):
    #         logger.debug('Entering: %s', func.__name__)
    #         result = func(*args, **kwargs)
    #         logger.debug(result)
    #         logger.debug('Exiting: %s', func.__name__)
    #         return result
    #
    #     return decorate(func, decorator)

    @staticmethod
    def log() -> logging.Logger:
        if Helper.logger is None:
            logging.basicConfig(filename='store/log/logfile.log',
                                filemode='a',
                                format='%(asctime)s %(name)s %(levelname)s %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S',
                                level=logging.DEBUG)
            logging.info("Running Logging!!!")
            Helper.logger = logging.getLogger('urbanGUI')
        return Helper.logger

    @classmethod
    def db(cls) -> Db:
        return Db()

    @staticmethod
    def get_addition_file_path(name: str) -> str:
        return f"{os.getcwd()}/store/bank/{name}.json"

    @staticmethod
    def get_bank_store_dir() -> str:
        bank_dir = f"{os.getcwd()}/store/bank/{time.strftime('%Y/%m/%d')}"
        if not os.path.exists(bank_dir):
            os.makedirs(bank_dir)
        return bank_dir

    @staticmethod
    def set_bank_store(bank_name: str, interval_prefix: int, data: dict):
        if not isinstance(data, dict) or not len(data):
            raise TypeError(f'Fun set_store get {data}')
        file_path = f'{Helper.get_bank_store_dir()}/{bank_name}_{int(time.localtime().tm_hour / interval_prefix)}.json'
        with open(file_path, 'w+') as file:
            json.dump(data, file)

    @staticmethod
    def save_bank_units(file_name: str, data):
        file_path = Helper.get_addition_file_path(file_name)
        if not os.path.exists(file_path):
            bank_units = data
        else:
            with open(file_path, 'r', encoding='utf-8') as file:
                bank_units = json.load(file)
                for hash_id in data:
                    if hash_id in bank_units.keys():
                        bank_units[hash_id] = bank_units[hash_id]

        with open(file_path, 'w+', encoding='utf-8') as file:
            json.dump(bank_units, file)

    @staticmethod
    def get_bank_store(bank_name: str, interval_prefix: int) -> dict:
        file_path = f"{Helper.get_bank_store_dir()}/{bank_name}_{int(time.localtime().tm_hour / interval_prefix)}.json"
        if os.path.exists(file_path):
            with open(file_path) as json_file:
                return json.load(json_file)
        else:
            return {}

    @staticmethod
    def http_request(url: str, method='get', data: dict = None):
        response_inst = None
        attempts = 5
        while attempts > 0:
            try:
                if method == 'get':
                    response_inst = requests.get(url=url, params=data)
                if method == 'post':
                    response_inst = requests.post(url=url, data=data)
                break
            except requests.exceptions.ConnectionError:
                print('BAD REQUEST')
                attempts -= 1
        if response_inst is None:
            raise ValueError(f'Undefined method: {method}')
        response_inst.encoding = 'UTF-8'
        try:
            response = response_inst.json()
        except JSONDecodeError:
            print('Not JSON')
            response = response_inst.content
        print('request url :', url, 'method:', method)
        Helper.log().debug({'response_api': {
            'url': url,
            'method': method,
            'status_code': response_inst.status_code,
            'headers': response_inst.headers,
            'content': response,
        }})
        return response
