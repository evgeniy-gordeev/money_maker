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
    
def menu_logic(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    itembtn_str1 = types.KeyboardButton('Стратегия 1(int_0)')
    itembtn_str2 = types.KeyboardButton('Стратегия 2(market)')
    itembtn_buy_val1 = types.KeyboardButton('Купить value_1')
    itembtn_sell_val1 = types.KeyboardButton('Продать value_1')
    itembtn_balance = types.KeyboardButton('Баланс')
    itembtn_intervals = types.KeyboardButton('Интервалы')
    itembtn_orders = types.KeyboardButton('Текущие Ордера')
    itembtn_trades = types.KeyboardButton('Last Trades')
    itembtn_stop = types.KeyboardButton('STOP')
    itembtn_vkl = types.KeyboardButton('ВКЛ СЧЕТЧИК')
    itembtn_vikl = types.KeyboardButton('ВЫКЛ СЧЕТЧИК')
    markup.add(
        itembtn_str1, itembtn_str2, 
        itembtn_buy_val1, itembtn_sell_val1,
        itembtn_balance, itembtn_intervals, 
        itembtn_orders, itembtn_trades, 
        itembtn_vkl, itembtn_vikl,
        itembtn_stop,        
        )
    bot.send_message(message.chat.id, text = "Пожалуйста, выберите статегию.", reply_markup=markup)