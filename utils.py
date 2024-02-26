import yaml
from pybit.unified_trading import HTTP
from datetime import datetime

keys = yaml.safe_load(open('keys.yml', 'r'))           
form = yaml.safe_load(open('form.yml', 'r'))
session = HTTP(testnet=False, api_key=keys['bybit']['api_key'], api_secret=keys['bybit']['api_secret'])


def calculate_timestamp(start_date_str:str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
    timestamp = start_date.timestamp()*1000
    return timestamp

def from_timestamp(timestamp_ms:str):
    timestamp_seconds = int(timestamp_ms) / 1000
    date_time = datetime.fromtimestamp(timestamp_seconds)
    formatted_datetime_str = date_time.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime_str

def assign_order_name(row):
    if row['orderType'] == 'Market' and row['side'] == 'Buy':
        if row['qty'] == form['values']['q_enter1']:
            return 'order_enter1'
        elif row['qty'] == form['values']['q_enter2']:
            return 'order_enter2'
        elif row['qty'] == form['values']['q8']:
            return 'order8'    
        elif row['qty'] == form['values']['q9']:
            return 'order9'      
        else:
            return 'man'
    elif row['orderType'] == 'Limit' and row['side'] == 'Sell':
        if row['qty'] == form['values']['q1']:
            return 'order1' 
        elif row['qty'] == form['values']['q3']:
            return 'order3'
        elif row['qty'] == form['values']['q4']:
            return 'order4'
        else:
            return 'man'
    elif row['orderType'] == 'Market' and row['side'] == 'Sell':
        if row['qty'] == form['values']['q5']: 
            return 'order5'    
        elif row['qty'] == form['values']['q10']: 
            return 'order10'
        elif row['qty'] == form['values']['q11']: 
            return 'order11'    
        else:
            return 'man'    
    else:
        return 'unknown'