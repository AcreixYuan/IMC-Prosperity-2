'''
Author: Thvrudorv 114965005+0xAlston@users.noreply.github.com
Date: 2023-02-11 17:00:30
LastEditors: Thvrudorv 114965005+0xAlston@users.noreply.github.com
LastEditTime: 2023-02-11 17:01:13
FilePath: /algo trader/auto_trade_v1.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''

# we clear position at the mid-price for the given tick
# we entry position with a favor difference w.r.t the mid-price, i.e we buy mid_price-delta and sell mid_price+delta

from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np


class Trader:
    # data members
    position_limit = {'PEARLS': 20,'BANANA': 20}
    # member functions

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]
                # get current position of pearls
                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0
                # maximum number of the quote that won't exceed the position limit
                legal_bid = int(np.minimum(self.position_limit[product]-current_position, self.position_limit[product]))
                legal_ask = int(np.maximum(self.position_limit[product]+current_position, -self.position_limit[product]))
                # legal bid is positive
                # legal ask is negative

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                # Define a fair value for the PEARLS.
                fair_price = 10000
                delta = 1


                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders)>0 and len(order_depth.buy_orders)>0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = -order_depth.sell_orders[best_ask] # the original volumne in the orderbook is negative
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    fair_price = (best_ask*best_bid_volume+ best_bid*best_ask_volume)/(best_ask_volume+best_bid_volume)

                if current_position == 0:
                    orders.append(Order(product, legal_bid, fair_price-delta))
                    orders.append(Order(product, legal_ask, fair_price+delta))
                # we clear our position at the fair price
                # we entry long when it's lower anad entry short when it's higher

                if current_position > 0:
                    # we sell at the fair price
                    orders.append(Order(product, -current_position, fair_price))
                elif current_position < 0:
                    # we buy at the fair price
                    orders.append(Order(product, -current_position, fair_price))


                # Add all the above orders to the result dict
                result[product] = orders

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above
                print(result)
            self.report_log(state)
        return result
    
    def report_log(self, state: TradingState) -> None:
        """
        This function is called at the end of each trading day
        """
        print("At timestamp {}, the position is {}".format(state.timestamp, state.position))
        print("At timestamp {}, our trades in the last tick: {}".format(state.timestamp, state.own_trades))