#imports
from pybit.unified_trading import HTTP
from pybit.exceptions import InvalidRequestError
import telebot
from telebot import types
import pandas as pd
from tabulate import tabulate
import datetime
import time
import yaml
from robot import Robot

# Конфиги
form = yaml.safe_load(open('form.yml', 'r'))

# Инициализация бота с токеном
session = HTTP(testnet=False, api_key=form['bybit']['api_key'], api_secret=form['bybit']['api_secret'])
bot = telebot.TeleBot(token=form['tg']['bot_token'])
r = Robot()

# Константы
sleep_time = form['time_period'] #счетчик
is_running = False


def document_logic(message):
    try:
        document_id = message.document.file_id
        document_path = bot.get_file(document_id).file_path
        document_name = message.document.file_name
        if document_name == 'form.yml':
            document_content = bot.download_file(document_path)
            document_content_decoded = document_content.decode('unicode_escape')
            if len(document_content_decoded) > 0:            
                yaml_data = yaml.safe_load(document_content_decoded)
                if isinstance(yaml_data, dict):
                    inputed_attribs_ = list(yaml_data.keys())
                    sorted_inputed_attribs_ = sorted(inputed_attribs_)
                    attribs_ = [
                        'time_period', 'symbol', 'isLeverage', 'min_value', 'int_profit',
                        'values', 'ints', 'int_triggers', 'bybit', 'tg']
                    sorted_attribs = sorted(attribs_)
                    if sorted_inputed_attribs_ == sorted_attribs:
                        with open('form.yml', 'w') as file:
                            yaml.dump(yaml_data, file)
                        bot.send_message(message.chat.id,   'Форма успешно загружена.\n'\
                                                            'Бот перезапущен с новыми параметрами.')
                        with open('restart.txt','w') as file:
                            file.write(f'форма изменена_{datetime.datetime.now()}')
                    else:
                        bot.send_message(message.chat.id,   'Ошибка.\n'\
                                                            'Неверный состав атрибутов.')                    
                else:
                    bot.send_message(message.chat.id,   'Ошибка.\n'\
                                                        'Отсутствуют атрибуты.') 

            else:
                bot.send_message(message.chat.id,   'Ошибка.\n'\
                                                    'Пустой документ.')
        else:
            bot.send_message(message.chat.id,   'Ошибка.\n'\
                                                'Некорректное название и расширение файла.\n'
                                                'Загрузите файл "form.yml"')
    except Exception:
            bot.send_message(message.chat.id,   'Ошибка.\n'\
                                                'Комментарии на русском после # в форме\n'
                                                'Уберите русский яз. и символ # из формы')