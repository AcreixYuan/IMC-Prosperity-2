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

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                # Define a fair value for the PEARLS.
                # Note that this value of 1 is just a dummy value, you should likely change it!
                profitable_price_bid = 9998
                profitable_price_ask = 10002

                # read current position
                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0
    
                legal_bid_volume = int(np.minimum(self.position_limit[product]-current_position,self.position_limit[product]))
                legal_ask_volume = int(np.maximum(self.position_limit[product]+current_position,-self.position_limit[product]))

                # static two way quote with 
                orders.append(Order(product, profitable_price_bid, legal_bid_volume))
                orders.append(Order(product, profitable_price_ask, legal_ask_volume))
                # Add all the above orders to the result dict
                result[product] = orders

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above
        return result
    

    

