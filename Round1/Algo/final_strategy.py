# score 2.639k
# quick description: we are using the ema for the am, and we are using an 90 10 split for the parameters, varying the N parameter to 20 
# market status added for both, one at 2, one at 1

alpha1 = 1.0;alpha2 =  0.1; N1 = 7; N2 = 30

from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState, UserId, Position, Product
from typing import List, Dict, Any
import numpy as np
import jsonpickle
from collections import deque

# import parameter_list

class Trader:
    # define data members
    def __init__(self):
        self.position_limit = {"AMETHYSTS": 20, "STARFRUIT": 20}
        self.last_mid_price = {'AMETHYSTS': 10000, 'STARFRUIT': 5000}
        self.mid_price = {'AMETHYSTS': {0: 10000}, 'STARFRUIT': {0: 5000}}
        self.ma_price = {'AMETHYSTS': {0: 10000}, 'STARFRUIT': {0: 5000}}
        self.ema_price = {'AMETHYSTS': {0: 10000}, 'STARFRUIT': {0: 5000}}
        self.price_history = {'AMETHYSTS': deque(maxlen=20), 'STARFRUIT': deque(maxlen=20)}  # 设置历史长度为 20

    def market_status(self, state: TradingState, product) -> int:
        order_depth: OrderDepth = state.order_depths[product]
        if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
            best_ask_volume = order_depth.sell_orders[min(order_depth.sell_orders.keys())]
            best_bid_volume = order_depth.buy_orders[max(order_depth.buy_orders.keys())]
            if best_ask_volume >= 15 and best_bid_volume <15:
                return -1
            elif best_ask_volume < 15 and best_bid_volume >=15:
                return 1
            else:
                return 0
            
    def simple_moving_average(self, product, price):
        self.price_history[product].append(price)
        if len(self.price_history[product]) > 0:
            return sum(self.price_history[product]) / len(self.price_history[product])
        return price

    def run(self, state: TradingState) -> tuple[dict[Symbol, list[Order]], int, str]: 
        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
            order_depth: OrderDepth = state.order_depths[product]

            if product in state.position.keys():
                current_position = state.position[product]
            else:
                current_position = 0

            legal_buy_vol = np.minimum(self.position_limit[product] - current_position, self.position_limit[product])
            legal_sell_vol = np.maximum(-(self.position_limit[product] + current_position), -self.position_limit[product])

            orders: List[Order] = []
            if product == 'AMETHYSTS':
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                mid_price = (best_ask * np.abs(best_ask_volume) + best_bid * np.abs(best_bid_volume)) / (np.abs(best_ask_volume) + np.abs(best_bid_volume))
                ma_price = self.simple_moving_average(product, mid_price)
                ema_price = (2 * mid_price + (N1 - 1) * self.ema_price[product][list(self.ema_price[product].keys())[-1]]) / (N1 + 1)
                self.mid_price[product][state.timestamp] = mid_price
                self.ma_price[product][state.timestamp] = ma_price
                self.ema_price[product][state.timestamp] = ema_price

                # market status
                market_status = self.market_status(state, product)

                acceptable_price = ema_price + 2 * market_status
                
            elif product == 'STARFRUIT':
                if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    avg_buy_price = sum([np.abs(order_depth.buy_orders[i]) * i for i in order_depth.buy_orders.keys()])/sum([np.abs(order_depth.buy_orders[i]) for i in order_depth.buy_orders.keys()])
                    avg_sell_price = sum([np.abs(order_depth.sell_orders[i]) * i for i in order_depth.sell_orders.keys()])/sum([np.abs(order_depth.sell_orders[i]) for i in order_depth.sell_orders.keys()])
                    mid_price = (avg_sell_price + avg_buy_price)/2
                    ma_price = self.simple_moving_average(product, mid_price)
                    ema_price = (2 * mid_price + (N2 - 1) * self.ema_price[product][list(self.ema_price[product].keys())[-1]]) / (N2 + 1)
                    self.ma_price[product][state.timestamp] = ma_price
                    self.ema_price[product][state.timestamp] = ema_price
                else:
                    mid_price = self.last_mid_price[product]
                self.last_mid_price[product] = mid_price
                acceptable_price = alpha2 * ema_price + (1 - alpha2)*mid_price + market_status

            if len(order_depth.sell_orders) > 0:
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                if best_ask <= acceptable_price:
                    print("BUY", str(-best_ask_volume) + "x", best_ask)
                    orders.append(Order(product, best_ask, int(np.minimum(-best_ask_volume, legal_buy_vol))))
                if best_bid + 1 <= acceptable_price:
                    print("BUY", str(-best_ask_volume) + "x", best_bid + 1)
                    orders.append(Order(product, best_bid + 1, int(np.minimum(-best_ask_volume, legal_buy_vol))))

            if len(order_depth.buy_orders) != 0:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                if best_bid >= acceptable_price:
                    print("SELL", str(best_bid_volume) + "x", best_bid)
                    orders.append(Order(product, best_bid, int(np.maximum(-best_bid_volume, legal_sell_vol))))
                if best_ask - 1 >= acceptable_price:
                    print("SELL", str(-best_bid_volume) + "x", best_ask - 1)
                    orders.append(Order(product, best_ask - 1, int(np.minimum(-best_bid_volume, legal_sell_vol))))

            result[product] = orders

        # String value holding Trader state data required.
        # It will be delivered as TradingState.traderData on next execution.
        traderData = "SAMPLE"

        conversions = 1

        return result, conversions, traderData
