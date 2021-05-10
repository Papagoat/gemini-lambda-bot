from utils.gemini import *
from utils.telegram_notification import telegram_notification


def new_order(
    key: str,
    price: int
):
    """logic to determine buy or sell order
        :key: type string - trading pair symbol
        :price: type integer - dollar amount to purchase
    """
    try:
        bought_transactions = get_redis_values("geminiState", "buy") or 0
        sold_transactions = get_redis_values("geminiState", "sell") or 0
    except Exception as e:
        print("Order Exception", e)

    if bought_transactions == 'True':
        order = create_order(
            key,
            price_feed(key),
            "buy",
            "gemini",
            price
        )
        print("BUY ORDER", order)
        if not order["is_cancelled"]:
            """ Set default values in Redis if order goes through
            :base_price: The price of first order
            :cash_balance: Cash balance in Gemini
            :btc_balance: BTC balance in Gemini
            :profit: BTC profit
            """
            notional_balance = get_notional_balance("USD", "BTC")
            my_trade_results = my_trades(key)[0]
            base_price = my_trade_results["price"]
            btc_balance = get_balances("BTC")
            cash_balance = get_balances("USD")
            dict = {
                "base_price": base_price,
                "btc_balance": btc_balance,
                "cash_balance": cash_balance,
                "notional_balance": notional_balance,
                "buy": int(bought_transactions) + 1,
                "sell": sold_transactions,
            }
            set_redis_values("geminiState", dict)
            print(f"{btc_balance} BTC bought at {base_price}")
            telegram_notification(f"{btc_balance} BTC bought at {base_price}")
            print(get_all_redis_values('geminiState'))
    else:
        """ Check price difference if there is more than 1 transaction
            Create a sell order if price increase by >= 0.1%
            Otherwise create a buy order if price dips by >= -0.1%
        """
        btc_balance = get_redis_values("geminiState", "btc_balance")
        price_difference = percent_change_1m(key)
        current_price = price_difference[0]
        percent_change = price_difference[1]

        notional_balance = get_notional_balance("USD", "BTC")
        redis_notional_balance = get_redis_values("geminiState", "notional_balance")
        
        if (notional_balance > (float(redis_notional_balance) * 1.05)):
            order = create_order(
                key,
                price_feed(key),
                "sell",
                "gemini",
                price
            )
            if not order["is_cancelled"]:
                cash_balance = get_balances("USD")
                profit = notional_balance - float(redis_notional_balance)
                executed_amount = order["executed_amount"]
                dict = {
                    "base_price": current_price,
                    "btc_balance": 0,
                    "profit": profit,
                    "cash_balance": cash_balance,
                    "notional_balance": 0,
                    "sell": int(sold_transactions) + 1,
                }
                set_redis_values("geminiState", dict)
                telegram_notification(f"{executed_amount} BTC sold at {current_price}. Profit: {profit}")

        elif percent_change <= -0.1 and get_balances("USD") >= price:
            order = create_order(
                key,
                price_feed(key),
                "buy",
                "gemini",
                price
            )
            if not order["is_cancelled"]:
                base_price = get_redis_values("geminiState", "base_price")
                btc_balance = get_balances("BTC")
                cash_balance = get_balances("USD")
                executed_amount = order["executed_amount"]
                notional_balance = get_notional_balance("USD", "BTC")
                dict = {
                    "base_price": (float(base_price) + float(current_price)) / 2,
                    "btc_balance": btc_balance,
                    "cash_balance": cash_balance,
                    "notional_balance": notional_balance,
                    "buy": int(bought_transactions) + 1,
                }
                set_redis_values("geminiState", dict)
                telegram_notification(f"{executed_amount} BTC bought at {current_price}")
        else:
            telegram_notification(f"Price did not reach target: {current_price}, {percent_change}")


def main(self, func):
    try:
        new_order("BTCUSD", 10)
    except Exception as e:
        print("Main Exception", e)
