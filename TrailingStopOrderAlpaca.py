from alpaca.trading.client import TradingClient
import keyring as kr
from alpaca.trading.requests import TrailingStopOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import json
import requests
import time
import schedule

APCA_API_BASE_URL = 'https://paper-api.alpaca.markets'
APCA_API_KEY_ID = kr.get_password("AlpacaKEY", "drcook6611")
APCA_API_SECRET_KEY = kr.get_password("AlpacaSecret", "drcook6611")

trading_client = TradingClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY)
account = trading_client.get_account()

def runner():
    if account.trading_blocked:
        print('Account is currently restricted from trading.')
        return

    print('${} is available as buying power.'.format(account.buying_power))

    symbol = 'AAL240614P00011500'

    limit_order_data = LimitOrderRequest(
        symbol=symbol,
        qty=1,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY,
        limit_price=29,
    )

    # Limit order
    limit_order = trading_client.submit_order(
        order_data=limit_order_data
    )

    price = limit_order.filled_avg_price
    if price is None:
        price = 0.25

    highest_price = price

    while True:
        url = f"https://data.alpaca.markets/v1beta1/options/quotes/latest?symbols={symbol}&feed=indicative"

        headers = {
            "accept": "application/json",
            "APCA-API-KEY-ID": APCA_API_KEY_ID,
            "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
        }

        response = requests.get(url, headers=headers)
        data = json.loads(response.content.decode('utf-8'))
        current_bid = data.get('quotes', {}).get(symbol, {}).get('bp')

        if current_bid is None:
            print("Unable to fetch current bid price.")
            break

        highest_price = max(highest_price, current_bid)

        if ((highest_price - current_bid) / highest_price) >= 0.15:
            break

        print('Checking Price -', end='\r')
        time.sleep(1)
        print('Checking Price |', end='\r')
        time.sleep(1)

schedule.every().day.at("08:30").do(runner)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        print('Waiting for 08:30 -', end='\r')
        time.sleep(1)
        print('Waiting for 08:30 |', end='\r')
        time.sleep(1)