import time
from dataclasses import dataclass
from src.db import IDb
from src.helper import Helper
import abc

CURRENCIES = ['USD', 'EUR']


class IBankApi(abc.ABC):
    interval: int = 10

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    @abc.abstractmethod
    def _get_bank_api(self) -> dict:
        pass

    def get_exchange_rate(self) -> dict:
        data = Helper.get_bank_store(self.name, self.interval)
        if len(data) == 0:
            data = self._get_bank_api()
            Helper.set_bank_store(self.name, self.interval, data)
        return data


@dataclass
class ExchangeRate(IDb):
    bank: str
    currency_code: str
    buy: float
    sale: float = None
    date_expired: str = None
    date_create: float = None

    def __post_init__(self):
        self.date_expired = time.strftime('%Y-%m-%d_%H:%M:%S') if self.date_expired is None else self.date_expired
        self.date_create = time.time() if self.date_create is None else self.date_create

    @staticmethod
    def tb_name() -> str:
        return 'exchange_rate'


@dataclass
class UnitBankFinance(IDb):
    hash: str
    type: str
    oldId: int
    title: str
    region: str
    city: str
    phone: str
    address: str
    date_expired: str
    date_create: float = None

    def __post_init__(self):
        self.date_expired = time.strftime('%Y-%m-%d_%H:%M:%S') if self.date_expired is None else self.date_expired
        self.date_create = time.time() if self.date_create is None else self.date_create

    @staticmethod
    def tb_name() -> str:
        return 'unit_bank_finance'


class PrivatbankBank(IBankApi):
    name = 'privatbank'
    api_url = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'
    interval = 5

    def __init__(self):
        super().__init__(self.name)

    def _get_bank_api(self) -> dict:
        data = {currency['ccy']: {'buy': currency['buy'], 'sale': currency['sale']} for currency in
                Helper.http_request(self.api_url) if
                currency['ccy'] in CURRENCIES}
        print('_get_bank_api', data)
        for currency in data:
            exchange_rate = ExchangeRate(str(self), currency, data[currency]['buy'], data[currency]['sale'])
            Helper.db().insert(exchange_rate)
        return data


class NationalBank(IBankApi):
    name = 'national'
    api_url = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode={}&json'

    def __init__(self):
        super().__init__(self.name)

    def _get_bank_api(self) -> dict:
        data = {}
        for code in CURRENCIES:
            response = Helper.http_request(self.api_url.format(code))[0]
            data[code] = {'buy': response['rate'], 'sale': None, 'date_expired': response['exchangedate']}
        print('_get_bank_api', data)
        for currency in data:
            exchange_rate = ExchangeRate(str(self),
                                         currency,
                                         data[currency]['buy'],
                                         data[currency]['sale'],
                                         data[currency]['date_expired']
                                         )
            Helper.db().insert(exchange_rate)
        return data


class MonobankBank(IBankApi):
    name = 'monobank'
    api_url = 'https://api.monobank.ua/bank/currency'
    interval = 3
    code_currencies = {840: {'code': 'USD'}, 978: {'code': 'EUR'}}
    code_UKR = 980

    def __init__(self):
        super().__init__(self.name)

    def _get_bank_api(self) -> dict:
        data = {}
        response = Helper.http_request(self.api_url)
        for currency in response:
            if currency['currencyCodeA'] in self.code_currencies.keys() and currency['currencyCodeB'] == self.code_UKR:
                code = self.code_currencies[currency['currencyCodeA']]['code']
                data[code] = {'buy': currency['rateBuy'],
                              'sale': currency['rateSell'],
                              'date_expired': time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(currency['date']))
                              }
        print('_get_bank_api', data)
        for currency in data:
            exchange_rate = ExchangeRate(str(self),
                                         currency,
                                         data[currency]['buy'],
                                         data[currency]['sale'],
                                         data[currency]['date_expired']
                                         )
            Helper.db().insert(exchange_rate)
        return data


class FinanceBank(IBankApi):
    name = 'finance'
    api_url = 'http://resources.finance.ua/ua/public/currency-cash.json'
    interval = 2

    def __init__(self):
        super().__init__(self.name)

    def _get_bank_api(self) -> dict:
        response = Helper.http_request(self.api_url)
        data = {}
        bank = {}
        unit_bank_fs = {}
        for bank_unit in response['organizations']:
            for currency in bank_unit['currencies']:
                if currency in CURRENCIES:
                    exchange_rate = ExchangeRate(f"<{self}> {bank_unit['title']}",
                                                 currency,
                                                 bank_unit['currencies'][currency]['bid'],
                                                 bank_unit['currencies'][currency]['ask'],
                                                 response['date']
                                                 )
                    Helper.db().insert(exchange_rate)
                    bank[currency] = {'buy': exchange_rate.buy,
                                      'sale': exchange_rate.sale,
                                      'date_expired': exchange_rate.date_expired
                                      }
            data[str(bank_unit['title'])] = bank
            unit_bank_f = UnitBankFinance(bank_unit['id'],
                                          response['orgTypes'][str(bank_unit['orgType'])],
                                          bank_unit['oldId'],
                                          bank_unit['title'],
                                          response['regions'][bank_unit['regionId']],
                                          response['cities'][bank_unit['cityId']],
                                          bank_unit['phone'],
                                          bank_unit['address'],
                                          response['date']
                                          )
            if Helper.db().find_by(UnitBankFinance.tb_name(), unit_bank_f.hash, 'hash') is None:
                Helper.db().insert(unit_bank_f)
            unit_bank_fs[unit_bank_f.__dict__['hash']] = unit_bank_f.__dict__
        Helper.write_addition_file('banks_and_kantors', unit_bank_fs)
        return data
