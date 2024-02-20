from pybit.unified_trading import HTTP
from utils import calculate_timestamp, from_timestamp

session = HTTP(
    testnet=False,
    api_key="5wH56z5gvRFfoNKVd6",
    api_secret="N4n1P6PG3E9mwhwysF4fSQPpBR2ZACOkdmA9",
)

open_orders_ = session.get_executions(category = 'spot',symbol = 'BTCUSDC')['result']['list'][:2]

import pandas as pd
fr_ = pd.DataFrame.from_records(open_orders_)[['execValue']].astype(float)
pnl_abs = fr_.loc[0] - fr_.loc[1]
pnl_abs = round(pnl_abs.values[0], 4)
print(pnl_abs)