#score 2.420
#quick description: we are using the ema for the am, and we are using an 90 10 split for the parameters, varying the N parameter to 20 
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState, UserId, Position, Product
from typing import List, Dict, Any
import numpy as np
import jsonpickle

class Trader:
    # define data members
    def __init__(self):
        self.position_limit = {"AMETHYSTS": 20, "STARFRUIT": 20}
        self.last_mid_price = {'AMETHYSTS': 10000, 'STARFRUIT': 5000}
        self.mid_price = {'AMETHYSTS': {0: 10000}, 'STARFRUIT': {0: 5000}}
        self.ema_price = {'AMETHYSTS': {0: 10000}, 'STARFRUIT': {0: 5000}}

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
            N = 30
            if product == 'AMETHYSTS':    
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                mid_price = (best_ask * np.abs(best_ask_volume) + best_bid * np.abs(best_bid_volume)) / (np.abs(best_ask_volume) + np.abs(best_bid_volume))
                ema_price = (2 * mid_price + (N - 1) * self.ema_price[product][list(self.ema_price[product].keys())[-1]]) / (N + 1)
                self.mid_price[product][state.timestamp] = mid_price
                self.ema_price[product][state.timestamp] = ema_price
                acceptable_price = ema_price
            elif product == 'STARFRUIT':
                if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    avg_buy_price = sum([np.abs(order_depth.buy_orders[i]) * i for i in order_depth.buy_orders.keys()])/sum([np.abs(order_depth.buy_orders[i]) for i in order_depth.buy_orders.keys()])
                    avg_sell_price = sum([np.abs(order_depth.sell_orders[i]) * i for i in order_depth.sell_orders.keys()])/sum([np.abs(order_depth.sell_orders[i]) for i in order_depth.sell_orders.keys()])
                    mid_price = (avg_sell_price + avg_buy_price)/2
                    ema_price = (2 * mid_price + (N - 1) * self.ema_price[product][list(self.ema_price[product].keys())[-1]]) / (N + 1)
                    self.ema_price[product][state.timestamp] = ema_price
                else:
                    mid_price = self.last_mid_price[product]
                self.last_mid_price[product] = mid_price
                acceptable_price = 0.1 * ema_price + 0.9*mid_price
            
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
