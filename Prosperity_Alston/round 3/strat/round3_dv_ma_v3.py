#BERRY无maker_仅双边挂单_仅周期:514 
#有maker_仅双边挂单_仅周期 1348
#v3_final: ******************
#berries双边：周期&take & maker 单边：taker
#改进： dv加了趋势预测，如果ds迅速上升，fair price调高 多买，ds迅速下降，fair price调低，多卖
#dv pnl:5132 n=20,diff = 0.99%(1.8)
import json
from datamodel import Order, ProsperityEncoder, Symbol, TradingState, OrderDepth
from typing import Any, Dict, List
import numpy as np

class Logger:
    def __init__(self) -> None:
        self.logs = ""

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]]) -> None:
        print(json.dumps({
            "state": state,
            "orders": orders,
            "logs": self.logs,
        }, cls=ProsperityEncoder, separators=(",", ":"), sort_keys=True))

        self.logs = ""

logger = Logger()

class Trader:
    # define data members
    def __init__(self):
        self.position_limit = {"PEARLS": 20, "BANANAS": 20,'COCONUTS':600,'PINA_COLADAS':300,'BERRIES':250,'DIVING_GEAR':50,'DOLPHIN_SIGHTINGS':0}
        self.last_mid_price = {'PEARLS': 10000, 'BANANAS': 4900,'COCONUTS':8000,'PINA_COLADAS':15000,'BERRIES':4000,'DIVING_GEAR':10000,'DOLPHIN_SIGHTINGS':3000}
        self.ema_price = {'DOLPHIN_SIGHTINGS':3000}
        self.last_ema_price = {'DOLPHIN_SIGHTINGS':3000}
        self.acceptable_price = {'PEARLS': 10000, 'BANANAS': 5000,'COCONUTS': 8000,'PINA_COLADAS': 15000,'BERRIES':4000,'DIVING_GEAR':10000,'DOLPHIN_SIGHTINGS':0}
        self.legal_buy_vol = {'PEARLS': 20, 'BANANAS': 20,'COCONUTS': 600,'PINA_COLADAS': 300,'BERRIES':250,'DIVING_GEAR':50,'DOLPHIN_SIGHTINGS':0}
        self.legal_sell_vol = {'PEARLS': -20, 'BANANAS': -20,'COCONUTS': -600,'PINA_COLADAS': -300,'BERRIES':-250,'DIVING_GEAR':-50,'DOLPHIN_SIGHTINGS':0}
        # store the orderbook depth 1 for each product
        self.best_bid = {'PEARLS': 0, 'BANANAS': 0,'COCONUTS': 0,'PINA_COLADAS': 0,'BERRIES':0,'DIVING_GEAR':0,'DOLPHIN_SIGHTINGS':0}
        self.best_ask = {'PEARLS': 0, 'BANANAS': 0,'COCONUTS': 0,'PINA_COLADAS': 0,'BERRIES':0,'DIVING_GEAR':0,'DOLPHIN_SIGHTINGS':0}
        self.best_bid_volume = {'PEARLS': 0, 'BANANAS': 0,'COCONUTS': 0,'PINA_COLADAS': 0,'BERRIES':0,'DIVING_GEAR':0,'DOLPHIN_SIGHTINGS':0}
        self.best_ask_volume = {'PEARLS': 0, 'BANANAS': 0,'COCONUTS': 0,'PINA_COLADAS': 0,'BERRIES':0,'DIVING_GEAR':0,'DOLPHIN_SIGHTINGS':0}
        self.last_best_bid = {'PEARLS': 0, 'BANANAS': 0,'COCONUTS': 0,'PINA_COLADAS': 0,'BERRIES':0,'DIVING_GEAR':0,'DOLPHIN_SIGHTINGS':0}
        self.last_best_ask = {'PEARLS': 0, 'BANANAS': 0,'COCONUTS': 0,'PINA_COLADAS': 0,'BERRIES':0,'DIVING_GEAR':0,'DOLPHIN_SIGHTINGS':0}



    
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        
        # Initialize the method output dict as an empty dict
        result = {}
        # Iterate over all the keys (the available products) contained in the order depths

        # for each product, we read its orderbook at first
        # to get:
        # 1. the fair price(weighted mid price)
        # 2. the legal buy volume and legal sell volume


        self.last_mid_price['DOLPHIN_SIGHTINGS'] = state.observations['DOLPHIN_SIGHTINGS']

        N=30
        self.ema_price['DOLPHIN_SIGHTINGS'] = (2 * state.observations['DOLPHIN_SIGHTINGS'] + (N - 1) * self.last_ema_price['DOLPHIN_SIGHTINGS']) / (N + 1)
            

        for product in state.order_depths.keys():
            
            # 算仓位信息，和 orderbook 无关
            if product in state.position.keys():
                current_position = state.position[product]
            else:
                current_position = 0
            
            time = state.timestamp
            legal_buy_vol = self.position_limit[product] - current_position # -pos_limit <=cur<=pos_limit, so the legal buy vol is always non-negative
            legal_sell_vol = -self.position_limit[product] - current_position # -pos_limit <=cur<=pos_limit, so the legal sell vol is always non-positive

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
            elif len(order_depth.sell_orders) == 0 and len(order_depth.buy_orders) != 0: # 只有买单
                best_ask = 0
                best_ask_volume = 0
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                mid_price = self.last_mid_price[product]
            elif len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) == 0: # 只有卖单
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                best_bid = 0
                best_bid_volume = 0
                mid_price = self.last_mid_price[product]
            else:
                mid_price = self.last_mid_price[product]

            # save the calculation result
            self.best_bid[product] = best_bid
            self.best_ask[product] = best_ask
            self.best_bid_volume[product] = best_bid_volume
            self.best_ask_volume[product] = best_ask_volume
            self.last_mid_price[product] = mid_price
            self.legal_buy_vol[product] = legal_buy_vol
            self.legal_sell_vol[product] = legal_sell_vol
            
            

        # for each product, we place the order
        for product in state.order_depths.keys():
                # the relationship between coconut and pina colada linear with intercept, 2*coconut = pina colada+1000
            alpha = -10000
            if product == 'PEARLS' or product == 'BANANAS' or product == 'BERRIES':
                self.acceptable_price[product] = self.last_mid_price[product]
            #elif product == 'BERRIES':
            #    self.acceptable_price[product] = self.last_mid_price[product]*(1+np.sin((time%alpha)/alpha*np.pi/10000))
            elif product == 'COCONUTS':
                self.acceptable_price[product] = (self.last_mid_price[product]+((self.last_mid_price['PINA_COLADAS']+1000)/2))/2
            elif product == 'PINA_COLADAS':
                self.acceptable_price[product] = (self.last_mid_price[product]*1/3 +(self.last_mid_price['COCONUTS']*2-1000)*2/3)
            elif product == 'DIVING_GEAR':
                if abs(self.last_mid_price['DOLPHIN_SIGHTINGS'] -self.ema_price['DOLPHIN_SIGHTINGS'])>=2.3:

                    self.acceptable_price[product] = self.last_mid_price[product] *self.ema_price['DOLPHIN_SIGHTINGS']/self.last_mid_price['DOLPHIN_SIGHTINGS']
                else:
                    self.acceptable_price[product] = self.last_mid_price[product]


            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []


            # get acceptable price, legal buy volume and legal sell volume from the init
            acceptable_price = self.acceptable_price[product]
            legal_buy_vol = self.legal_buy_vol[product]
            legal_sell_vol = self.legal_sell_vol[product]
            if product == 'BERRIES':
                if self.best_ask_volume[product] !=0 and self.best_bid_volume[product] !=0: # 双边都有挂单
                    best_ask = self.best_ask[product]
                    best_ask_volume = self.best_ask_volume[product]
                    best_bid = self.best_bid[product]
                    best_bid_volume = self.best_bid_volume[product]
                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    # taker strategy
                    # TODO：两个 buy order 可能同时发单，两个 sell order 也可能同时发单
                    
                    if best_bid > self.last_best_ask[product]:# 卖得低，take the sell order on the orderbook as much as possible

                        orders.append(Order(product, best_ask, int(min(-best_ask_volume,legal_buy_vol))))

                        # 因为我们买了，所以我们可以买的量减少，我们可以卖的量增加
                        # TODO: 先更新 sell, 如果先更新buy,那更新sell的时候数值已经变了
                        legal_sell_vol = legal_sell_vol - int(min(-best_ask_volume,legal_buy_vol))
                        legal_buy_vol = legal_buy_vol - int(min(-best_ask_volume,legal_buy_vol))

                    elif best_ask < self.last_best_bid[product]: # 买得贵，take the buy order on the orderbook as much as possible
                        orders.append(Order(product, best_bid, int(max(-best_bid_volume,legal_sell_vol))))
                        # 因为我们卖了，所以我们可以卖的量减少，我们可以买的量增加
                        legal_buy_vol = legal_buy_vol - int(max(-best_bid_volume,legal_sell_vol))
                        legal_sell_vol = legal_sell_vol - int(max(-best_bid_volume,legal_sell_vol)) 
                    
                    else:
                        if best_ask <= acceptable_price:# 卖得低，take the sell order on the orderbook as much as possible
                            orders.append(Order(product, best_ask, int(min(-best_ask_volume,legal_buy_vol))))

                            # 因为我们买了，所以我们可以买的量减少，我们可以卖的量增加
                            # TODO: 先更新 sell, 如果先更新buy,那更新sell的时候数值已经变了
                            legal_sell_vol = legal_sell_vol - int(min(-best_ask_volume,legal_buy_vol))
                            legal_buy_vol = legal_buy_vol - int(min(-best_ask_volume,legal_buy_vol))

                        if best_bid >= acceptable_price: # 买得贵，take the buy order on the orderbook as much as possible
                            orders.append(Order(product, best_bid, int(max(-best_bid_volume,legal_sell_vol))))
                            # 因为我们卖了，所以我们可以卖的量减少，我们可以买的量增加
                            legal_buy_vol = legal_buy_vol - int(max(-best_bid_volume,legal_sell_vol))
                            legal_sell_vol = legal_sell_vol - int(max(-best_bid_volume,legal_sell_vol)) 
                            
                        
                        # maker strategy
                        if best_ask - 1 >= acceptable_price:# orderbook最优卖单足够贵，我们可以以-1的价格仍然卖出获利
                            # make the market by placing a sell order at a price of 1 below the best ask
                            orders.append(Order(product, best_ask - 1, legal_sell_vol))
                        if best_bid + 1 <= acceptable_price:
                            # make the market by placing a buy order at a price of 1 above the best bid
                            orders.append(Order(product, best_bid + 1, legal_buy_vol))

                elif self.best_ask_volume[product] ==0 and self.best_bid_volume[product] !=0: # 只有买单
                    best_bid = self.best_bid[product]
                    best_bid_volume = self.best_bid_volume[product]
                    if best_bid >= acceptable_price:
                        orders.append(Order(product, best_bid, int(max(-best_bid_volume,legal_sell_vol))))

                elif self.best_ask_volume[product] !=0 and self.best_bid_volume[product] ==0: # 只有卖单
                    best_ask = self.best_ask[product]
                    best_ask_volume = self.best_ask_volume[product]
                    if best_ask <= acceptable_price:
                        orders.append(Order(product, best_ask, int(min(-best_ask_volume,legal_buy_vol))))
            else:
                if self.best_ask_volume[product] !=0 and self.best_bid_volume[product] !=0: # 双边都有挂单
                    best_ask = self.best_ask[product]
                    best_ask_volume = self.best_ask_volume[product]
                    best_bid = self.best_bid[product]
                    best_bid_volume = self.best_bid_volume[product]
                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    # taker strategy
                    # TODO：两个 buy order 可能同时发单，两个 sell order 也可能同时发单
                    
                    if best_ask <= acceptable_price:# 卖得低，take the sell order on the orderbook as much as possible
                        orders.append(Order(product, best_ask, int(min(-best_ask_volume,legal_buy_vol))))

                        # 因为我们买了，所以我们可以买的量减少，我们可以卖的量增加
                        # TODO: 先更新 sell, 如果先更新buy,那更新sell的时候数值已经变了
                        legal_sell_vol = legal_sell_vol - int(min(-best_ask_volume,legal_buy_vol))
                        legal_buy_vol = legal_buy_vol - int(min(-best_ask_volume,legal_buy_vol))

                    if best_bid >= acceptable_price: # 买得贵，take the buy order on the orderbook as much as possible
                        orders.append(Order(product, best_bid, int(max(-best_bid_volume,legal_sell_vol))))
                        # 因为我们卖了，所以我们可以卖的量减少，我们可以买的量增加
                        legal_buy_vol = legal_buy_vol - int(max(-best_bid_volume,legal_sell_vol))
                        legal_sell_vol = legal_sell_vol - int(max(-best_bid_volume,legal_sell_vol)) 
                        
                    
                    # maker strategy
                    if best_ask - 1 >= acceptable_price:# orderbook最优卖单足够贵，我们可以以-1的价格仍然卖出获利
                        # make the market by placing a sell order at a price of 1 below the best ask
                        orders.append(Order(product, best_ask - 1, legal_sell_vol))
                    if best_bid + 1 <= acceptable_price:
                        # make the market by placing a buy order at a price of 1 above the best bid
                        orders.append(Order(product, best_bid + 1, legal_buy_vol))

                elif self.best_ask_volume[product] ==0 and self.best_bid_volume[product] !=0: # 只有买单
                    best_bid = self.best_bid[product]
                    best_bid_volume = self.best_bid_volume[product]
                    if best_bid >= acceptable_price:
                        orders.append(Order(product, best_bid, int(max(-best_bid_volume,legal_sell_vol))))

                elif self.best_ask_volume[product] !=0 and self.best_bid_volume[product] ==0: # 只有卖单
                    best_ask = self.best_ask[product]
                    best_ask_volume = self.best_ask_volume[product]
                    if best_ask <= acceptable_price:
                        orders.append(Order(product, best_ask, int(min(-best_ask_volume,legal_buy_vol))))

            # Add all the above the orders to the result dict
            result[product] = orders
            self.last_best_bid[product] = best_bid
            self.last_best_ask[product] = best_ask
        self.last_ema_price['DOLPHIN_SIGHTINGS'] = self.ema_price['DOLPHIN_SIGHTINGS']

        logger.flush(state, result)   
        return result
