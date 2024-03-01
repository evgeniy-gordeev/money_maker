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
from backend.form_chg import document_logic
from backend.commands import menu_logic

# Конфиги
form = yaml.safe_load(open('form.yml', 'r'))

# Инициализация бота с токеном
session = HTTP(testnet=False, api_key=form['bybit']['api_key'], api_secret=form['bybit']['api_secret'])
bot = telebot.TeleBot(token=form['tg']['bot_token'])
r = Robot()

# Константы
sleep_time = form['time_period'] #счетчик
is_running = False


def delete_orders_and_balance(message):
    r.delete_all_orders()
    try:
        r.create_order_11()
        token1_balance, token2_balance, total_balance = r.calculate_balance()
        bot.send_message(message.chat.id, 
                         text = f"--Робот удален. Все btc проданы.--\n"\
                                f"--Общий баланс: {total_balance:.7f} USDC--")
    except InvalidRequestError:
        response =  f"Не могу продать btc, не хватает баланса\n."\
                    f"Обратить внимание." 
        bot.send_message(message.chat.id, response)   


# Обработчики
@bot.message_handler(commands=['start'])
def handle_start(message):
    response =  f"Приветствую Вас!\n"\
                f"В меню слева доступны команды\n"\
                f'"Смена Формы" и "Запуск Стратегии"'
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['chg_form'])
def form_chg(message):
    response =  f"Пожалуйста, подгрузите form.yml\n"\
                f"По умолчанию используется форма разработчика.\n"\
                f"Пропустите шаг, если изменения не требуются.\n"\
                f"Не нужно писать комментарии к форме."
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['strategy'])
def handle_strat(message):
    menu_logic(message)

@bot.message_handler(content_types=['document'])
def proc_document(message):
    document_logic(message)


