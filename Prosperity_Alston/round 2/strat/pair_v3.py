import json
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order, ProsperityEncoder, Symbol
import numpy as np

# PEARLS strategy:
# fair_price = EMA(weighted mid price,20)
from typing import Any


class Trader:
    # define data members
    def __init__(self):
        self.position_limit = {"PEARLS": 20, "BANANAS": 20,
                               'COCONUTS': 600, 'PINA_COLADAS': 300}
        self.last_mid_price = {
            'PEARLS': 10000, 'BANANAS': 4900, 'COCONUTS': 8000, 'PINA_COLADAS': 15000}
        self.fair_price = 1000
        self.last_bid = {'COCONUTS': 0, 'PINA_COLADAS': 0}
        self.last_ask = {'COCONUTS': 0, 'PINA_COLADAS': 0}
        self.last_bid_vol = {'COCONUTS': 0, 'PINA_COLADAS': 0}
        self.last_ask_vol = {'COCONUTS': 0, 'PINA_COLADAS': 0}
        self.z = []

    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        # Initialize the method output dict as an empty dict
        result = {}
        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
            if product == 'COCONUTS' or product == 'PINA_COLADAS':
                # 算 挂单的数量
                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0
                legal_buy_vol = min(
                    self.position_limit[product] - current_position, self.position_limit[product])
                legal_sell_vol = max(
                    -(self.position_limit[product] + current_position), -self.position_limit[product])
                order_depth: OrderDepth = state.order_depths[product]

                if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    avg_buy_price = sum([order_depth.buy_orders[i] * i for i in order_depth.buy_orders.keys()])/sum(
                        [order_depth.buy_orders[i] for i in order_depth.buy_orders.keys()])
                    avg_sell_price = sum([-order_depth.sell_orders[i] * i for i in order_depth.sell_orders.keys()])/sum(
                        [-order_depth.sell_orders[i] for i in order_depth.sell_orders.keys()])
                    # fair price 是 weighted mid price
                    mid_price = (avg_sell_price + avg_buy_price)/2
                    # 记录订单数据
                    self.last_ask[product] = best_ask
                    self.last_bid[product] = best_bid
                    self.last_ask_vol[product] = best_ask_volume
                    self.last_bid_vol[product] = best_bid_volume
                elif len(order_depth.sell_orders) == 0 and len(order_depth.buy_orders) != 0:  # 只有买单
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    mid_price = self.last_mid_price[product]
                    # 记录订单数据
                    self.last_bid[product] = best_bid
                    self.last_bid_vol[product] = best_bid_volume
                elif len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) == 0:  # 只有卖单
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    mid_price = self.last_mid_price[product]
                    # 记录订单数据
                    self.last_ask[product] = best_ask
                    self.last_ask_vol[product] = best_ask_volume
                else:
                    mid_price = self.last_mid_price[product]

                # 记录 读完 order book 之后的 mid price
                    self.last_mid_price[product] = mid_price

                if product == 'COCONUTS':
                    etf = 2*mid_price - self.last_mid_price['PINA_COLADAS']

                else:
                    etf = 2 * self.last_mid_price['COCONUTS'] - mid_price

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:  # 双边都有挂单
                    if product == 'COCONUTS':
                        best_ask = min(order_depth.sell_orders.keys())
                        best_ask_volume = order_depth.sell_orders[best_ask]
                        best_bid = max(order_depth.buy_orders.keys())
                        best_bid_volume = order_depth.buy_orders[best_bid]

                        best_ask_etf = 2*best_ask - \
                            self.last_bid['PINA_COLADAS']
                        best_ask_volume_etf = min(
                            2*best_ask_volume, self.last_bid_vol['PINA_COLADAS'])
                        best_bid_etf = 2*best_bid - \
                            self.last_ask['PINA_COLADAS']
                        best_bid_volume_etf = min(
                            2*best_bid_volume, self.last_ask_vol['PINA_COLADAS'])

                        if best_ask_etf <= etf:
                            # take sell order of coco
                            orders.append(Order('COCONUTS', best_ask, int(
                                min(-best_ask_volume, legal_buy_vol))))
                            #orders.append(Order('PINA_COLADAS', self.last_ask['PINA_COLADAS'], -int(min(-best_ask_volume,legal_buy_vol))))

                        if best_bid_etf >= etf:
                            # take buy order of coco
                            orders.append(Order('COCONUTS', best_bid, int(
                                max(-best_bid_volume, legal_sell_vol))))
                            #orders.append(Order('PINA_COLADAS', self.last_bid['PINA_COLADAS'], -int(min(-best_ask_volume,legal_buy_vol))))

                    if product == 'PINA_COLADAS':
                        best_ask = min(order_depth.sell_orders.keys())
                        best_ask_volume = order_depth.sell_orders[best_ask]
                        best_bid = max(order_depth.buy_orders.keys())
                        best_bid_volume = order_depth.buy_orders[best_bid]

                        best_ask_etf = 2*self.last_ask['COCONUTS'] - best_bid
                        best_ask_volume_etf = min(
                            2*self.last_ask_vol['COCONUTS'], best_bid_volume)
                        best_bid_etf = 2*self.last_bid['COCONUTS'] - best_ask
                        best_bid_volume_etf = min(
                            2*self.last_bid_vol['COCONUTS'], best_ask_volume)
                        if best_ask_etf >= etf:
                            # take buy order of pina
                            orders.append(Order('PINA_COLADAS', best_bid, int(
                                max(-best_bid_volume, legal_sell_vol))))

                        else:
                            # take sell order of pina
                            orders.append(Order('PINA_COLADAS', best_ask, int(
                                min(-best_ask_volume, legal_buy_vol))))
                result[product] = orders

        return result
