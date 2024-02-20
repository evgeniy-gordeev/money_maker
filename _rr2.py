from pybit.unified_trading import HTTP
session = HTTP(
    testnet=False,
    api_key="5wH56z5gvRFfoNKVd6",
    api_secret="N4n1P6PG3E9mwhwysF4fSQPpBR2ZACOkdmA9",
)
from robot import Robot
import pandas as pd
r = Robot()
import time

i = 0
while True:
    i+=1
    
    print('____________________')
    print(f'Цикл {i}')
    print(f'Бот начинает работу. До страта {5} секунд')
    time.sleep(5)

    r.delete_all_orders()
    print('Удалил ордера')
    time.sleep(5)

    r.create_order_11()
    print('Закрыл все позиции')
    time.sleep(5)

    r.create_order_9()
    print('поставил enter 9 - закупил резерыв')
    time.sleep(5)
    r.create_order_enter_1()
    print('поставил enter 1 - закупил объем')
    time.sleep(5)

    r.create_order_1()
    r.create_order_3()
    r.create_order_4()
    open_orders_ = session.get_open_orders(category = 'spot',symbol = 'BTCUSDC')['result']['list']
    open_orders_id_ = pd.DataFrame.from_records(open_orders_)['orderId'].to_list()
    open_orders_id_.reverse()
    print('выставил orders 1-4: TP/SL')
    time.sleep(5)

    print('waiting order execution...')
    l_o_type = None
    while l_o_type != 'Limit':
        l_o_type = session.get_executions(category='spot', symbol = 'BTCUSDC')['result']['list'][0]['orderType']
    
    l_o_id = session.get_executions(category='spot', symbol = 'BTCUSDC')['result']['list'][0]['orderId']
    if l_o_id == open_orders_id_[0]:
        order_that_worked = 'ордер 1 - stop loss'
    elif l_o_id == open_orders_id_[1]:
        order_that_worked = 'ордер 3 - stop loss'
    else:
        order_that_worked = 'ордер 4 - take profit'    
    print(f"сработал {order_that_worked}. Завершаю цикл через 5 секунд")
    time.sleep(5)
