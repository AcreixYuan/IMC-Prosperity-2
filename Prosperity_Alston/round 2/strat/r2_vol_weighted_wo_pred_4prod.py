from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

# PEARLS strategy: 
# fair_price = EMA(weighted mid price,20) 


class Trader:
    # define data members
    def __init__(self):
        self.position_limit = {"PEARLS": 20, "BANANAS": 20,"COCONUTS":600,"PINA_COLADAS":300}
        self.last_mid_price = {'PEARLS': 10000, 'BANANAS': 5000,'COCONUTS': 8000,'PINA_COLADAS': 15000}
        self.acceptable_price = {'PEARLS': 10000, 'BANANAS': 5000,'COCONUTS': 8000,'PINA_COLADAS': 15000}
        self.legal_buy_vol = {'PEARLS': 20, 'BANANAS': 20,'COCONUTS': 600,'PINA_COLADAS': 300}
        self.legal_sell_vol = {'PEARLS': 20, 'BANANAS': 20,'COCONUTS': 600,'PINA_COLADAS': 300}


    
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        
        # Initialize the method output dict as an empty dict
        result = {}
        # Iterate over all the keys (the available products) contained in the order depths

        # for each product, we read its orderbook at first
        # to get:
        # 1. the fair price(weighted mid price)
        # 2. the legal buy volume and legal sell volume

        for product in state.order_depths.keys():
            
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
                best_ask_volume = order_depth.sell_orders[best_ask]
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                avg_buy_price = sum([order_depth.buy_orders[i] * i for i in order_depth.buy_orders.keys()])/sum([order_depth.buy_orders[i] for i in order_depth.buy_orders.keys()])
                avg_sell_price = sum([-order_depth.sell_orders[i] * i for i in order_depth.sell_orders.keys()])/sum([-order_depth.sell_orders[i] for i in order_depth.sell_orders.keys()])
                buy_order_volume = sum([order_depth.buy_orders[i] for i in order_depth.buy_orders.keys()])
                sell_order_volume = sum([-order_depth.sell_orders[i] for i in order_depth.sell_orders.keys()])
                mid_price = (avg_sell_price*sell_order_volume + avg_buy_price*buy_order_volume)/(sell_order_volume+buy_order_volume)
            else:
                mid_price = self.last_mid_price[product]

            self.last_mid_price[product] = mid_price
            self.legal_buy_vol[product] = legal_buy_vol
            self.legal_sell_vol[product] = legal_sell_vol
            

        

        # for each product, we place the order
        for product in state.order_depths.keys():
                # the relationship between coconut and pina colada linear with intercept, 2*coconut = pina colada+1000

            if product == 'PEARLS' or product == 'BANANAS':
                self.acceptable_price[product] = self.last_mid_price[product]
            elif product == 'COCONUTS':
                self.acceptable_price[product] = (self.last_mid_price[product]+((self.last_mid_price['PINA_COLADAS']+1000)/2))/2
            elif product == 'PINA_COLADAS':
                self.acceptable_price[product] = (self.last_mid_price[product] +(self.last_mid_price['COCONUTS']*2-1000))/2
            else:
                self.acceptable_price[product] = self.last_mid_price[product]

            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []


            # get acceptable price, legal buy volume and legal sell volume from the init
            acceptable_price = self.acceptable_price[product]
            legal_buy_vol = self.legal_buy_vol[product]
            legal_sell_vol = self.legal_sell_vol[product]
            
            # load the orderbook for one more time to place the order
            order_depth: OrderDepth = state.order_depths[product]


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
