from datetime import datetime
import pandas as pd
import yaml
from pybit.unified_trading import HTTP
from utils import calculate_timestamp, from_timestamp, assign_order_name

session = HTTP(
    testnet=False,
    api_key="5wH56z5gvRFfoNKVd6",
    api_secret="N4n1P6PG3E9mwhwysF4fSQPpBR2ZACOkdmA9",
)
                                    
form = yaml.safe_load(open('form.yml', 'r'))

class Robot:

    def __init__(self) -> None:
        pass

    def delete_all_orders(self):
        session.cancel_all_orders(
            category="spot",
            symbol="BTCUSDC",
            orderFilter = 'StopOrder'
            )
    def create_order_11(self):
        order_value_all = float(session.get_coin_balance(
                accountType="UNIFIED",
                coin="BTC",
                )['result']['balance']['walletBalance'])
        if order_value_all > 0:  #непустой объем
            session.place_order(
                category = 'spot',
                symbol = 'BTCUSDC',
                isLeverage = form['isLeverage'],
                orderType = "Market",
                side = 'Sell',
                qty = order_value_all, #продать current объем btc
                marketUnit = 'baseCoin' 
                )

    def create_order_enter_1(self):
        session.place_order( 
            category = 'spot',
            symbol = 'BTCUSDC',
            isLeverage = form['isLeverage'],
            orderType = "Market",
            side = 'Buy',
            qty = form['values']['q_enter1'], # купить основной объем btc 1
            marketUnit = 'baseCoin'
        )
    def create_order_enter_2(self):
        session.place_order(
            category = 'spot',
            symbol = 'BTCUSDC',
            isLeverage = form['isLeverage'],
            orderType = 'Market',
            side = 'Buy',
            qty = form['values']['q_enter2'], # купить основной объем btc 2
            marketUnit = 'baseCoin'
        )
    def create_order_8(self):
        session.place_order(
            category = 'spot',
            symbol = 'BTCUSDC',
            isLeverage = form['isLeverage'],
            orderType = 'Market',
            side = 'Buy',
            qty = form['values']['q8'],
            marketUnit = 'baseCoin'
        )
    def create_order_9(self):
        session.place_order( 
            category = 'spot',
            symbol = 'BTCUSDC',
            isLeverage = form['isLeverage'],
            orderType = "Market",
            side = 'Buy',
            qty = form['values']['q9'], # купить резервный объем btc
            marketUnit = 'baseCoin'
        )

    def create_order_5(self):
        last_order_price = float(session.get_executions(category='spot', symbol = 'BTCUSDC')['result']['list'][0]['execPrice'])
        session.place_order( 
            category = 'spot',
            symbol = 'BTCUSDC',
            isLeverage = form['isLeverage'],
            orderFilter = 'StopOrder',
            orderType = "Market",
            side = 'Sell',
            triggerPrice = last_order_price,
            qty = form['values']['q5'],
            marketUnit = 'baseCoin'
        )
    def create_order_10(self):
        session.place_order( 
            category = 'spot',
            symbol = 'BTCUSDC',
            isLeverage = form['isLeverage'],
            orderType = "Market",
            side = 'Sell',
            qty = form['values']['q10'],
            marketUnit = 'baseCoin'
        )     

    def create_order_1(self):
        marketPrice = float(session.get_tickers(category="spot", symbol="BTCUSDC")['result']['list'][0]['ask1Price'])
        session.place_order( 
            category = 'spot',
            symbol = 'BTCUSDC',
            isLeverage = form['isLeverage'],
            orderType = "Limit",
            side = 'Sell',
            orderFilter = 'StopOrder',
            triggerPrice = marketPrice - 5,  #int1 - trigger1
            price = marketPrice - 10, #int1
            qty = form['values']['q1'],
            marketUnit = 'baseCoin'
            )            
    def create_order_3(self):
        marketPrice = float(session.get_tickers(category="spot", symbol="BTCUSDC")['result']['list'][0]['ask1Price'])
        session.place_order( 
            category = 'spot',
            symbol = 'BTCUSDC',
            isLeverage = form['isLeverage'],
            orderType = "Limit",
            side = 'Sell',
            orderFilter = 'StopOrder',
            triggerPrice = marketPrice - 40,  #int3-trigger2
            price = marketPrice - 50, #int3
            qty = form['values']['q3'],
            marketUnit = 'baseCoin'
            )
    def create_order_4(self):
        marketPrice = float(session.get_tickers(category="spot", symbol="BTCUSDC")['result']['list'][0]['ask1Price'])
        session.place_order( 
            category = 'spot',
            symbol = 'BTCUSDC',
            isLeverage = form['isLeverage'],
            orderType = "Limit",
            side = 'Sell',
            orderFilter = 'StopOrder',
            triggerPrice = marketPrice + 10, #form['int_4'] - form['int_trigger3'] вергуть 20/40
            price = marketPrice + 20, #form['int_4'
            qty = form['values']['q4'],
            marketUnit = 'baseCoin' 
            )
        
    def check_exec_time(self):
        execTime = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        return execTime
    def check_market_price(self):
        marketPrice = float(session.get_tickers(category="spot", symbol="BTCUSDC")['result']['list'][0]['ask1Price'])
        return marketPrice
    def check_last_order_price(self):
        last_order_price = float(session.get_executions(category='spot', symbol = 'BTCUSDC')['result']['list'][0]['execPrice'])
        return last_order_price
    def check_last_order_side(self):
        last_order_id = session.get_executions(category='spot', symbol = 'BTCUSDC')['result']['list'][0]['side']
        return last_order_id
    def save_metka_to_file(self, metka):
        with open('metka.txt', 'w') as file:
            file.write(str(metka))

    def check_orders(self):
        #обработка отсутствия ор
        bbt_request = session.get_open_orders(category='spot', symbol='BTCUSDC')
        open_orders = bbt_request['result']['list']
        fr_ =  pd.DataFrame.from_records(open_orders)[['symbol','orderType', 'side', 'qty', 'triggerPrice', 'price', 'createdTime']]
        fr_['qty'] = fr_['qty'].astype(float)
        fr_['createdTime'] = pd.to_datetime(fr_['createdTime'].apply(lambda x: from_timestamp(x)))
        fr_['createdTime'] = fr_['createdTime'].dt.time
        fr_['name'] = fr_.apply(assign_order_name, axis =1)
        return fr_
    def check_trades(self):
        trades = session.get_executions(category="spot",)['result']['list']
        trades_table = pd.DataFrame.from_records(trades)
        attr_ = ['orderType', 'side', 'execQty',  'execTime']
        trades_table = trades_table[attr_]
        trades_table['execQty'] = trades_table['execQty'].astype(float)
        trades_table.rename(columns={'execQty':'qty'}, inplace = True)
        trades_table['execTime'] = pd.to_datetime(trades_table['execTime'].apply(lambda x: from_timestamp(x)))
        trades_table['execTime'] = trades_table['execTime'].dt.time
        trades_table['name'] = trades_table.apply(assign_order_name, axis =1)
        return trades_table
    def calculate_balance(self):
        
        marketPrice = float(session.get_tickers(category="spot", symbol="BTCUSDC")['result']['list'][0]['ask1Price'])
        token1_balance = float(session.get_coin_balance(accountType="UNIFIED",coin="USDC",)['result']['balance']['walletBalance'])
        token2_balance = float(session.get_coin_balance(accountType="UNIFIED",coin="BTC",)['result']['balance']['walletBalance'])
        total_balance = token1_balance + marketPrice * token2_balance
        return token1_balance, token2_balance, total_balance

    def calc_open_orders_id(self):
        bbt_req = session.get_open_orders(category = 'spot', symbol = 'BTCUSDC')
        open_orders_ = bbt_req['result']['list']
        open_orders_id_ = pd.DataFrame.from_records(open_orders_)['orderId'].to_list()
        open_orders_id_.reverse()
        return open_orders_id_
    def calc_open_orders_table(self):
        bbt_req = session.get_open_orders(category = 'spot', symbol = 'BTCUSDC')
        open_orders_ = bbt_req['result']['list']

        attribs_ = ['symbol','orderType', 'side', 'qty', 'triggerPrice', 'price', 'createdTime']
        fr_ =  pd.DataFrame.from_records(open_orders_)[attribs_]
        # fr_['createdTime'] = pd.to_datetime(fr_['createdTime'].apply(lambda x: from_timestamp(x)))
        # fr_['createdTime'] = fr_['createdTime'].dt.time
        return fr_