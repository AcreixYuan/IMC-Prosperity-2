from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np

# PEARLS strategy: 
# fair_price = EMA(weighted mid price,20) 


class Trader:
    # define data members
    def __init__(self):
        self.position_limit = {"PEARLS": 20, "BANANAS": 20}
        self.last_mid_price = {'PEARLS': 10000, 'BANANAS': 5000}
        self.last_ema_price = {'PEARLS': 10000, 'BANANAS': 5000}



    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        
        # Initialize the method output dict as an empty dict
        result = {}
        # Iterate over all the keys (the available products) contained in the order dephts
        for product in state.order_depths.keys():
            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':
                # 算仓位信息，和 orderbook 无关
                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0
                legal_buy_vol = min(self.position_limit[product] - current_position,self.position_limit[product])
                legal_sell_vol = max(-(self.position_limit[product] + current_position),-self.position_limit[product])
               
                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]
                # Calculate the fair price based on the order depth
                if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask] # <=0
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid] # >=0
                    avg_buy_price = sum([order_depth.buy_orders[i] * i for i in order_depth.buy_orders.keys()])/sum([order_depth.buy_orders[i] for i in order_depth.buy_orders.keys()])
                    avg_sell_price = sum([-order_depth.sell_orders[i] * i for i in order_depth.sell_orders.keys()])/sum([-order_depth.sell_orders[i] for i in order_depth.sell_orders.keys()])
                    # calcualte midprice
                    mid_price = (avg_sell_price + avg_buy_price)/2
  
                else:
                    mid_price = self.last_mid_price[product]
                    # expected_movement = self.expected_movement[product]
                self.last_mid_price[product] = mid_price
                # self.expected_movement[product] = expected_movement

                # market status
                # market_status = self.market_status(state, product)
                # factor: volume imbalance
                # Define a fair value for the PEARLS.
                acceptable_price = mid_price
                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                
                if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0: # 双边都有挂单
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    # taker strategy
                    # TODO：两个 buy order 可能同时发单，两个 sell order 也可能同时发单
                    if best_ask <= acceptable_price:# 卖得低，take the sell order on the orderbook as much as possible
                        orders.append(Order(product, best_ask, int(min(-best_ask_volume,legal_buy_vol))))

                        legal_buy_vol = legal_buy_vol - int(min(-best_ask_volume,legal_buy_vol))
                    if best_bid >= acceptable_price: # 买得贵，take the buy order on the orderbook as much as possible
                        orders.append(Order(product, best_bid, int(max(-best_bid_volume,legal_sell_vol))))

                        legal_sell_vol = legal_sell_vol - int(max(-best_bid_volume,legal_sell_vol))
                    
                    # maker strategy
                    if best_ask - 1 >= acceptable_price:# orderbook最优卖单足够贵，我们可以以-1的价格仍然卖出获利
                        # make the market by placing a sell order at a price of 1 below the best ask
                        orders.append(Order(product, best_ask - 1, legal_sell_vol))
                    if best_bid + 1 <= acceptable_price:
                        # make the market by placing a buy order at a price of 1 above the best bid
                        orders.append(Order(product, best_bid + 1, legal_buy_vol))

                elif len(order_depth.buy_orders) > 0 and len(order_depth.sell_orders) == 0: # 只有买单
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid >= acceptable_price:
                        orders.append(Order(product, best_bid, int(max(-best_bid_volume,legal_sell_vol))))

                elif len(order_depth.buy_orders) == 0 and len(order_depth.sell_orders) > 0: # 只有卖单
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    if best_ask <= acceptable_price:
                        orders.append(Order(product, best_ask, int(min(-best_ask_volume,legal_buy_vol))))
                # Add all the above the orders to the result dict
                result[product] = orders



            if product == 'BANANAS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # quote volume limit
                current_position = 0 if product not in state.position else state.position[product]

                legal_buy_vol = min(self.position_limit[product] - current_position,self.position_limit[product])
                legal_sell_vol = max(-(self.position_limit[product] + current_position),-self.position_limit[product])
                
                if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    avg_buy_price = sum([order_depth.buy_orders[i] * i for i in order_depth.buy_orders.keys()])/sum([order_depth.buy_orders[i] for i in order_depth.buy_orders.keys()])
                    avg_sell_price = sum([-order_depth.sell_orders[i] * i for i in order_depth.sell_orders.keys()])/sum([-order_depth.sell_orders[i] for i in order_depth.sell_orders.keys()])
                    # calculate the mid price
                    mid_price = (avg_sell_price + avg_buy_price)/2

                else:
                    mid_price = self.last_mid_price[product]

                self.last_mid_price[product] = mid_price


                acceptable_price = mid_price

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                # Calculate the mid price of the PEARLS market
                
                if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0: # 双边都有挂单
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    # taker strategy
                    # TODO：两个 buy order 可能同时发单，两个 sell order 也可能同时发单
                    if best_ask <= acceptable_price:# 卖得低，take the sell order on the orderbook as much as possible
                        orders.append(Order(product, best_ask, int(min(-best_ask_volume,legal_buy_vol))))

                        legal_buy_vol = legal_buy_vol - int(min(-best_ask_volume,legal_buy_vol))
                    if best_bid >= acceptable_price: # 买得贵，take the buy order on the orderbook as much as possible
                        orders.append(Order(product, best_bid, int(max(-best_bid_volume,legal_sell_vol))))

                        legal_sell_vol = legal_sell_vol - int(max(-best_bid_volume,legal_sell_vol))
                    
                    # maker strategy
                    if best_ask - 1 >= acceptable_price:# orderbook最优卖单足够贵，我们可以以-1的价格仍然卖出获利
                        # make the market by placing a sell order at a price of 1 below the best ask
                        orders.append(Order(product, best_ask - 1, legal_sell_vol))
                    if best_bid + 1 <= acceptable_price:
                        # make the market by placing a buy order at a price of 1 above the best bid
                        orders.append(Order(product, best_bid + 1, legal_buy_vol))

                elif len(order_depth.buy_orders) > 0 and len(order_depth.sell_orders) == 0: # 只有买单
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid >= acceptable_price:
                        orders.append(Order(product, best_bid, int(max(-best_bid_volume,legal_sell_vol))))

                elif len(order_depth.buy_orders) == 0 and len(order_depth.sell_orders) > 0: # 只有卖单
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    if best_ask <= acceptable_price:
                        orders.append(Order(product, best_ask, int(min(-best_ask_volume,legal_buy_vol))))
                # Add all the above the orders to the result dict
                
                
                result[product] = orders
        return result
