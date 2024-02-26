from pybit.unified_trading import HTTP
from pybit.exceptions import InvalidRequestError
import telebot
from telebot import types
import pandas as pd
from tabulate import tabulate
import time
import yaml
from robot import Robot
from utils import from_timestamp

# Инициализация бота с токеном
session = HTTP(
    testnet=False,
    api_key="5wH56z5gvRFfoNKVd6",
    api_secret="N4n1P6PG3E9mwhwysF4fSQPpBR2ZACOkdmA9",
)
bot = telebot.TeleBot("6928882205:AAFHKZ8QNDUA4v_zw18Xo7VJvHH9VHMNKh0")

form = yaml.safe_load(open('form.yml', 'r'))
r = Robot()

sleep_time = 3 #счетчик
is_running = False

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    
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
        itembtn_stop,
        itembtn_vkl, itembtn_vikl
        )

    response =  f"Приветствую Вас!\n" \
                f"Пожалуйста, выберите статегию." 
    bot.send_message(message.chat.id, response, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Стратегия 1(int_0)")
def handle_strategy_1(message):
    #обработка двойного нажатия кнопки
    global is_running
    if is_running:
        response = f"Стратегия уже выполняется.\n" \
                   f"Дождитесь выполнения стратегии."
        bot.send_message(message.chat.id, response)
    else:
        is_running = True
        
        #t0 - block0(подготовка)
        bot.send_message(message.chat.id, '--Подготовка--') 
        r.delete_all_orders()
        r.create_order_11()
        r.create_order_9()
        response = f"Закрыл все ордера - delete open orders.\n" \
                   f"Выполнил order_11 прод. - продал все btc.\n" \
                   f"Выполнил order_9 пок. - закупил резерв.\n" 
        bot.send_message(message.chat.id, response)   
        time.sleep(sleep_time)

        #t1 - block1
        lo_price = r.check_last_order_price()
        bot.send_message(message.chat.id, f"--Нахожусь в Блоке 1. lo_price={lo_price}--")
        while is_running:
            metka = None
            delta = int(r.check_market_price() - r.check_last_order_price())
            if delta > 10:
                r.create_order_enter_2()
                r.create_order_1()
                r.create_order_3() 
                r.create_order_4()                        
                bot.send_message(message.chat.id, f"delta = {delta} -> Выполнил enter2 пок; Выставил ордера1-4")
                break
            elif delta < -10:
                metka = r.check_market_price()  
                bot.send_message(message.chat.id, f" delta={delta} -> Выставил метку по цене {metka}")
                break    
            else:
                bot.send_message(message.chat.id, f"delta={delta} -> hold")                
                time.sleep(sleep_time)        
        time.sleep(sleep_time)
                            
        #t2 - blocks2/3/4
        side = None
        decision = None
        while is_running:
            if metka is None:
                side=r.check_last_order_side()
                lo_price = r.check_last_order_price()
                if side == 'Buy':
                    decision = 'блок2'
                    bot.send_message(message.chat.id, f"last order={side} по {lo_price}-перехожу в {decision}")
                else:
                    decision = 'блок3'
                    bot.send_message(message.chat.id, f"last order={side} по {lo_price}-перехожу в {decision}")
            else:
                side = 'metka'
                decision = 'блок4'
                bot.send_message(message.chat.id, f"last order={side} по {metka}-перехожу в {decision}")  
            
            if side == 'Buy':
                lo_price = r.check_last_order_price()
                bot.send_message(message.chat.id, f"--Нахожусь в Блоке 2. lo_price={lo_price}--")
                while is_running:
                    delta = int(r.check_market_price() - r.check_last_order_price())
                    try:
                        order_5_is_active = r.check_orders()['name'].str.contains('order5').any()
                    except Exception:
                        order_5_is_active = False
                    if delta < 0:
                        r.delete_all_orders()
                        r.create_order_10()       
                        bot.send_message(message.chat.id,
                                         text = f"Закрыл все ордера - delete open orders\n"\
                                                f"delta={delta} -> Выполнил order10 прод.") 
                        break
                    elif order_5_is_active == False: 
                        # r.delete_all_orders() - александр попросил закомментить
                        r.create_order_5()                         
                        bot.send_message(message.chat.id, f"delta={delta} и order5={order_5_is_active} -> Выставил order5 прод.") 
                        break
                    else:
                        bot.send_message(message.chat.id, f"delta={delta} и order5={order_5_is_active} -> hold")
                        time.sleep(sleep_time)
                time.sleep(sleep_time)

            elif side == 'Sell':
                lo_price = r.check_last_order_price()
                bot.send_message(message.chat.id, f"--Нахожусь в Блоке 3. lo_price={lo_price}--")
                while is_running:
                    metka = None
                    delta = int(r.check_market_price() - r.check_last_order_price())
                    if delta > 15:
                        r.delete_all_orders()
                        r.create_order_8()
                        r.create_order_1()
                        r.create_order_3() 
                        r.create_order_4()
                        bot.send_message(message.chat.id,
                                         text = f"Закрыл все ордера - delete open orders\n"\
                                                f"delta={delta} -> Выполнил order8 пок; Выставил ордера1-4\n") 
                        break
                    elif delta < -10:
                        metka = r.check_market_price()
                        bot.send_message(message.chat.id, f" delta={delta} -> Выставил метку по цене {metka}")
                        break
                    else:
                        bot.send_message(message.chat.id, f"delta={delta} -> hold")
                        time.sleep(sleep_time)
                time.sleep(sleep_time)

            else:
                lo_price = r.check_last_order_price()
                bot.send_message(message.chat.id, f"--Нахожусь в Блоке 4. lo_price={lo_price}--")
                while is_running:
                    delta = int(r.check_market_price() - r.check_last_order_price())
                    if delta > 50: #int7
                        r.delete_all_orders()
                        r.create_order_7()
                        r.create_order_1()
                        r.create_order_3() 
                        r.create_order_4()
                        metka = None
                        bot.send_message(message.chat.id,
                                         text = f"Закрыл все ордера - delete open orders\n"\
                                                f"delta={delta} -> Выполнил order7 пок; Выставил ордера1-4\n"\
                                                f"Обнулил значение метки")                        
                        break
                    elif delta < -50: #int10
                        metka = r.check_market_price()
                        bot.send_message(message.chat.id, f"delta={delta} -> Выставил метку по цене {metka}")
                        break
                    else:
                        bot.send_message(message.chat.id, f"delta={delta} -> hold")
                        time.sleep(sleep_time)
                time.sleep(sleep_time)
                break

@bot.message_handler(func=lambda message: message.text == "Стратегия 2(market)")
def handle_strategy_2(message):
    #обработка двойного нажатия кнопки
    global is_running
    if is_running:
        response = f"Стратегия уже выполняется.\n" \
                   f"Дождитесь выполнения стратегии."
        bot.send_message(message.chat.id, response)
    else:
        is_running = True

        #t0 - block0(подготовка)
        bot.send_message(message.chat.id, '--Подготовка--') 
        r.delete_all_orders()
        r.create_order_11()
        r.create_order_9()
        response = f"Закрыл все ордера - delete open orders.\n" \
                   f"Выполнил order_11 прод. - продал все btc.\n" \
                   f"Выполнил order_9 пок. - закупил резерв.\n" 
        bot.send_message(message.chat.id, response)   
        time.sleep(sleep_time)
        
        #t1 - block1
        lo_price = r.check_last_order_price()
        bot.send_message(message.chat.id, f"--Нахожусь в Блоке 1. lo_price={lo_price}--")
        r.create_order_enter_1()
        r.create_order_1()
        r.create_order_3()
        r.create_order_4()
        bot.send_message(message.chat.id, f"Выполнил enter1 пок; Выставил ордера1-4")
        time.sleep(sleep_time)

        #t2 - blocks2,3,4
        metka = None
        side = None
        decision = None
        while is_running:
            if metka is None:
                side=r.check_last_order_side()
                lo_price = r.check_last_order_price()
                if side == 'Buy':
                    decision = 'блок2'
                    bot.send_message(message.chat.id, f"last order={side} по {lo_price}-перехожу в {decision}")
                else:
                    decision = 'блок3'
                    bot.send_message(message.chat.id, f"last order={side} по {lo_price}-перехожу в {decision}")
            else:
                side = 'metka'
                decision = 'блок4'
                bot.send_message(message.chat.id, f"last order={side} по {metka}-перехожу в {decision}")  

            if side == 'Buy':
                lo_price = r.check_last_order_price()
                bot.send_message(message.chat.id, f"--Нахожусь в Блоке 2. lo_price={lo_price}--")
                while is_running:
                    delta = int(r.check_market_price() - r.check_last_order_price())
                    try:
                        order_5_is_active = r.check_orders()['name'].str.contains('order5').any()
                    except Exception:
                        order_5_is_active = False
                    if delta < 0:
                        r.delete_all_orders()
                        r.create_order_10()       
                        bot.send_message(message.chat.id,
                                         text = f"Закрыл все ордера - delete open orders\n"\
                                                f"delta={delta} -> Выполнил order10 прод.") 
                        break
                    elif order_5_is_active == False: 
                        # r.delete_all_orders() - александр попросил закомментить
                        r.create_order_5()                         
                        bot.send_message(message.chat.id, f"delta={delta} и order5={order_5_is_active} -> Выставил order5 прод.") 
                        break
                    else:
                        bot.send_message(message.chat.id, f"delta={delta} и order5={order_5_is_active} -> hold")
                        time.sleep(sleep_time)
                time.sleep(sleep_time)

            elif side == 'Sell':
                lo_price = r.check_last_order_price()
                bot.send_message(message.chat.id, f"--Нахожусь в Блоке 3. lo_price={lo_price}--")
                while is_running:
                    metka = None
                    delta = int(r.check_market_price() - r.check_last_order_price())
                    if delta > 15:
                        r.delete_all_orders()
                        r.create_order_8()
                        r.create_order_1()
                        r.create_order_3() 
                        r.create_order_4()
                        bot.send_message(message.chat.id,
                                         text = f"Закрыл все ордера - delete open orders\n"\
                                                f"delta={delta} -> Выполнил order8 пок; Выставил ордера1-4\n") 
                        break
                    elif delta < -10:
                        metka = r.check_market_price()
                        bot.send_message(message.chat.id, f" delta={delta} -> Выставил метку по цене {metka}")
                        break
                    else:
                        bot.send_message(message.chat.id, f"delta={delta} -> hold")
                        time.sleep(sleep_time)
                time.sleep(sleep_time)

            else:
                lo_price = r.check_last_order_price()
                bot.send_message(message.chat.id, f"--Нахожусь в Блоке 4. lo_price={lo_price}--")
                while is_running:
                    delta = int(r.check_market_price() - r.check_last_order_price())
                    if delta > 50: #int7
                        r.delete_all_orders()
                        r.create_order_7()
                        r.create_order_1()
                        r.create_order_3() 
                        r.create_order_4()
                        metka = None
                        bot.send_message(message.chat.id,
                                         text = f"Закрыл все ордера - delete open orders\n"\
                                                f"delta={delta} -> Выполнил order7 пок; Выставил ордера1-4\n"\
                                                f"Обнулил значение метки")                        
                        break
                    elif delta < -50: #int10
                        metka = r.check_market_price()
                        bot.send_message(message.chat.id, f"delta={delta} -> Выставил метку по цене {metka}")
                        break
                    else:
                        bot.send_message(message.chat.id, f"delta={delta} -> hold")
                        time.sleep(sleep_time)
                time.sleep(sleep_time)
                break



@bot.message_handler(func=lambda message: message.text == "Купить value_1")
def handle_buy_value_1(message):
    try:
        r.delete_all_orders()
        r.create_order_8()
        r.create_order_1()
        r.create_order_3()
        r.create_order_4()
        bot.send_message(message.chat.id, text = 'Купил value_1')
    except Exception as e:
        bot.send_message(message.chat.id, "Недостаточный объем usdc на балансе")

@bot.message_handler(func=lambda message: message.text == "Продать value_1")
def handle_sell_value_1(message):
    try:
        r.create_order_10()
        bot.send_message(message.chat.id, "Продал value_1")
    except Exception as e:
        bot.send_message(message.chat.id, "Объем на балансе < value_1")



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

@bot.message_handler(func=lambda message: message.text == "Текущие Ордера")
def handle_orders(message):
    try:
        bbt_request = session.get_open_orders(category='spot', symbol='BTCUSDC')
        open_orders = bbt_request['result']['list']
        if len(open_orders) > 0:
            fr_ =  pd.DataFrame.from_records(open_orders)[['symbol','orderType', 'side', 'qty', 'triggerPrice', 'price', 'createdTime']]
            fr_['createdTime'] = pd.to_datetime(fr_['createdTime'].apply(lambda x: from_timestamp(x)))
            fr_ = fr_.head(7)
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
    trades = r.check_trades().head(10)
    response = tabulate(trades, headers='keys', tablefmt='pretty')
    bot.send_message(message.chat.id, response)



@bot.message_handler(func=lambda message: message.text == "STOP")
def handle_stop(message):
    global is_running
    is_running = False
    r.delete_all_orders()
    try:
        order_value_all = float(session.get_coin_balance(
            accountType="UNIFIED",
            coin="BTC",
        )['result']['balance']['walletBalance'])
        if order_value_all >= 0.00020: #больше мин объема на продажу
            r.create_order_11()

        token1_balance, token2_balance, total_balance = r.calculate_balance()
        bot.send_message(message.chat.id, f"--Робот удален. Все btc проданы. Общий баланс: {total_balance:.7f} USDC--")
    except InvalidRequestError:
        response =  f"Не могу продать btc, не хватает баланса\n."\
                    f"Обратить внимание." 
        bot.send_message(message.chat.id, response)   



@bot.message_handler(func=lambda message: message.text == "ВКЛ СЧЕТЧИК")
def handle_vkl(message):
    global is_running
    is_running = True

@bot.message_handler(func=lambda message: message.text == "ВЫКЛ СЧЕТЧИК")
def handle_vikl(message):
    global is_running
    is_running = False



# Запуск бота
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(15)