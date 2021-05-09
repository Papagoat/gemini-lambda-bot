from datetime import datetime
from decimal import *

import base64
import hashlib
import hmac
import json
import redis
import requests
import time

from utils.get_secrets import get_secrets

base_url = "https://api.gemini.com"
gemini_api_key = get_secrets("GEMINI-AWS")["GEMINI_API_KEY"]
gemini_api_secret = get_secrets("GEMINI-AWS")["GEMINI_API_SECRET"].encode()
redis_endpoint = get_secrets("GEMINI-AWS")["REDIS_ENDPOINT"]

r = redis.StrictRedis(
        host=redis_endpoint,
        port=6379,
        db=0,
        charset="utf-8",
        decode_responses=True
    )


def flushall():
    r.flushall()


def prettify_json(
    val,
    indent=4
):
    return json.dumps(
        val,
        indent=indent
    )


def set_redis_values(
    name,
    dict
):
    set_values = r.hset(
        name,
        mapping=dict
    )
    return set_values


def get_redis_values(
    name,
    key
):
    get_values = r.hmget(
        name,
        key
    )
    return get_values[0]


def get_all_redis_values(dict):
    """get redis default values to be used across application
    :dict: name of dictionary
    """
    get_all_values = r.hgetall(dict)
    return get_all_values


def get_nonce():
    # function to generate nonce. Required for payload
    t = datetime.now()
    payload_nonce = str(int(time.mktime(t.timetuple())*1000))
    return payload_nonce


def request_headers(
    payload: object,
    url: str
):
    """request headers for api
        :payload: type object - request payload
        :url: type string -  request url path
    """
    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(
        gemini_api_secret,
        b64,
        hashlib.sha384
    ).hexdigest()
    request_headers = {
            "Content-Type": "text/plain",
            "Content-Length": "0",
            "X-GEMINI-APIKEY": gemini_api_key,
            "X-GEMINI-PAYLOAD": b64,
            "X-GEMINI-SIGNATURE": signature,
            "Cache-Control": "no-cache"
            }
    return requests.post(
        url,
        headers=request_headers
    )


def my_trades(
    key: str,
    limit: int = 1
):
    """get past trades
        :key: type string - trading pair symbol
        :limit: type integer - the maximum number of trades to return.
        Default is 50, max is 500.
    """
    url = f"{base_url}/v1/mytrades"
    payload = {
        "request": "/v1/mytrades",
        "nonce": get_nonce(),
        "symbol": key,
        "limit_trades": limit
    }
    response = request_headers(
        payload,
        url
    )
    my_trades = response.json()
    return my_trades


def get_balances(
    key,
    val1="currency",
    val2="amount"
):
    """get account balance
        :key: type string - crypto symbol
    """
    url = f"{base_url}/v1/balances"
    payload = {
        "request": "/v1/balances",
        "nonce": get_nonce()
    }
    response = request_headers(payload, url)
    balances = response.json()
    return float([balance for balance in balances if balance[val1] == key][0][val2])


def price_feed(
    key: str
):
    """get current crypto price
        :key: type string - trading pair symbol
    """
    try:
        url = base_url
        response = requests.get(f"{url}/v1/pricefeed")
        price_feed = response.json()
        price = [price for price in price_feed if price["pair"] == key][0]["price"]
        return float(price)
    except Exception as e:
        print("Price Feed Exception ", e)


def order_status(order_id: str):
    """get status of order
    :order_id: type string - id of transaction
    """
    try:
        url = f"{base_url}/v1/order/status"
        payload = {
            "request": "/v1/order/status",
            "nonce": get_nonce(),
            "order_id": order_id,
            "include_trades": True
        }
        response = request_headers(payload, url)
        order_details = response.json()
        return order_details
    except Exception as e:
        print("Order Status Exception", e)


def ticker_info(
    key: str,
    type: str
):
    """get recent trading activity for key pair
        :key: type string - crypto key pair
    """
    try:
        url = base_url
        response = requests.get(f"{url}/v1/pubticker/{key}")
        return float(response.json()[type])
    except Exception as e:
        print("Ticker Info Exception ", e)


def get_notional_balance(
    key: str,
    currency: str,
    val1="currency",
    val2="amountNotional"
):
    """get notional amount for currency
        :key: type string - currency key
    """
    try:
        url = f"{base_url}/v1/notionalbalances/{key}"
        payload = {
            "request": f"/v1/notionalbalances/{key}",
            "nonce": get_nonce(),
        }
        response = request_headers(payload, url)
        notional_balance = response.json()
        return float([amount for amount in notional_balance if amount[val1] == currency][0][val2])
    except Exception as e:
        print("Notional Balance Exception ", e)


def percent_change_1m(
    key: str
):
    """logic to calculate price difference in percentages
        :key: type string - trading pair symbol
    """
    try:
        base_price = float(get_redis_values("geminiState", "base_price"))
        current_price = price_feed(key)
        percent_change_1m = float(round((current_price - base_price) / current_price * 100, 4))
        return current_price, percent_change_1m
    except Exception as e:
        print("Percent Change Exception", e)


def create_order(
    key: str,
    price: int,
    side: str,
    client_order_id: str,
    dollar_cost: int,
    currency: str = "BTC"
):
    """create buy or sell order
        :key: type string - trading pair symbol
        :price: type integer - quoted decimal amount to spend per unit
        :side: type string - buy or sell
        :client_order_id: type string - custom id for transaction
        :dollar_cost: type integer - quoted dollar amount to spend
        :currency: type string - crypto key
    """
    url = f"{base_url}/v1/order/new"
    getcontext().prec = 10
    amount = 1/price * float(dollar_cost) if side == 'buy' else get_balances(currency)
    amount = Decimal(amount)

    payload = {
        "request": "/v1/order/new",
        "nonce": get_nonce(),
        "client_order_id": client_order_id,
        "symbol": key,
        "amount": str(round(amount, 6)),
        "price": str(price),
        "side": side,
        "type": "exchange limit",
        "options": ["fill-or-kill"]
    }
    response = request_headers(payload, url)
    order = response.json()
    return order