@bot.message_handler(func=lambda message: message.text == "Стратегия 1(int_0)" or message.text == "Стратегия 2(market)")
def handle_strategy(message):
    #обработка двойного нажатия кнопки
    global is_running
    if is_running:
        response = f"Стратегия уже выполняется.\n" \
                   f"Дождитесь выполнения стратегии."
        bot.send_message(message.chat.id, response)
    else:
        is_running = True
        
        #t0.1 - block0(подготовка)
        enter_balance = r.calculate_total_balance()
        max_profit = None
        response =  f"--Подготовка--\n"\
                    f"--Начальный баланс {enter_balance} USDC"
        bot.send_message(message.chat.id, response)
        time.sleep(sleep_time)

        #t0.2 - block0(подготовка)
        r.delete_all_orders()
        r.create_order_11()
        r.create_order_9()
        response = f"Закрыл все ордера - delete open orders.\n" \
                   f"Выполнил order_11 прод. - продал все btc.\n" \
                   f"Выполнил order_9 пок. - закупил резерв.\n" 
        bot.send_message(message.chat.id, response)   
        time.sleep(sleep_time)

        
        #t1.1 - block1 intro
        profit = round(r.calculate_total_balance() - enter_balance, 3)
        max_profit = round(profit, 3)
        lo_price = r.check_last_order_price()
        bot.send_message(message.chat.id, f"--Нахожусь в Блоке 1--\n"\
                                          f"--LO_price={lo_price}--\n"\
                                          f"--profit={profit} USDC, max={max_profit} USDC--")
        time.sleep(sleep_time)
    
        #t1.2 - block1 action
        if message.text == "Стратегия 1(int_0)":
            while is_running:                
                delta = int(r.check_market_price() - r.check_last_order_price())
                if delta > form['ints']['int_0']:
                    metka = None
                    try:
                        r.create_order_enter_2()
                        order_price = r.check_last_order_price()
                        r.create_order_1()
                        r.create_order_3() 
                        r.create_order_4()                   
                        bot.send_message(message.chat.id, f"delta={delta} ---> \n"\
                                                        f"Выполнил enter2 пок {order_price}\n"\
                                                        f"Выставил ордера 1-4")
                    except Exception:
                        bot.send_message(message.chat.id, "Ошибка. Перезапустите бота")     
                    break
                elif delta < -form['ints']['int_9']:
                    metka = r.check_market_price()  
                    bot.send_message(message.chat.id, f"delta={delta} ----> \n"\
                                                    f"Выставил метку по цене {metka}")
                    break    
                else:
                    metka = None
                    bot.send_message(message.chat.id, f"delta={delta} ---> hold")
                    time.sleep(sleep_time)
            time.sleep(sleep_time)
        if message.text == "Стратегия 2(market)":
            metka = None
            try:
                r.create_order_enter_1()
                order_price = r.check_last_order_price()
                r.create_order_1()
                r.create_order_3()
                r.create_order_4()
                bot.send_message(message.chat.id, f"Выполнил enter1 пок. {order_price}\n"\
                                                f"Выставил ордера 1-4")
            except Exception:
                bot.send_message(message.chat.id, "Ошибка. Перезапустите бота")
            time.sleep(sleep_time)
        

        #t2 - blocks2/3/4
        side = None
        decision = None
        while is_running:
            if metka is None:
                side=r.check_last_order_side()
                lo_price = r.check_last_order_price()
                if side == 'Buy':
                    decision = 'Блок2'
                    bot.send_message(message.chat.id, f"Last Order = {side} по {lo_price} --->\n"\
                                                      f"Перехожу в {decision}")
                    time.sleep(sleep_time)
                else:
                    decision = 'Блок3'
                    bot.send_message(message.chat.id, f"Last Order = {side} по {lo_price} --->\n"\
                                                      f"Перехожу в {decision}")
                    time.sleep(sleep_time)
            else:
                side = 'metka'
                decision = 'Блок4'
                bot.send_message(message.chat.id, f"Last Order = {side} по {metka} --->\n"\
                                                  f"Перехожу в {decision}") 
                time.sleep(sleep_time)
            
            if side == 'Buy':
                #t2.1 - block2 intro
                profit = round(r.calculate_total_balance() - enter_balance, 3)
                max_profit = profit if profit >= max_profit else max_profit                
                lo_price = r.check_last_order_price()
                bot.send_message(message.chat.id, f"--Нахожусь в Блоке 2--\n"\
                                                f"--LO_price={lo_price}--\n"\
                                                f"--profit={profit} USDC, max={max_profit} USDC--")
                time.sleep(sleep_time)

                #_----
                if profit <= max_profit - form['int_profit']:
                    is_running = False
                    bot.send_message(message.chat.id, 'max-int_profit>profit')
                    delete_orders_and_balance(message)
                else:
                    is_running = True   
                
                #t2.2 - block2 action
                while is_running:
                    delta = int(r.check_market_price() - r.check_last_order_price())
                    order_5_is_active = r.check_order5_active()
                    if delta < 0:
                        try:
                            metka = None
                            r.delete_all_orders()
                            r.create_order_10()       
                            bot.send_message(message.chat.id, f"Закрыл все ордера - delete open orders.\n"\
                                                            f"delta={delta} --->\n"\
                                                            f"Выполнил order10 прод.") 
                        except Exception:
                            bot.send_message(message.chat.id, "Ошибка. Перезапустите бота")
                        break
                    elif order_5_is_active == False: 
                        try:
                            metka = None
                            # r.delete_all_orders() - александр попросил закомментить
                            r.create_order_5()
                            try:
                                price = session.get_open_orders(category = 'spot', symbol=form['symbol'])['result']['list'][0]['triggerPrice']
                            except Exception:
                                price = 'цена не определена'

                            bot.send_message(message.chat.id, f"delta={delta} и order5={order_5_is_active} --->\n"\
                                                              f"Выставил order5 прод. {price}")
                            del price 
                        except Exception:
                            bot.send_message(message.chat.id, "Ошибка. Перезапустите бота")
                        break
                    else:
                        metka = None
                        bot.send_message(message.chat.id, f"delta={delta} и order5={order_5_is_active} ---> hold")
                        time.sleep(sleep_time)
                time.sleep(sleep_time)

            elif side == 'Sell':
                #t3.1 - block3 intro
                profit = round(r.calculate_total_balance() - enter_balance, 3)
                max_profit = profit if profit >= max_profit else max_profit                
                lo_price = r.check_last_order_price()
                r.delete_all_orders()
                bot.send_message(message.chat.id, f"--Нахожусь в Блоке 3--\n"\
                                                f"--LO_price={lo_price}--\n"\
                                                f"--profit={profit} USDC, max={max_profit} USDC--\n"\
                                                f"--Закрыл все ордера-delete open orders--")
                time.sleep(sleep_time)

                #_----
                if profit <= max_profit - form['int_profit']:
                    is_running = False
                    bot.send_message(message.chat.id, 'max-int_profit>profit')
                    delete_orders_and_balance(message)
                else:
                    is_running = True   

                #t3.2 - block3 action
                while is_running:                    
                    delta = int(r.check_market_price() - r.check_last_order_price())
                    if delta > form['ints']['int_8']:
                        try:
                            metka = None
                            r.create_order_8()
                            order_price = r.check_last_order_price()
                            r.create_order_1()
                            r.create_order_3() 
                            r.create_order_4()
                            bot.send_message(message.chat.id, 
                                            text = f"delta={delta} --->\n"\
                                                    f"Выполнил order8 пок. {order_price}\n"\
                                                    f"Выставил ордера 1-4") 
                        except Exception:
                            bot.send_message(message.chat.id, "Ошибка. Перезапустите бота")
                        break
                    elif delta < -form['ints']['int_9']:
                        metka = r.check_market_price()
                        bot.send_message(message.chat.id, f"delta={delta} --->\n"\
                                                          f"Выставил метку по цене {metka}")
                        break
                    else:
                        metka = None
                        bot.send_message(message.chat.id, f"delta={delta} ---> hold")
                        time.sleep(sleep_time)
                time.sleep(sleep_time)

            else:
                #t4.1 - block4 intro
                profit = round(r.calculate_total_balance() - enter_balance, 3)
                max_profit = profit if profit >= max_profit else max_profit                
                bot.send_message(message.chat.id, f"--Нахожусь в Блоке 4--\n"\
                                                f"--LO_price={metka}--\n"\
                                                f"--profit={profit} USDC, max={max_profit} USDC--")
                if profit <= max_profit - form['int_profit']:
                    is_running = False
                    bot.send_message(message.chat.id, 'max-int_profit>profit')
                    delete_orders_and_balance(message)
                else:
                    is_running = True   
                time.sleep(sleep_time)

                #t4.2 - block4 action
                while is_running:
                    delta = int(r.check_market_price() - metka)
                    if delta > form['ints']['int_7']:
                        try:
                            metka = None
                            r.delete_all_orders()
                            r.create_order_7()
                            order_price = r.check_last_order_price()
                            r.create_order_1()
                            r.create_order_3() 
                            r.create_order_4()                        
                            bot.send_message(message.chat.id, f"Закрыл все ордера - delete open orders\n"\
                                                            f"delta={delta} --->\n"\
                                                            f"Выполнил order7 пок. {order_price}\n"\
                                                            f"Выставил ордера 1-4\n"\
                                                            f"Обнулил значение метки")  
                        except Exception:
                            bot.send_message(message.chat.id, "Ошибка. Перезапустите бота")                                                  
                        break
                    elif delta < -form['ints']['int_10']:
                        metka = r.check_market_price()
                        bot.send_message(message.chat.id, f"delta={delta} --->\n"\
                                                          f"Выставил метку по цене {metka}")
                        break
                    else:
                        metka = None
                        bot.send_message(message.chat.id, f"delta={delta} ---> hold")
                        time.sleep(sleep_time)
                time.sleep(sleep_time)


