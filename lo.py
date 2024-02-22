from pybit.unified_trading import HTTP
from utils import calculate_timestamp, from_timestamp
from requests.exceptions import ConnectionError
session = HTTP(
    testnet=False,
    api_key="5wH56z5gvRFfoNKVd6",
    api_secret="N4n1P6PG3E9mwhwysF4fSQPpBR2ZACOkdmA9",
)

from robot import Robot
r = Robot()
id = r.create_order_enter_2()
print(id)