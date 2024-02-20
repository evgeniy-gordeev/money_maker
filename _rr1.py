from pybit.unified_trading import HTTP
session = HTTP(
    testnet=False,
    api_key="5wH56z5gvRFfoNKVd6",
    api_secret="N4n1P6PG3E9mwhwysF4fSQPpBR2ZACOkdmA9",
)

from robot import Robot
r = Robot()

r.delete_all_orders()
r.create_order_11()
r.create_order_9()
bot.send_message(message.chat.id, "Закрыл все ордера✅\n Закрыл все позиции✅\n Закупил резервы✅")

while is_running:
    time.sleep(1)

    marketPrice = float(session.get_tickers(category="spot", symbol="BTCUSDC")['result']['list'][0]['ask1Price'])
    lastOrderPrice = float(session.get_executions(category='spot', symbol = 'BTCUSDC')['result']['list'][0]['execPrice'])

    if marketPrice - lastOrderPrice > 30:
        r.create_order_enter_2()
        if is_running:
            bot.send_message(message.chat.id, f"delta = {int(marketPrice - lastOrderPrice)} -> long")
            bot.send_message(message.chat.id, "Позиция открыта. Заврешаю работу")
        break
    elif marketPrice - lastOrderPrice < 30:
        if is_running:
            bot.send_message(message.chat.id, f"delta = {int(marketPrice - lastOrderPrice)} -> hold")
    elif lastOrderPrice - marketPrice < 100:
        if is_running:
            bot.send_message(message.chat.id, f"delta = {int(marketPrice - lastOrderPrice)} -> hold")
    else:
        metka = lastOrderPrice - 100
        with open('metka.txt', 'w') as file:
            file.write(str(metka))
        if is_running:
            bot.send_message(message.chat.id, f"created metka at {metka}. Завершаю работу")
        break