import telebot
from telebot import types
from utils import from_timestamp
import pandas as pd
from tabulate import tabulate
import pandas as pd
from pybit.unified_trading import HTTP
from pybit.exceptions import InvalidRequestError
from robot import Robot
import time
import yaml
import traceback

# Инициализация бота с токеном
session = HTTP(
    testnet=False,
    api_key="5wH56z5gvRFfoNKVd6",
    api_secret="N4n1P6PG3E9mwhwysF4fSQPpBR2ZACOkdmA9",
)
bot = telebot.TeleBot("6928882205:AAFHKZ8QNDUA4v_zw18Xo7VJvHH9VHMNKh0")
form = yaml.safe_load(open('form.yml', 'r'))
r = Robot()

is_running = False

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    itembtn_str1 = types.KeyboardButton('Стратегия 1(int_0)')
    itembtn_str2 = types.KeyboardButton('Стратегия 2(market_buy)')
    itembtn_balance = types.KeyboardButton('Баланс')
    itembtn_intervals = types.KeyboardButton('Интервалы')
    itembtn_orders = types.KeyboardButton('Ордера')
    itembtn_trades = types.KeyboardButton('Last Trades')
    itembtn_stop = types.KeyboardButton('STOP')
    markup.add(
        itembtn_str1, itembtn_str2, 
        itembtn_balance, itembtn_intervals, 
        itembtn_orders, itembtn_trades, 
        itembtn_stop
        )

    response =  f"Приветствую Вас!\n" \
                f"Пожалуйста, выберите статегию." 
    bot.send_message(message.chat.id, response, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Стратегия 1(int_0)")
def handle_strategy_1(message):

    global is_running
    if is_running:
        response = f"Стратегия уже выполняется.\n" \
                   f"Дождитесь выполнения стратегии."
        bot.send_message(message.chat.id, response)
    else:
        is_running = True

        r.delete_all_orders()
        r.create_order_11()
        r.create_order_9()
        response = f"Закрыл все ордера.\n" \
                   f"Поставил order_11 - продал все btc.\n" \
                   f"Закупил резерв."

        lastOrderPrice = r.check_last_order_price()
        bot.send_message(message.chat.id, f"Метка 1 = {lastOrderPrice}")
        
        while is_running:
            #to
            delta = r.check_market_price() - r.check_last_order_price()
            if delta > 10:
                r.create_order_enter_2()
                r.create_order_1()
                r.create_order_3() 
                r.create_order_4()
                status = 'orders'
            elif delta <= -10:
                metka = r.check_market_price()
                with open('metka.txt', 'w') as file:
                    file.write(str(metka))
                status = 'metka'
            else:
                status = 'pass'
                continue
            #t1
            if status == 'orders':
                side=r.check_last_order_side()
                if side == 'Buy': #order2
                    exec('block2')
                else:
                    #block3
                    delta = r.check_market_price() - r.check_last_order_price()
                    if delta > 15:
                        r.delete_all_orders()
                        r.create_order_8()
                        r.create_order_1()
                        r.create_order_3() 
                        r.create_order_4()
                    elif delta <= -10:
                        metka = r.check_market_price()
                        with open('metka.txt', 'w') as file:
                            file.write(str(metka))                        
                    else:
                       #в начало 3ьего
                       continue 
            elif status == 'metka':
                exec('block4')
            else:
                pass

@bot.message_handler(func=lambda message: message.text == "Стратегия 2(market_buy)")
def handle_strategy_2(message):

    global is_running
    if is_running:
        response = f"Стратегия уже выполняется.\n" \
                   f"Дождитесь выполнения стратегии."
        bot.send_message(message.chat.id, response)
    else:
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
                response =  f"Поставил order_11 - продал все btc." 
                bot.send_message(message.chat.id, response)    
            except InvalidRequestError:
                response =  f"Не могу закрыть позиции, не хватает баланса. Обратить внимание." 
                bot.send_message(message.chat.id, response)   
            time.sleep(5)

            r.create_order_9()
            response =  f"Поставил enter_9 - закупил резерв" 
            bot.send_message(message.chat.id, response) 
            time.sleep(5)
            
            r.create_order_enter_1()
            response =  f"Поставил enter_1 - закупил объем" 
            bot.send_message(message.chat.id, response) 
            r.create_order_1()
            r.create_order_3()
            r.create_order_4()
            open_orders_ = session.get_open_orders(category = 'spot', symbol = 'BTCUSDC')['result']['list']
            open_orders_id_ = pd.DataFrame.from_records(open_orders_)['orderId'].to_list()
            open_orders_id_.reverse()
            response =  f"Выставил ордера 1-4: TP/SL" 
            bot.send_message(message.chat.id, response) 
            time.sleep(5)

            # response =  f"waiting order execution..."  # - вариант черный ящик
            # bot.send_message(message.chat.id, response) 
            l_o_type = None
            while l_o_type != 'Limit':
                l_o_type = session.get_executions(category='spot', symbol = 'BTCUSDC')['result']['list'][0]['orderType']
                marketPrice = float(session.get_tickers(category="spot", symbol="BTCUSDC")['result']['list'][0]['ask1Price'])
                lastOrderPrice = float(session.get_executions(category='spot', symbol = 'BTCUSDC')['result']['list'][0]['execPrice'])
                response =  f"delta = {marketPrice-lastOrderPrice}"
                bot.send_message(message.chat.id, response)  

            l_o_id = session.get_executions(category='spot', symbol = 'BTCUSDC')['result']['list'][0]['orderId']
            if l_o_id == open_orders_id_[0]:
                order_that_worked = 'ордер 1 - stop loss'
            elif l_o_id == open_orders_id_[1]:
                order_that_worked = 'ордер 3 - stop loss'
            else:
                order_that_worked = 'ордер 4 - take profit' 
            l_2_0 = session.get_executions(category = 'spot',symbol = 'BTCUSDC')['result']['list'][:2]
            fr_ = pd.DataFrame.from_records(l_2_0)[['execValue']].astype(float)
            pnl_abs = fr_.loc[0] - fr_.loc[1]
            pnl_abs = round(pnl_abs.values[0], 4)
            response =  f"Сработал {order_that_worked}\n" \
                        f"Реализованная прибыль {pnl_abs} USDC.\n" \
                        f"Завершаю цикл.\n" \
                        f"До старта следующего цикла 5 секунд."
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

@bot.message_handler(func=lambda message: message.text == "Интервалы")
def handle_ints(message):
    response = f"Интервалы: \n {form['ints']}"
    bot.send_message(message.chat.id, response)
    response = f"Триггеры: \n {form['int_triggers']}"
    bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: message.text == "Ордера")
