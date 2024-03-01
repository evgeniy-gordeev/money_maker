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


# Обработчики
@bot.message_handler(commands=['start'])
def handle_start(message):
    response =  f"Приветствую Вас!\n"\
                f"В меню слева доступны команды\n"\
                f'"Смена Формы" и "Запуск Стратегии"'
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['chg_form'])
def form_chg(message):
    bot.send_message(message.chat.id, 
                     text = f"Пожалуйста, подгрузите form.yml\n"
                            f"По умолчанию используется форма разработчика.\n"
                            f"Пропустите шаг, если изменения не требуются.\n"
                            f"Не нужно писать комментарии к форме.")

@bot.message_handler(commands=['strategy'])
def handle_strat(message):
    menu_logic(message)

@bot.message_handler(content_types=['document'])
def proc_document(message):
    document_logic(message)


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
        bot.send_message(message.chat.id, f"--Нахожусь в Блоке 1--\n"\
                                          f"--LO_price={lo_price}--")
        while is_running:
            metka = None
            delta = int(r.check_market_price() - r.check_last_order_price())
            if delta > form['ints']['int_0']:
                r.create_order_enter_2()
                r.create_order_1()
                r.create_order_3() 
                r.create_order_4()                        
                bot.send_message(message.chat.id, f"delta={delta} ---> \n"\
                                                  f"Выполнил enter2 пок\n"\
                                                  f"Выставил ордера 1-4")
                break
            elif delta < -form['ints']['int_9']:
                metka = r.check_market_price()  
                bot.send_message(message.chat.id, f"delta={delta} ----> \n"\
                                                  f"Выставил метку по цене {metka}")
                break    
            else:
                bot.send_message(message.chat.id, f"delta={delta} ---> hold")                
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
                    decision = 'Блок2'
                    bot.send_message(message.chat.id, f"Last Order = {side} по {lo_price} --->\n"\
                                                      f"Перехожу в {decision}")
                else:
                    decision = 'Блок3'
                    bot.send_message(message.chat.id, f"Last Order = {side} по {lo_price} --->\n"\
                                                      f"Перехожу в {decision}")
            else:
                side = 'metka'
                decision = 'Блок4'
                bot.send_message(message.chat.id, f"Last Order = {side} по {metka} --->\n"\
                                                  f"Перехожу в {decision}") 
            
            if side == 'Buy':
                lo_price = r.check_last_order_price()
                bot.send_message(message.chat.id, f"--Нахожусь в Блоке 2--\n"\
                                                  f"--LO_price={lo_price}--")                
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
                                         text = f"Закрыл все ордера - delete open orders.\n"\
                                                f"delta={delta} --->\n"\
                                                f"Выполнил order10 прод.") 
                        break
                    elif order_5_is_active == False: 
                        # r.delete_all_orders() - александр попросил закомментить
                        r.create_order_5()                         
                        bot.send_message(message.chat.id, f"delta={delta} и order5={order_5_is_active} --->\n"\
                                                          f"Выставил order5 прод.") 
                        break
                    else:
                        bot.send_message(message.chat.id, f"delta={delta} и order5={order_5_is_active} ---> hold")
                        time.sleep(sleep_time)
                time.sleep(sleep_time)

            elif side == 'Sell':
                lo_price = r.check_last_order_price()
                bot.send_message(message.chat.id, f"--Нахожусь в Блоке 3--\n"\
                                                  f"--LO_price={lo_price}--")
                r.delete_all_orders()
                bot.send_message(message.chat.id, "Закрыл все ордера - delete open orders")
                while is_running:
                    metka = None
                    delta = int(r.check_market_price() - r.check_last_order_price())
                    if delta > form['ints']['int_8']:
                        r.delete_all_orders()
                        r.create_order_8()
                        r.create_order_1()
                        r.create_order_3() 
                        r.create_order_4()
                        bot.send_message(message.chat.id, 
                                         text = f"delta={delta} --->\n"\
                                                f"Выполнил order8 пок.\n"\
                                                f"Выставил ордера 1-4") 
                        break
                    elif delta < -form['ints']['int_9']:
                        metka = r.check_market_price()
                        bot.send_message(message.chat.id, f"delta={delta} --->\n"\
                                                          f"Выставил метку по цене {metka}")
                        break
                    else:
                        bot.send_message(message.chat.id, f"delta={delta} ---> hold")
                        time.sleep(sleep_time)
                time.sleep(sleep_time)

            else:
                bot.send_message(message.chat.id, f"--Нахожусь в Блоке 4--\n"\
                                                  f"--LO_price={metka}--")
                while is_running:
                    delta = int(r.check_market_price() - metka)
                    if delta > form['ints']['int_7']:
                        r.delete_all_orders()
                        r.create_order_7()
                        r.create_order_1()
                        r.create_order_3() 
                        r.create_order_4()
                        metka = None
                        bot.send_message(message.chat.id,
                                         text = f"Закрыл все ордера - delete open orders\n"\
                                                f"delta={delta} --->\n"\
                                                f"Выполнил order7 пок.\n"\
                                                f"Выставил ордера 1-4\n"\
                                                f"Обнулил значение метки")                        
                        break
                    elif delta < -form['ints']['int_10']:
                        metka = r.check_market_price()
                        bot.send_message(message.chat.id, f"delta={delta} --->\n"\
                                                          f"Выставил метку по цене {metka}")
                        break
                    else:
                        bot.send_message(message.chat.id, f"delta={delta} ---> hold")
                        time.sleep(sleep_time)
                time.sleep(sleep_time)

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
        bot.send_message(message.chat.id, f"--Нахожусь в Блоке 1--\n"\
                                          f"--LO_price={lo_price}--")       
        r.create_order_enter_1()
        r.create_order_1()
        r.create_order_3()
        r.create_order_4()
        bot.send_message(message.chat.id, f"Выполнил enter1 пок.\n"\
                                          f"Выставил ордера 1-4")
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
                    decision = 'Блок2'
                    bot.send_message(message.chat.id, f"Last Order = {side} по {lo_price} --->\n"\
                                                      f"Перехожу в {decision}")
                else:
                    decision = 'Блок3'
                    bot.send_message(message.chat.id, f"Last Order = {side} по {lo_price} --->\n"\
                                                      f"Перехожу в {decision}")
            else:
                side = 'metka'
                decision = 'Блок4'
                bot.send_message(message.chat.id, f"Last Order = {side} по {metka} --->\n"\
                                                  f"Перехожу в {decision}") 

            if side == 'Buy':
                lo_price = r.check_last_order_price()
                bot.send_message(message.chat.id, f"--Нахожусь в Блоке 2--\n"\
                                                  f"--LO_price={lo_price}--")                
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
                                         text = f"Закрыл все ордера - delete open orders.\n"\
                                                f"delta={delta} --->\n"\
                                                f"Выполнил order10 прод.") 
                        break
                    elif order_5_is_active == False: 
                        # r.delete_all_orders() - александр попросил закомментить
                        r.create_order_5()                         
                        bot.send_message(message.chat.id, f"delta={delta} и order5={order_5_is_active} --->\n"\
                                                          f"Выставил order5 прод.") 
                        break
                    else:
                        bot.send_message(message.chat.id, f"delta={delta} и order5={order_5_is_active} ---> hold")
                        time.sleep(sleep_time)
                time.sleep(sleep_time)

            elif side == 'Sell':
                lo_price = r.check_last_order_price()
                bot.send_message(message.chat.id, f"--Нахожусь в Блоке 3--\n"\
                                                  f"--LO_price={lo_price}--")
                r.delete_all_orders()
                bot.send_message(message.chat.id, "Закрыл все ордера - delete open orders")
                while is_running:
                    metka = None
                    delta = int(r.check_market_price() - r.check_last_order_price())
                    if delta > form['ints']['int_8']:
                        r.create_order_8()
                        r.create_order_1()
                        r.create_order_3() 
                        r.create_order_4()
                        bot.send_message(message.chat.id,
                                         text = f"Закрыл все ордера - delete open orders\n"\
                                                f"delta={delta} --->\n"\
                                                f"Выполнил order8 пок.\n"\
                                                f"Выставил ордера 1-4") 
                        break
                    elif delta < -form['ints']['int_9']:
                        metka = r.check_market_price()
                        bot.send_message(message.chat.id, f"delta={delta} --->\n"\
                                                          f"Выставил метку по цене {metka}")
                        break
                    else:
                        bot.send_message(message.chat.id, f"delta={delta} ---> hold")
                        time.sleep(sleep_time)
                time.sleep(sleep_time)

            else:
                bot.send_message(message.chat.id, f"--Нахожусь в Блоке 4--\n"\
                                                  f"--LO_price={metka}--")
                while is_running:
                    delta = int(r.check_market_price() - metka)
                    if delta > form['ints']['int_7']:
                        r.delete_all_orders()
                        r.create_order_7()
                        r.create_order_1()
                        r.create_order_3() 
                        r.create_order_4()
                        metka = None
                        bot.send_message(message.chat.id,
                                         text = f"Закрыл все ордера - delete open orders\n"\
                                                f"delta={delta} --->\n"\
                                                f"Выполнил order7 пок.\n"\
                                                f"Выставил ордера 1-4\n"\
                                                f"Обнулил значение метки")                        
                        break
                    elif delta < -form['ints']['int_10']:
                        metka = r.check_market_price()
                        bot.send_message(message.chat.id, f"delta={delta} --->\n"\
                                                          f"Выставил метку по цене {metka}")
                        break
                    else:
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