@bot.message_handler(func=lambda message: message.text == "Купить value_1")
def handle_buy_value_1(message):
    try:
        r.delete_all_orders()
        r.create_order_8()
        r.create_order_1()
        r.create_order_3()
        r.create_order_4()
        bot.send_message(message.chat.id, text = 'Купил value_1')
    except Exception:
        bot.send_message(message.chat.id, "Недостаточный объем usdc на балансе")

@bot.message_handler(func=lambda message: message.text == "Продать value_1")
def handle_sell_value_1(message):
    try:
        r.create_order_10()
        bot.send_message(message.chat.id, "Продал value_1")
    except Exception:
        bot.send_message(message.chat.id, "Объем на балансе < value_1")



@bot.message_handler(func=lambda message: message.text == "Баланс")
def handle_balance(message):
    try:
        token1_balance, token2_balance, total_balance = r.calculate_balance()
        response = f"Ваш текущий баланс:\n" \
                f"USDC: {token1_balance:.5f}\n" \
                f"BTC: {token2_balance:.8f}\n" \
                f"Общий баланс: {total_balance:.7f} USDC"
        bot.send_message(message.chat.id, response)
    except:
        bot.send_message(message.chat.id, "Баланс не может быть посчитан")
        
@bot.message_handler(func=lambda message: message.text == "Интервалы")
def handle_ints(message):
    try:
        response = f"Интервалы: \n {form['ints']}"
        bot.send_message(message.chat.id, response)
    except Exception:
        bot.send_message(message.chat.id, "Не заданы интревалы")

    try:
        response = f"Триггеры: \n {form['int_triggers']}"
        bot.send_message(message.chat.id, response)
    except Exception:
        bot.send_message(message.chat.id, "Не заданы триггерные интревалы")

