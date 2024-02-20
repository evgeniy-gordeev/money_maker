from pybit.unified_trading import HTTP
from utils import calculate_timestamp, from_timestamp

session = HTTP(
    testnet=False,
    api_key="5wH56z5gvRFfoNKVd6",
    api_secret="N4n1P6PG3E9mwhwysF4fSQPpBR2ZACOkdmA9",
)

session.cancel_all_orders(
    category="spot",
    symbol="BTCUSDC",
    orderFilter = 'StopOrder'
    )