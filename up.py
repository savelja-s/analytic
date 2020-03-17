from src.bank import PrivatbankBank, IBankApi, NationalBank, MonobankBank, FinanceBank
from src.weather import get_weather


class Analytic:

    @classmethod
    def __get_bank(cls, bank_name: str):
        if bank_name == PrivatbankBank.name:
            return PrivatbankBank()
        if bank_name == NationalBank.name:
            return NationalBank()
        if bank_name == MonobankBank.name:
            return MonobankBank()
        if bank_name == FinanceBank.name:
            return FinanceBank()
        else:
            raise Exception('We do not work with such a bank. Until;=)')

    @classmethod
    def __exchange_rate(cls, bank_name: str):
        bank = cls.__get_bank(bank_name)
        if not isinstance(bank, IBankApi):
            raise TypeError('Incorrect bank.')
        print(f'On {bank.name}: {bank.get_exchange_rate()}.')

    @classmethod
    def run(cls):
        print(get_weather('Lviv'))
        # cls.__exchange_rate(FinanceBank.name)
        # cls.__exchange_rate(PrivatbankBank.name)
        # cls.__exchange_rate(NationalBank.name)
        # cls.__exchange_rate(MonobankBank.name)
        print('Good by')


if __name__ == "__main__":
    Analytic.run()
