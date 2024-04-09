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
        self.last_coco_ask_tran = 0
        self.last_coco_bid_tran = 0
        self.last_etf = 1000

    def market_status(self, state: TradingState, product) -> int:
        order_depth: OrderDepth = state.order_depths[product]
        if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
            best_ask_volume = order_depth.sell_orders[min(
                order_depth.sell_orders.keys())]
            best_bid_volume = order_depth.buy_orders[max(
                order_depth.buy_orders.keys())]
            if best_ask_volume >= 60 and best_bid_volume < 60:
                return -1
            elif best_ask_volume < 60 and best_bid_volume >= 60:
                return 1
            else:
                return 0

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}
        # pair trading

        coconut_current_position = 0 if 'COCONUTS' not in state.position else state.position[
            'COCONUTS']
        pina_colada_current_position = 0 if 'PINA_COLADAS' not in state.position else state.position[
            'PINA_COLADAS']

        pos_ratio = coconut_current_position / pina_colada_current_position if (
            coconut_current_position != 0) and (pina_colada_current_position != 0) else 0
        
        legal_buy_vol_coco = min(
            self.position_limit['COCONUTS'] - coconut_current_position, self.position_limit['COCONUTS'])
        legal_sell_vol_coco = max(-(self.position_limit['COCONUTS'] +
                                  coconut_current_position), -self.position_limit['COCONUTS'])

        legal_buy_vol_pina = min(
            self.position_limit['PINA_COLADAS'] - pina_colada_current_position, self.position_limit['PINA_COLADAS'])
        legal_sell_vol_pina = max(-(self.position_limit['PINA_COLADAS'] +
                                  pina_colada_current_position), -self.position_limit['PINA_COLADAS'])

        etf_current_position = min(round(coconut_current_position/2),-pina_colada_current_position)

        legal_buy_vol_etf = min(300 - etf_current_position, 300)
        legal_sell_vol_etf = max(-(300 + etf_current_position), -300)

        coconut_order_depth: OrderDepth = state.order_depths['COCONUTS']

        pina_colada_order_depth: OrderDepth = state.order_depths['PINA_COLADAS']

        if len(coconut_order_depth.sell_orders) != 0 and len(coconut_order_depth.buy_orders) != 0:
            coconut_best_ask = min(coconut_order_depth.sell_orders.keys())
            coconut_best_ask_volume = coconut_order_depth.sell_orders[coconut_best_ask]
            coconut_best_bid = max(coconut_order_depth.buy_orders.keys())
            coconut_best_bid_volume = coconut_order_depth.buy_orders[coconut_best_bid]
            coconut_avg_buy_price = sum([coconut_order_depth.buy_orders[i] * i for i in coconut_order_depth.buy_orders.keys()])/sum(
                [coconut_order_depth.buy_orders[i] for i in coconut_order_depth.buy_orders.keys()])
            coconut_avg_sell_price = sum([-coconut_order_depth.sell_orders[i] * i for i in coconut_order_depth.sell_orders.keys()])/sum(
                [-coconut_order_depth.sell_orders[i] for i in coconut_order_depth.sell_orders.keys()])
            coconut_mid_price = (coconut_avg_sell_price +
                                 coconut_avg_buy_price)/2

        else:
            coconut_mid_price = self.last_mid_price['COCONUTS']

        self.last_mid_price['COCONUTS'] = coconut_mid_price

        orders1: list[Order] = []
        orders2: list[Order] = []

        if len(pina_colada_order_depth.sell_orders) != 0 and len(pina_colada_order_depth.buy_orders) != 0:
            pina_colada_best_ask = min(
                pina_colada_order_depth.sell_orders.keys())
            pina_colada_best_ask_volume = pina_colada_order_depth.sell_orders[
                pina_colada_best_ask]
            pina_colada_best_bid = max(
                pina_colada_order_depth.buy_orders.keys())
            pina_colada_best_bid_volume = pina_colada_order_depth.buy_orders[pina_colada_best_bid]
            pina_colada_avg_buy_price = sum([pina_colada_order_depth.buy_orders[i] * i for i in pina_colada_order_depth.buy_orders.keys()])/sum([
                pina_colada_order_depth.buy_orders[i] for i in pina_colada_order_depth.buy_orders.keys()])
            pina_colada_avg_sell_price = sum([-pina_colada_order_depth.sell_orders[i] * i for i in pina_colada_order_depth.sell_orders.keys()])/sum(
                [-pina_colada_order_depth.sell_orders[i] for i in pina_colada_order_depth.sell_orders.keys()])
            pina_colada_mid_price = (
                pina_colada_avg_sell_price + pina_colada_avg_buy_price)/2
        else:
            pina_colada_mid_price = self.last_mid_price['PINA_COLADAS']
        self.last_mid_price['PINA_COLADAS'] = pina_colada_mid_price

        # 对coconut做市
        # if len(coconut_order_depth.sell_orders) > 0 and len(coconut_order_depth.buy_orders) > 0: # 双边都有挂单
        # # build the orderbook of ETF based on these 2 products
        ETF = 2*coconut_mid_price - pina_colada_mid_price
        best_ask_etf = 2*coconut_best_ask - pina_colada_best_bid
        best_ask_volume_etf = max(
            coconut_best_ask_volume/2, -pina_colada_best_bid_volume)
        best_bid_etf = 2*coconut_best_bid - pina_colada_best_ask
        best_bid_volume_etf = min(
            coconut_best_bid_volume/2, -pina_colada_best_ask_volume)

        print([best_ask_volume_etf, best_bid_volume_etf, etf_current_position])

        if best_ask_etf <= ETF:

            orders1.append(Order('COCONUTS', coconut_best_ask, int(
                min(-best_ask_volume_etf*2, legal_buy_vol_coco))))
            orders2.append(Order('PINA_COLADAS', pina_colada_best_ask, int(
                min(-best_ask_volume_etf, legal_buy_vol_pina))))

        if best_bid_etf >= ETF:
            # coco跌，pina跌
            orders2.append(Order('PINA_COLADAS', pina_colada_best_bid, int(
                max(-best_bid_volume_etf, legal_sell_vol_pina))))
            orders1.append(Order('COCONUTS', coconut_best_bid, int(
                max(-best_bid_volume_etf*2, legal_sell_vol_coco))))

        #acceptable_price = coconut_mid_price
        '''
		if best_ask_etf <= ETF and ETF >1000:

			orders1.append(Order('COCONUTS', coconut_best_ask, int(min(-best_ask_volume_etf*2,legal_buy_vol_coco))))
			orders2.append(Order('PINA_COLADAS', pina_colada_best_bid, int(min(-best_bid_volume_etf,legal_sell_vol_pina))))
			#orders2.append(Order('PINA_COLADAS', pina_colada_best_ask, int(min(-best_ask_volume_etf,legal_buy_vol_pina))))
		elif best_ask_etf <= ETF and ETF < 1000:
			#coco跌，pina涨
			orders1.append(Order('COCONUTS', coconut_best_ask, int(min(-best_ask_volume_etf*2,legal_buy_vol_coco))))
			#orders2.append(Order('PINA_COLADAS', pina_colada_best_bid, int(min(-best_bid_volume_etf,legal_sell_vol_pina))))
			orders2.append(Order('PINA_COLADAS', pina_colada_best_ask, int(min(-best_ask_volume_etf,legal_buy_vol_pina))))

		if best_bid_etf >= ETF and ETF < 1000:
			#coco跌，pina跌
			#orders2.append(Order('PINA_COLADAS', pina_colada_best_bid, int(max(-best_bid_volume_etf,legal_sell_vol_pina))))
			orders1.append(Order('COCONUTS', coconut_best_bid, int(max(-best_bid_volume_etf*2,legal_sell_vol_coco))))
			orders2.append(Order('PINA_COLADAS', pina_colada_best_ask, int(min(-best_ask_volume_etf,legal_buy_vol_pina))))
		elif best_bid_etf >= ETF and ETF > 1000:
			#coco涨，pina跌
			orders1.append(Order('COCONUTS', coconut_best_bid, int(max(-best_bid_volume_etf*2,legal_sell_vol_coco))))
			#orders2.append(Order('PINA_COLADAS', pina_colada_best_ask, int(min(-best_ask_volume_etf,legal_buy_vol_pina))))
			orders2.append(Order('PINA_COLADAS', pina_colada_best_bid, int(max(-best_bid_volume_etf,legal_sell_vol_pina))))
		'''
        result['COCONUTS'] = orders1
        result['PINA_COLADAS'] = orders2

        return result
