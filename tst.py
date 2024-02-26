#imports
from pybit.unified_trading import HTTP
from pybit.exceptions import InvalidRequestError
import telebot
from telebot import types
import pandas as pd
from tabulate import tabulate
import time
import yaml
from robot import Robot

# Конфиги
form = yaml.safe_load(open('form.yml', 'r'))
keys = yaml.safe_load(open('keys.yml', 'r'))

# Инициализация бота с токеном
session = HTTP(testnet=False, api_key=keys['bybit']['api_key'], api_secret=keys['bybit']['api_secret'])

print(session)