'''
Author: Thvrudorv 114965005+0xAlston@users.noreply.github.com
Date: 2023-02-11 17:00:30
LastEditors: Thvrudorv 114965005+0xAlston@users.noreply.github.com
LastEditTime: 2023-02-11 17:01:13
FilePath: /algo trader/auto_trade_v1.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''


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
                legal_bid = int(np.minimum(self.position_limit[product]-current_position, self.position_limit[product]))
                legal_ask = int(np.maximum(self.position_limit[product]+current_position, -self.position_limit[product]))

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                # Define a fair value for the PEARLS.
                acceptable_price_to_bid = 9998 # 9998 is the higheest price we would like to bid
                acceptable_price_to_ask = 10002 # 10002 is the lowest price we would like to ask

                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:

                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]

                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    if best_ask < acceptable_price_to_bid:

                        print("BUY", str(-best_ask_volume) + "x", int(np.minimum(best_ask, legal_bid)))
                        orders.append(Order(product, best_ask, -best_ask_volume))
                else:
                    print("BUY", str(-best_ask_volume) + "x", legal_bid)
                    orders.append(Order(product, acceptable_price_to_bid, legal_bid))

                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    # it's not possible that best_bid = 9995 higher than acceptable_price_ask, so we only 
                    # use the block to avoid extreme situation in live trading
                    if best_bid > acceptable_price_to_ask:
                        print("SELL", str(best_bid_volume) + "x", best_bid)
                        orders.append(Order(product, best_bid, int(np.maximum(-best_bid_volume,legal_ask))))
                else:
                    print("SELL", str(best_bid_volume) + "x", int(np.maximum(best_bid, legal_ask)))
                    orders.append(Order(product, acceptable_price_to_ask, legal_ask))

                # Add all the above orders to the result dict
                result[product] = orders

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above
        return result
