import requests
import hashlib
import urllib
import time
from config import private_key, public_key
import random
from datetime import datetime, timedelta


class BTC:
    API_URL_V1 = "https://btc-trade.com.ua/api/"
    BASE = "https://btc-trade.com.ua/"

    def __init__(self):
        self.__end_points = {}
        self.__nonce = int(time.time() * 1000)
        self.__private_key = private_key
        self.__public_key = public_key

        self.__generate_end_points()

    def increment_nonce(self):
        self.__nonce = self.__nonce + 1

    @staticmethod
    def make_api_sign(private, body):
        m = hashlib.sha256()
        line = body + private
        m.update(line.encode('utf-8'))
        return m.hexdigest()

    def __post_request(self, url, payload=None):

        custom_headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "public_key": self.__public_key,
            "api_sign":
                BTC.make_api_sign(self.__private_key, payload)
        }

        result = requests.post(url, data=payload, headers=custom_headers, verify=False)

        try:
            return result.json()
        except:
            print(result.text)
            raise Exception("Bad status response")

    @staticmethod
    def random_order():
        Val = "randm" + str(random.randrange(1, 1000000000000000000))
        m = hashlib.sha256()
        m.update(Val.encode('utf-8'))
        return m.hexdigest()

    def get_balance(self, out_order_id=None):
        if out_order_id is None:
            out_order_id = BTC.random_order()
        url = self.__end_points["balance"]
        params = {"out_order_id": out_order_id, "nonce": self.__nonce}
        raw_data = urllib.parse.urlencode(params)
        result = self.__post_request(url, raw_data)
        self.increment_nonce()
        return result

    def sell(self, amount, price, market, out_order_id=None):
        if out_order_id is None:
            out_order_id = BTC.random_order()

        url = self.__end_points["sell"] + market
        params = {"out_order_id": out_order_id, "nonce": self.__nonce, "count": amount, "price": price}
        raw_data = urllib.parse.urlencode(params)
        result = self.__post_request(url, raw_data)
        self.increment_nonce()
        return result

    def buy(self, amount, price, market="btc_uah", out_order_id=None):
        if out_order_id is None:
            out_order_id = BTC.random_order()

        url = self.__end_points["buy"] + market
        params = {"out_order_id": out_order_id, "nonce": self.__nonce, "count": amount, "price": price}
        raw_data = urllib.parse.urlencode(params)
        result = self.__post_request(url, raw_data)
        self.increment_nonce()
        return result

    def my_orders(self, market_name, out_order_id=None):
        if out_order_id is None:
            out_order_id = BTC.random_order()

        url = self.__end_points["my_orders"] + market_name
        params = {"out_order_id": out_order_id, "nonce": self.__nonce}
        raw_data = urllib.parse.urlencode(params)
        result = self.__post_request(url, raw_data)
        self.increment_nonce()
        return result

    @staticmethod
    def check_zero(month):
        if len(month) < 2:
            month = '0' + month
        return month

    def my_deals(self, market="btc_uah", start_date='', end_date='', out_order_id=None):
        if out_order_id is None:
            out_order_id = BTC.random_order()

        if start_date == '' or end_date == '':
            now = datetime.now()

            end_date = str(now.year) + '-' + BTC.check_zero(str(now.month)) \
                       + '-' + BTC.check_zero(str(now.day))

            start = now - timedelta(days=13)

            start_date = str(start.year) + '-' + BTC.check_zero(str(start.month)) \
                         + '-' + BTC.check_zero(str(start.day))

        url = self.__end_points["my_deals"] + market
        params = {"out_order_id": out_order_id, "nonce": self.__nonce, "ts": start_date, "ts1": end_date}
        raw_data = urllib.parse.urlencode(params)
        result = self.__post_request(url, raw_data)
        self.increment_nonce()
        return result

    def order_remove(self, order_id, out_order_id=None):
        if out_order_id is None:
            out_order_id = BTC.random_order()

        url = self.__end_points["remove"] + str(order_id)
        params = {"out_order_id": out_order_id, "nonce": self.__nonce}
        raw_data = urllib.parse.urlencode(params)
        result = self.__post_request(url, raw_data)
        self.increment_nonce()
        return result

    def order_move(self, order_id, new_price, out_order_id=None):
        if out_order_id is None:
            out_order_id = BTC.random_order()

        url = self.__end_points["move"] + str(order_id) + "/" + new_price
        params = {"out_order_id": out_order_id, "nonce": self.__nonce}
        raw_data = urllib.parse.urlencode(params)
        result = self.__post_request(url, raw_data)
        self.increment_nonce()
        return result

    def check_order_status(self, order_id, out_order_id=None):
        if out_order_id is None:
            out_order_id = BTC.random_order()

        url = self.__end_points["status"] + str(order_id)
        params = {"out_order_id": out_order_id, "nonce": self.__nonce}
        raw_data = urllib.parse.urlencode(params)
        result = self.__post_request(url, raw_data)
        self.increment_nonce()
        return result

    @staticmethod
    def get_prices(market=''):
        url = 'https://btc-trade.com.ua/api/ticker'
        if market != '':
            url += '/' + market
        result = requests.get(url)
        return result.json()

    def check_buy_cost(self, market="ltc_uah", amount=1):
        url = self.__end_points["ask"] + market + "?is_api=1&amount=" + str(amount)
        result = requests.get(url)
        return result.json()

    def check_sell_cost(self, market="ltc_uah", amount=1):
        url = self.__end_points["bid"] + market + "?is_api=1&amount=" + str(amount)
        result = requests.get(url)
        return result.json()

    def __generate_end_points(self):
        self.__end_points["auth"] = BTC.API_URL_V1 + "auth"
        self.__end_points["sell_list"] = BTC.API_URL_V1 + "trades/sell/"
        self.__end_points["buy_list"] = BTC.API_URL_V1 + "trades/buy/"
        self.__end_points["ask"] = BTC.API_URL_V1 + "ask/"
        self.__end_points["bid"] = BTC.API_URL_V1 + "bid/"
        self.__end_points["buy"] = BTC.API_URL_V1 + "buy/"
        self.__end_points["sell"] = BTC.API_URL_V1 + "sell/"
        self.__end_points["remove"] = BTC.API_URL_V1 + "remove/order/"
        self.__end_points["move"] = BTC.API_URL_V1 + "move/order/"

        self.__end_points["status"] = BTC.API_URL_V1 + "order/status/"
        self.__end_points["deals"] = BTC.API_URL_V1 + "deals"
        self.__end_points["my_deals"] = BTC.API_URL_V1 + "my_deals/"
        self.__end_points["my_orders"] = BTC.API_URL_V1 + "my_orders/"
        self.__end_points["balance"] = BTC.API_URL_V1 + "balance"
        self.__end_points["markets"] = BTC.API_URL_V1 + "market_prices"
        self.__end_points["checkout"] = BTC.BASE + "checkout/invoice"
        self.__end_points["checkout_status"] = BTC.BASE + "checkout/status"
        self.__end_points["checkout_send"] = BTC.BASE + "checkout/send"
        self.__end_points["send_status"] = BTC.BASE + "checkout/send/status"
        self.__end_points["address"] = BTC.BASE + "finance/crypto_currency/"
