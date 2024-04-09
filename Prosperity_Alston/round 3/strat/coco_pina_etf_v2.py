import json
from datamodel import Order, ProsperityEncoder, Symbol, TradingState, OrderDepth
from typing import Any, Dict, List
# PNL pina:10088
# coco:3353


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


    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}
        coconut_current_position = 0 if 'COCONUTS' not in state.position else state.position[
            'COCONUTS']
        pina_colada_current_position = 0 if 'PINA_COLADAS' not in state.position else state.position[
            'PINA_COLADAS']


        legal_buy_vol_coco = min(
            self.position_limit['COCONUTS'] - coconut_current_position, self.position_limit['COCONUTS'])
        legal_sell_vol_coco = max(-(self.position_limit['COCONUTS'] +
                                  coconut_current_position), -self.position_limit['COCONUTS'])

        legal_buy_vol_pina = min(
            self.position_limit['PINA_COLADAS'] - pina_colada_current_position, self.position_limit['PINA_COLADAS'])
        legal_sell_vol_pina = max(-(self.position_limit['PINA_COLADAS'] +
                                  pina_colada_current_position), -self.position_limit['PINA_COLADAS'])


        coconut_order_depth: OrderDepth = state.order_depths['COCONUTS']

        pina_colada_order_depth: OrderDepth = state.order_depths['PINA_COLADAS']
        # 读 coconut order depth 计算 mid price 
        if len(coconut_order_depth.sell_orders) != 0 and len(coconut_order_depth.buy_orders) != 0:
            coconut_best_ask = min(coconut_order_depth.sell_orders.keys())
            coconut_best_ask_volume = coconut_order_depth.sell_orders[coconut_best_ask]
            coconut_best_bid = max(coconut_order_depth.buy_orders.keys())
            coconut_best_bid_volume = coconut_order_depth.buy_orders[coconut_best_bid]
            coconut_avg_buy_price = sum([coconut_order_depth.buy_orders[i] * i for i in coconut_order_depth.buy_orders.keys()])/sum(
                [coconut_order_depth.buy_orders[i] for i in coconut_order_depth.buy_orders.keys()])
            coconut_avg_sell_price = sum([-coconut_order_depth.sell_orders[i] * i for i in coconut_order_depth.sell_orders.keys()])/sum(
                [-coconut_order_depth.sell_orders[i] for i in coconut_order_depth.sell_orders.keys()])
            coco_buy_order_volume = sum(
                [coconut_order_depth.buy_orders[i] for i in coconut_order_depth.buy_orders.keys()])
            coco_sell_order_volume = sum(
                [-coconut_order_depth.sell_orders[i] for i in coconut_order_depth.sell_orders.keys()])
            coconut_mid_price = (coconut_avg_sell_price*coco_sell_order_volume + coconut_avg_buy_price *
                                 coco_buy_order_volume)/(coco_sell_order_volume+coco_buy_order_volume)

        else:
            coconut_mid_price = self.last_mid_price['COCONUTS']

        self.last_mid_price['COCONUTS'] = coconut_mid_price

        orders1: list[Order] = []
        orders2: list[Order] = []
        # 读 pina colada order depth 计算 mid price
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
            pina_buy_order_volume = sum(
                [pina_colada_order_depth.buy_orders[i] for i in pina_colada_order_depth.buy_orders.keys()])
            pina_sell_order_volume = sum(
                [-pina_colada_order_depth.sell_orders[i] for i in pina_colada_order_depth.sell_orders.keys()])
            pina_colada_mid_price = (pina_colada_avg_sell_price*pina_sell_order_volume +
                                     pina_colada_avg_buy_price*pina_buy_order_volume)/(pina_sell_order_volume+pina_buy_order_volume)

        else:
            pina_colada_mid_price = self.last_mid_price['PINA_COLADAS']
        self.last_mid_price['PINA_COLADAS'] = pina_colada_mid_price
        
		# 计算 etf mid price
        ETF = 2*coconut_mid_price - pina_colada_mid_price
        best_ask_etf = 2*coconut_best_ask - pina_colada_best_bid
        best_ask_volume_etf = max(
            coconut_best_ask_volume/2, -pina_colada_best_bid_volume)
        best_bid_etf = 2*coconut_best_bid - pina_colada_best_ask
        best_bid_volume_etf = min(
            coconut_best_bid_volume/2, -pina_colada_best_ask_volume)

        if len(pina_colada_order_depth.sell_orders) > 0 and len(pina_colada_order_depth.buy_orders) > 0 and len(coconut_order_depth.sell_orders) > 0 and len(coconut_order_depth.buy_orders) > 0:
            if best_ask_etf <= 1000:  # 都买

                orders1.append(Order('COCONUTS', coconut_best_ask, int(
                    min(-best_ask_volume_etf*2, legal_buy_vol_coco))))
                legal_sell_vol_coco -= int(min(-best_ask_volume_etf *
                                           2, legal_buy_vol_coco))
                legal_buy_vol_coco -= int(min(-best_ask_volume_etf *
                                          2, legal_buy_vol_coco))

                orders2.append(Order('PINA_COLADAS', pina_colada_best_ask, int(
                    min(-pina_colada_best_ask_volume, legal_buy_vol_pina))))
                legal_sell_vol_pina -= int(
                    min(-pina_colada_best_ask_volume, legal_buy_vol_pina))
                legal_buy_vol_pina -= int(
                    min(-pina_colada_best_ask_volume, legal_buy_vol_pina))

            if best_bid_etf >= 1000:  # 都卖

                orders1.append(Order('COCONUTS', coconut_best_bid, int(
                    max(-best_bid_volume_etf*2, legal_sell_vol_coco))))

                legal_buy_vol_coco -= int(max(-best_bid_volume_etf *
                                          2, legal_sell_vol_coco))
                legal_sell_vol_coco -= int(max(-best_bid_volume_etf *
                                           2, legal_sell_vol_coco))

                orders2.append(Order('PINA_COLADAS', pina_colada_best_bid, int(
                    max(-pina_colada_best_bid_volume, legal_sell_vol_pina))))
                legal_buy_vol_pina -= int(
                    max(-pina_colada_best_bid_volume, legal_sell_vol_pina))
                legal_sell_vol_pina -= int(
                    max(-pina_colada_best_bid_volume, legal_sell_vol_pina))

            if best_ask_etf-1 >= 1000:
                orders1.append(
                    Order('COCONUTS', coconut_best_ask-1, legal_sell_vol_coco))

            if best_bid_etf+1 <= 1000:
                orders1.append(
                    Order('COCONUTS', coconut_best_ask+1, legal_buy_vol_coco))

        result['COCONUTS'] = orders1
        result['PINA_COLADAS'] = orders2

        logger.flush(state, result)
        return result
