import telebot
from telebot import types
from telebot import apihelper
import pandas as pd
from tabulate import tabulate
import pandas as pd
from pybit.unified_trading import HTTP
from pybit.exceptions import InvalidRequestError
from robot import Robot
import time

# Инициализация бота с токеном
session = HTTP(
    testnet=False,
    api_key="5wH56z5gvRFfoNKVd6",
    api_secret="N4n1P6PG3E9mwhwysF4fSQPpBR2ZACOkdmA9",
)
bot = telebot.TeleBot("6928882205:AAFHKZ8QNDUA4v_zw18Xo7VJvHH9VHMNKh0")

r = Robot()
is_running = False

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    itembtn_str1 = types.KeyboardButton('Стратегия 1')
    itembtn_str2 = types.KeyboardButton('Стратегия 2')
    itembtn_balance = types.KeyboardButton('Баланс')
    itembtn_trades = types.KeyboardButton('Last Trades')
    itembtn_stop = types.KeyboardButton('STOP')
    markup.add(itembtn_str1, itembtn_str2, itembtn_balance, itembtn_trades, itembtn_stop)

    response =  f"Приветствую Вас!\n" \
                f"Пожалуйста, выберите статегию." 
    bot.send_message(message.chat.id, response, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Стратегия 1")
def handle_strategy_1(message):
    global is_running
    is_running = True

    r.delete_all_orders()
    r.create_order_11()
    r.create_order_9()
    bot.send_message(message.chat.id, "Закрыл все ордера✅\n Закрыл все позиции✅\n Закупил резервы✅")

    lastOrderPrice = float(session.get_executions(category='spot', symbol = 'BTCUSDC')['result']['list'][0]['execPrice'])
    bot.send_message(message.chat.id, f"Метка 1 = {lastOrderPrice}")
    
    while is_running:
        time.sleep(1)

        marketPrice = float(session.get_tickers(category="spot", symbol="BTCUSDC")['result']['list'][0]['ask1Price'])
        lastOrderPrice = float(session.get_executions(category='spot', symbol = 'BTCUSDC')['result']['list'][0]['execPrice'])

        if marketPrice - lastOrderPrice > 10:
            r.create_order_enter_2()
            if is_running:
                bot.send_message(message.chat.id, f"delta = {int(marketPrice - lastOrderPrice)} -> long")
                bot.send_message(message.chat.id, "Позиция открыта. Заврешаю работу")
            break
        elif marketPrice - lastOrderPrice > 0 and marketPrice - lastOrderPrice < 10:
            if is_running:
                bot.send_message(message.chat.id, f"delta = {int(marketPrice - lastOrderPrice)} -> hold")
        elif lastOrderPrice - marketPrice > 0 and lastOrderPrice - marketPrice < 10:
            if is_running:
                bot.send_message(message.chat.id, f"delta = {int(marketPrice - lastOrderPrice)} -> hold")
        else:
            metka = lastOrderPrice - 10
            with open('metka.txt', 'w') as file:
                file.write(str(metka))
            if is_running:
                bot.send_message(message.chat.id, f"created metka at {metka}. Завершаю работу")
            break

@bot.message_handler(func=lambda message: message.text == "Стратегия 2")
def handle_strategy_2(message):
    global is_running
    is_running = True
    i = 0
    while is_running:
        i+=1
        response =  f"Цикл {i}\n" \
                    f"Бот начинает работу. До старта {5} секунд"
        bot.send_message(message.chat.id, response)
        time.sleep(5)

        r.delete_all_orders()
        response =  f"Удалил ордера" 
        bot.send_message(message.chat.id, response)        
        time.sleep(5)

        try:
            r.create_order_11()
            response =  f"Закрыл все позиции" 
            bot.send_message(message.chat.id, response)    
        except InvalidRequestError:
            response =  f"Не могу закрыть позиции, не хватает баланса. Обратить внимание." 
            bot.send_message(message.chat.id, response)   
        time.sleep(5)

        r.create_order_enter_1()
        response =  f"Поставил enter_1 - закупил объем" 
        bot.send_message(message.chat.id, response) 
        time.sleep(5)

        r.create_order_9()
        response =  f"Поставил enter_9 - закупил резерв" 
        bot.send_message(message.chat.id, response) 
        time.sleep(5)

        r.create_order_1()
        r.create_order_3()
        r.create_order_4()
        response =  f"Выставил ордера 1-4: TP/SL" 
        bot.send_message(message.chat.id, response) 
        time.sleep(5)

        response =  f"waiting order execution..." 
        bot.send_message(message.chat.id, response) 
        l_o_type = None
        while l_o_type != 'Limit':
            l_o_type = session.get_executions(category='spot', symbol = 'BTCUSDC')['result']['list'][0]['orderType']

        response =  f"сработал TP/SL. Завершаю цикл. До старта следующего цикла 5 секунд" 
        bot.send_message(message.chat.id, response) 
        time.sleep(5)


@bot.message_handler(func=lambda message: message.text == "Баланс")
def handle_balance(message):
    token1_balance, token2_balance, total_balance = r.calculate_balance()
    response = f"Ваш текущий баланс:\n" \
               f"USDC: {token1_balance:.5f}\n" \
               f"BTC: {token2_balance:.8f}\n" \
               f"Общий баланс: {total_balance:.7f} USDC"
    bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: message.text == "Last Trades")
def handle_trades(message):
    trades = r.check_trades().head(5)
    trades = tabulate(trades, headers='keys', tablefmt='pretty')
    bot.send_message(message.chat.id, trades)


@bot.message_handler(func=lambda message: message.text == "STOP")
def handle_trades(message):
    global is_running
    is_running = False
    r.delete_all_orders()
    r.create_order_11()
    bot.send_message(message.chat.id, "Робот удален. Все позиции закрыты")

# Запуск бота
bot.polling()
