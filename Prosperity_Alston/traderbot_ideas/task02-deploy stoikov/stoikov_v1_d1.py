from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np


class Trader:
    # define data members
    def __init__(self):
        self.last_mid_price = 10000
        self.position_limit = {"PEARLS": 20, "BANANAS": 10}

    def stoikov_finite(product_symbol:str, cur_pos:int, mid_price:float,timestamp:int, gamma=0.1):
        sigma_param = {"PEARLS": 1.5, "BANANAS": 5.5}
        sigma = sigma_param[product_symbol]
        time_interval = ((199900-timestamp)/100)/2000
        return mid_price-cur_pos*gamma*sigma**2*time_interval
        

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order dephts
        for product in state.order_depths.keys():

            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # quote volume limit
                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0
                legal_buy_vol = np.minimum(self.position_limit[product] - current_position,self.position_limit[product])
                legal_sell_vol = np.maximum(-(self.position_limit[product] + current_position),-self.position_limit[product])


                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                # Calculate the mid price of the PEARLS market
                mid_price = 10000
                if len(order_depth.buy_orders) != 0 and len(order_depth.sell_orders) != 0:
                    mid_price = (max(order_depth.buy_orders.keys()) + min(order_depth.sell_orders.keys())) / 2
                else:
                    mid_price = self.last_mid_price
                # memorize the mid price
                self.last_mid_price = mid_price

                # Define a fair value for the PEARLS based on stoikov_finite
                print("mid_price", mid_price)
                print("current_position", current_position)
                print("timestamp", state.timestamp)
                print("product", product)
                #acceptable_price = self.stoikov_finite(product, current_position, mid_price, state.timestamp)
                acceptable_price = 10000

                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:

                    # Sort all the available sell orders by their price,
                    # and select only the sell order with the lowest price
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]

                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    if best_ask < acceptable_price:

                        # In case the lowest ask is lower than our fair value,
                        # This presents an opportunity for us to buy cheaply
                        # The code below therefore sends a BUY order at the price level of the ask,
                        # with the same quantity
                        # We expect this order to trade with the sell order
                        print("BUY", str(-best_ask_volume) + "x", best_ask)
                        orders.append(Order(product, best_ask, int(np.minimum(-best_ask_volume,legal_buy_vol))))

                # The below code block is similar to the one above,
                # the difference is that it find the highest bid (buy order)
                # If the price of the order is higher than the fair value
                # This is an opportunity to sell at a premium
                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid > acceptable_price:
                        print("SELL", str(best_bid_volume) + "x", best_bid)
                        orders.append(Order(product, best_bid, int(np.maximum(-best_bid_volume,legal_sell_vol))))

                # Add all the above the orders to the result dict
                result[product] = orders

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above
        
        return result