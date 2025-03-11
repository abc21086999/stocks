import time
import twstock


previous_price = None

while True:
    stock = twstock.realtime.get("00878")
    name = stock.get('info').get("name")
    price_now = stock.get('realtime').get('latest_trade_price')

    # 第一次進來
    if previous_price is None and price_now != "-":
        previous_price = price_now
        print(name, price_now)
    # 第二次開始
    else:
        if price_now != "-" and previous_price != "-" and previous_price != price_now:
            print(name, price_now)
            previous_price = price_now
    time.sleep(5)