@bot.message_handler(func=lambda message: message.text == "Текущие Ордера")
def handle_orders(message):
    try:
        fr_ = r.check_orders().head(7)
        response = tabulate(fr_, headers='keys', tablefmt='pretty')
        bot.send_message(message.chat.id, response)
    except Exception:
        response = "Нет открытых ордеров"
        bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: message.text == "Last Trades")
def handle_trades(message):
    try:
        trades = r.check_trades().head(10)
        response = tabulate(trades, headers='keys', tablefmt='pretty')
        bot.send_message(message.chat.id, response)
    except Exception:
        response = "Отсутствует история торговли"
        bot.send_message(message.chat.id, response)



@bot.message_handler(func=lambda message: message.text == "ВКЛ СЧЕТЧИК")
def handle_vkl(message):
    global is_running
    if is_running:
        bot.send_message(message.chat.id, "Счетчик уже включен")
    else:
        is_running = True
        bot.send_message(message.chat.id, "Включил счетчик")

@bot.message_handler(func=lambda message: message.text == "ВЫКЛ СЧЕТЧИК")
def handle_vikl(message):
    global is_running
    if is_running==False:
        bot.send_message(message.chat.id, "Счетчик уже выключен")
    else:
        is_running = False
        bot.send_message(message.chat.id, "Выключил счетчик")



@bot.message_handler(func=lambda message: message.text == "STOP")
def handle_stop(message):
    global is_running
    is_running = False
    r.delete_all_orders()
    try:
        r.create_order_11()
        token1_balance, token2_balance, total_balance = r.calculate_balance()
        bot.send_message(message.chat.id, 
                         text = f"--Робот удален. Все btc проданы.--\n"\
                                f"--Общий баланс: {total_balance:.7f} USDC--")
    except InvalidRequestError:
        response =  f"Не могу продать btc, не хватает баланса\n."\
                    f"Обратить внимание." 
        bot.send_message(message.chat.id, response)  

# Запуск бота
while True:
    try:
        bot.polling(none_stop=True, restart_on_change=True, path_to_watch='restart.txt')
    except Exception as e:
        print(e)
        time.sleep(15)