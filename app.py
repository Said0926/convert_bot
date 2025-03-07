import telebot
import requests
import json
from config import TOKEN, keys


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def help(message: telebot.types.Message):
    text = ('''Чтобы начать работу введите команду боту в следующем формате:
<валюта>  в  <валюта>  <количество переводимой волюты>  
    
Увидеть список всех доступных валют:  /values''')


    bot.reply_to(message, text)

@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные волюты:'
    for key in keys.keys():
        text = '\n'.join((text, key, ))
    bot.reply_to(message, text)


@bot.message_handler(content_types=['text'])
def convert(message: telebot.types.Message):
    try:
        values = message.text.split(' в ')


        if len(values) != 2:
            raise ValueError('Неверный формат. Используйте: <валюта> в <валюта> <количество>')

        quote_value = values[0].strip().lower()

        base_amount_value = values[1].strip().lower()
        base_amount = base_amount_value.split(' ')

        if len(base_amount) < 2:
            raise ValueError('Неверный формат. Используйте: <валюта> в <валюта> <количество>')

        base = ' '.join(base_amount[:-1]).strip().lower()

        amount = float(base_amount[-1])


        if quote_value not in keys:
            raise ValueError(f'Валюта {quote_value} не найдена. Проверьте список доступных валют: /values')
        if base not in keys:
            raise ValueError(f'Валюта {base} не найдена. Проверьте список доступных валют: /values')

        r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={keys[quote_value]}&tsyms={keys[base]}')
        data = json.loads(r.content)

        if keys[base] not in data:
            raise ValueError(f'Не удалось получить данные для {keys[base]}')

        total_base = data[keys[base]] * amount

        text = f'Цена {amount} {quote_value} в {base} - {total_base}'

        bot.send_message(message.chat.id, text)

    except ValueError as e:
        bot.reply_to(message, f'Ошибка: {e}')
    except KeyError:
        bot.reply_to(message, 'Неверная валюта. Проверьте список доступных валют: /values')
    except Exception as e:
        bot.reply_to(message, f'Произошла ошибка: {e}')


bot.polling(non_stop=True)
