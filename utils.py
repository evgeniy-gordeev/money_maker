from datetime import datetime
import pandas as pd
from pybit.unified_trading import HTTP
import yaml

session = HTTP(
    testnet=False,
    api_key="5wH56z5gvRFfoNKVd6",
    api_secret="N4n1P6PG3E9mwhwysF4fSQPpBR2ZACOkdmA9",
)

def write_df_to_excel(df, excel_file):

    #if the Excel file exists append your DataFrame to it
    try: 
        existing_df = pd.read_excel(excel_file)
        with pd.ExcelWriter(excel_file, mode='a', engine='openpyxl', if_sheet_exists = 'overlay') as writer:
            df.to_excel(writer, index=False, header=False, startrow=len(existing_df) + 1)
    except FileNotFoundError: 
        df.to_excel(excel_file, index=False)

def calculate_timestamp(start_date_str:str):

    # Create a datetime object for February 10, 2024
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")

    # Convert datetime object to timestamp
    timestamp = start_date.timestamp()*1000

    return timestamp

def from_timestamp(timestamp_ms:str):

    # Convert milliseconds to seconds
    timestamp_seconds = int(timestamp_ms) / 1000

    # Convert timestamp to datetime object
    date_time = datetime.fromtimestamp(timestamp_seconds)
    
    # Format datetime object without milliseconds
    formatted_datetime_str = date_time.strftime("%Y-%m-%d %H:%M:%S")
    
    return formatted_datetime_str


def delete_all_orders():

    open_orders = session.get_open_orders(
        category="spot", symbol="BTCUSDC"
        )['result']['list']
    n_open_orders = len(open_orders)

    session.cancel_all_orders(
        category="spot",
        symbol="BTCUSDC",
        orderFilter = 'StopOrder'
        )
    
    print(f'--deleted {n_open_orders} orders')