def handle_orders(message):
    try:
        bbt_request = session.get_open_orders(category='spot', symbol='BTCUSDC')
        open_orders = bbt_request['result']['list']
        if len(open_orders) > 0:
            fr_ =  pd.DataFrame.from_records(open_orders)[['symbol','orderType', 'side', 'qty', 'triggerPrice', 'price', 'createdTime']]
            fr_['createdTime'] = pd.to_datetime(fr_['createdTime'].apply(lambda x: from_timestamp(x)))
            response = tabulate(fr_, headers='keys', tablefmt='pretty')
            bot.send_message(message.chat.id, response)
        else:
            response = "Нет открытых ордеров"
            bot.send_message(message.chat.id, response)
    except ConnectionError:
        response = "Ошибка подключения к bybit - нет интернета"
        bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: message.text == "Last Trades")
def handle_trades(message):
    trades = r.check_trades().head(5)
    response = tabulate(trades, headers='keys', tablefmt='pretty')
    bot.send_message(message.chat.id, response)


@bot.message_handler(func=lambda message: message.text == "STOP")
def handle_trades(message):
    global is_running
    is_running = False
    r.delete_all_orders()
    try:
        r.create_order_11()
        bot.send_message(message.chat.id, "Робот удален. Все позиции закрыты")
    except InvalidRequestError:
        response =  f"Не могу закрыть позиции, не хватает баланса\n."\
                    f"Обратить внимание." 
        bot.send_message(message.chat.id, response)   

# Запуск бота
# bot.polling()

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(15)