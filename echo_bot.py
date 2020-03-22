import json
import telebot
from src.bank import PrivatbankBank, NationalBank, MonobankBank, FinanceBank

CONFIG = json.load(open('config.json'))
ALLOWED_BANKS = {
    PrivatbankBank.name: {'bank': PrivatbankBank, 'description': 'Api Privatbank'},
    NationalBank.name: {'bank': NationalBank, 'description': 'Api National bank'},
    MonobankBank.name: {'bank': MonobankBank, 'description': 'Api Monobank bank'},
    FinanceBank.name: {'bank': FinanceBank, 'description': 'Api Finance bank'},
}

bot = telebot.TeleBot(CONFIG['tel_bot_token'])


def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            if m.text == '/exit_force':
                exit()
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)


def __exchange_rate_by_bank(bank_name: str):
    bank = ALLOWED_BANKS.get(bank_name, None)
    if bank is None:
        return None
    exchange_rate = bank['bank'].get_exchange_rate()
    msg = f'Bank {bank_name}'
    if bank_name == FinanceBank.name:
        for address in exchange_rate:
            msg += f' address {address}\n'
            currencies = exchange_rate[address]
            for c_code in currencies:
                data = dict(currencies[c_code])
                msg += f"{c_code} - {round(float(data['buy']), 2)}/{round(float(data.get('sale', 0)), 2)} "
                msg += f"date: {data.get('date_expired', None)}\n"
    else:
        msg += f'\n'
        for c_code in exchange_rate:
            data = dict(exchange_rate[c_code])
            sale = data.get('sale') if data.get('sale') is not None else 0
            sale = round(float(sale), 2)
            msg += f"{c_code} - {round(float(data['buy']), 2)}/{sale} "
            msg += f"date: {data.get('date_expired', None)}\n"
    return msg


bot.set_update_listener(listener)


def is_bank_command(msg: str) -> bool:
    if msg.startswith('/'):
        return msg[1:] in ALLOWED_BANKS
    return False


@bot.message_handler(commands=['start'])
def start(message):
    command_help(message)
    return


@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "The following commands are available: \n"
    help_text += "/start \n"
    help_text += "/help \n"
    for key in ALLOWED_BANKS:
        help_text += f"/{key} - {ALLOWED_BANKS[key]['description']}\n"
    bot.send_message(cid, help_text)


@bot.message_handler(func=lambda m: is_bank_command(m.text))
def bank_command(message):
    cid = message.chat.id
    bot.send_chat_action(cid, 'typing')
    exchange_rate = __exchange_rate_by_bank(message.text[1:])
    if exchange_rate is None:
        bot.send_message(cid, 'Bad exchange_rate.')
        print('Bad exchange_rate.')
        return
    print('exchange_rate', exchange_rate)
    bot.send_message(cid, str(exchange_rate))


bot.polling()
