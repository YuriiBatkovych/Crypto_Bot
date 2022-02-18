import urllib3
import time
from BTC import BTC


class Order:

    def __init__(self, _id, _type, _currency1, _currency2, _amount1, _price):
        self.id = _id
        self.type = _type  # 'buy' or 'sell'
        self.currency1 = _currency1
        self.currency2 = _currency2
        self.amount1 = _amount1
        self.price = _price

    def display(self):
        print("order_id = " + str(
            self.id) + ", type = " + self.type + ", market - " + self.currency1 + "_" + self.currency2 + \
              ", amount1 = " + str(self.amount1) + ", price = " + str(self.price))


class BOT:

    def __init__(self):
        self.orders = []
        self.LastOperationPrice = 1

        self.critic_low_to_buy = 0
        self.critic_high_to_buy = 0
        self.critic_low_to_sell = 0
        self.critic_high_to_sell = 0

        self.BTC_object = BTC()

        self.isNextOperationToBuy = False
        self.market = 'ltc_uah'

    def getMarketPrice(self):
        info = self.BTC_object.get_prices(market=self.market)
        if self.isNextOperationToBuy:
            return info[self.market]['buy']
        else:
            return info[self.market]['sell']

    def mybalance(self, currency):
        info = self.BTC_object.get_balance()
        for i in info['accounts']:
            if i['currency'] == currency:
                return float(i['balance'])

    def buy_exists(self):
        for i in self.orders:
            if i.type == 'buy':
                return i
        return None

    def sell_exists(self):
        for i in self.orders:
            if i.type == 'sell':
                return i
        return None

    def get_status(self, order_id):
        info = self.BTC_object.check_order_status(order_id=order_id)
        print(info)
        if info['status'] == 'processing':
            return True
        else:
            return False

    def tryToBuy(self, percentage_diff, price):
        if percentage_diff > self.critic_high_to_buy or percentage_diff < self.critic_low_to_buy:
            buy_order = self.buy_exists()
            if (buy_order is not None) and (self.get_status(buy_order.id)):
                info = self.BTC_object.order_move(order_id=buy_order.id, new_price=price)
                if info['status'] is not True:
                    print("Error :", end=' ')
                    print(info)
                else:
                    buy_order.price = price
                    self.LastOperationPrice = price
            else:
                if buy_order is not None:
                    self.orders.remove(buy_order)
                amount = self.mybalance('LTC') / 2
                info = self.BTC_object.buy(amount, price, self.market)
                print(info)
                if info['status'] is True:
                    new_order = Order(info['order_id'], 'buy', 'LTC', 'UAH', amount, price * amount)
                    self.orders.append(new_order)
                    self.LastOperationPrice = price
                else:
                    print("Error :", end=' ')
                    print(info)

        self.isNextOperationToBuy = False

    def tryToSell(self, percentage_diff, price):
        if percentage_diff > self.critic_high_to_sell or percentage_diff < self.critic_low_to_sell:
            sell_order = self.sell_exists()
            if (sell_order is not None) and (self.get_status(sell_order.id)):
                info = self.BTC_object.order_move(order_id=sell_order.id, new_price=price)
                if info['status'] is not True:
                    print("Error :", end=' ')
                    print(info)
                else:
                    sell_order.price = price
                    self.LastOperationPrice = price
            else:
                if sell_order is not None:
                    self.orders.remove(sell_order)
                amount = self.mybalance('LTC') / 2
                info = self.BTC_object.sell(amount, price, self.market)
                print(info)
                if info['status'] is True:
                    new_order = Order(info['order_id'], 'sell', 'LTC', 'UAH', amount, price * amount)
                    self.orders.append(new_order)
                    self.LastOperationPrice = price
                else:
                    print("Error :", end=' ')
                    print(info)
        self.isNextOperationToBuy = True

    def attemptToMakeTrade(self):
        current_price = float(self.getMarketPrice())
        percentage_diff = ((current_price - self.LastOperationPrice) / self.LastOperationPrice) * 100
        print(percentage_diff)

        if self.isNextOperationToBuy:
            self.tryToBuy(percentage_diff, current_price)
        else:
            self.tryToSell(percentage_diff, current_price)

    def make_money(self):
        while True:
            self.attemptToMakeTrade()
            time.sleep(30)


if __name__ == '__main__':
    # bo wyskakuje nepotribnyj do holery welykyj worning :
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    bot = BOT()
    BOT.make_money()