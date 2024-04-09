
import json
from datamodel import Order, ProsperityEncoder, Symbol, TradingState, OrderDepth
from typing import Any, Dict, List


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
        self.position_limit = {"PEARLS": 20, "BANANAS": 20, 'COCONUTS': 600, 'PINA_COLADAS': 300, 'BERRIES': 250,
                               'DIVING_GEAR': 50, 'DOLPHIN_SIGHTINGS': 0, 'PICNIC_BASKET': 70, 'UKULELE': 70, 'DIP': 300, 'BAGUETTE': 150}
        self.last_mid_price = {'PEARLS': 10000, 'BANANAS': 4900, 'COCONUTS': 8000, 'PINA_COLADAS': 15000, 'BERRIES': 4000,
                               'DIVING_GEAR': 10000, 'DOLPHIN_SIGHTINGS': 0, 'PICNIC_BASKET': 73000, 'UKULELE': 21000, 'DIP': 7000, 'BAGUETTE': 12000}
        self.acceptable_price = {'PEARLS': 10000, 'BANANAS': 5000, 'COCONUTS': 8000, 'PINA_COLADAS': 15000, 'BERRIES': 4000,
                                 'DIVING_GEAR': 10000, 'DOLPHIN_SIGHTINGS': 0, 'PICNIC_BASKET': 73000, 'UKULELE': 21000, 'DIP': 7000, 'BAGUETTE': 12000}
        self.legal_buy_vol = {'PEARLS': 20, 'BANANAS': 20, 'COCONUTS': 600, 'PINA_COLADAS': 300, 'BERRIES': 250,
                              'DIVING_GEAR': 50, 'DOLPHIN_SIGHTINGS': 0, 'PICNIC_BASKET': 70, 'UKULELE': 70, 'DIP': 300, 'BAGUETTE': 150}
        self.legal_sell_vol = {'PEARLS': -20, 'BANANAS': -20, 'COCONUTS': -600, 'PINA_COLADAS': -300, 'BERRIES': -250,
                               'DIVING_GEAR': -50, 'DOLPHIN_SIGHTINGS': 0, 'PICNIC_BASKET': -70, 'UKULELE': -70, 'DIP': -300, 'BAGUETTE': -150}
        self.current_position = {'PEARLS': 0, 'BANANAS': 0, 'COCONUTS': 0, 'PINA_COLADAS': 0, 'BERRIES': 0,
                                 'DIVING_GEAR': 0, 'DOLPHIN_SIGHTINGS': 0, 'PICNIC_BASKET': 0, 'UKULELE': 0, 'DIP': 0, 'BAGUETTE': 0}
        self.last_sign = 0
        self.signal_expire = 0

        self.premium = 379

        # ETF INVENTORY
        self.etf_ask = {'PEARLS': 0, 'BANANAS': 0, 'COCONUTS': 0, 'PINA_COLADAS': 0, 'BERRIES': 0,
                        'DIVING_GEAR': 0, 'DOLPHIN_SIGHTINGS': 0, 'PICNIC_BASKET': 0, 'UKULELE': 0, 'DIP': 0, 'BAGUETTE': 0}
        self.etf_bid = {'PEARLS': 0, 'BANANAS': 0, 'COCONUTS': 0, 'PINA_COLADAS': 0, 'BERRIES': 0,
                        'DIVING_GEAR': 0, 'DOLPHIN_SIGHTINGS': 0, 'PICNIC_BASKET': 0, 'UKULELE': 0, 'DIP': 0, 'BAGUETTE': 0}

        # store the orderbook depth 1 for each product
        self.best_bid = {'PEARLS': 0, 'BANANAS': 0, 'COCONUTS': 0, 'PINA_COLADAS': 0, 'BERRIES': 0,
                         'DIVING_GEAR': 0, 'DOLPHIN_SIGHTINGS': 0, 'PICNIC_BASKET': 0, 'UKULELE': 0, 'DIP': 0, 'BAGUETTE': 0}
        self.best_ask = {'PEARLS': 0, 'BANANAS': 0, 'COCONUTS': 0, 'PINA_COLADAS': 0, 'BERRIES': 0,
                         'DIVING_GEAR': 0, 'DOLPHIN_SIGHTINGS': 0, 'PICNIC_BASKET': 0, 'UKULELE': 0, 'DIP': 0, 'BAGUETTE': 0}
        self.best_bid_volume = {'PEARLS': 0, 'BANANAS': 0, 'COCONUTS': 0, 'PINA_COLADAS': 0, 'BERRIES': 0,
                                'DIVING_GEAR': 0, 'DOLPHIN_SIGHTINGS': 0, 'PICNIC_BASKET': 0, 'UKULELE': 0, 'DIP': 0, 'BAGUETTE': 0}
        self.best_ask_volume = {'PEARLS': 0, 'BANANAS': 0, 'COCONUTS': 0, 'PINA_COLADAS': 0, 'BERRIES': 0,
                                'DIVING_GEAR': 0, 'DOLPHIN_SIGHTINGS': 0, 'PICNIC_BASKET': 0, 'UKULELE': 0, 'DIP': 0, 'BAGUETTE': 0}

        self.imbalance_threshold = {'PEARLS': 15, 'BANANAS': 15,
                          'BERRIES': 30, 'PICNIC_BASKET': 9}

    def market_status(self, product) -> int:

        # banana*1, pearl*2, berries *0.5,picnic * 3
        # 异常处理
        if product not in self.imbalance_threshold.keys(): return 0

        N = self.imbalance_threshold[product]

        if self.best_ask_volume[product] !=0 and self.best_bid_volume[product] !=0:

            best_ask_volume = self.best_ask_volume[product]
            best_bid_volume = self.best_bid_volume[product]
            if -best_ask_volume > N and best_bid_volume <= N:
                return -1
            elif -best_ask_volume <= N and best_bid_volume > N:
                return 1
            else:
                return 0

    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        result = {}


        # generate signal for the diving gear
        dolphin_sightings = state.observations['DOLPHIN_SIGHTINGS']
        dolphin_sightings_diff = dolphin_sightings - \
            self.last_mid_price['DOLPHIN_SIGHTINGS'] if self.last_mid_price['DOLPHIN_SIGHTINGS'] != 0 else 0
        
        self.last_mid_price['DOLPHIN_SIGHTINGS'] = dolphin_sightings

        instant_signal = 1 if dolphin_sightings_diff > 5 else - \
            1 if dolphin_sightings_diff < -5 else 0

        # we save the dg_signal for 900 steps

        if instant_signal == 1:
            self.last_sign = 1
            self.signal_expire = state.timestamp + 900*100
        elif instant_signal == -1:
            self.last_sign = -1
            self.signal_expire = state.timestamp + 900*100
        else:
            if state.timestamp > self.signal_expire:
                self.last_sign = 0
            else:
                # 不更改last sign 继续记忆上一个instant signal
                pass

        # read orderbook to get 
        # - position limit
        # -orderbook depth 1
        # -mid price

        for product in state.order_depths.keys():
            current_position = 0 if product not in state.position.keys() else state.position[product]

            legal_buy_vol = self.position_limit[product] - current_position
            legal_sell_vol = -self.position_limit[product] - current_position
        
            # orderbook information and mid price
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
                # mid_price = (avg_sell_price + avg_buy_price)/2 weighted bid weighted ask/2
                buy_order_volume = sum([order_depth.buy_orders[i]
                                       for i in order_depth.buy_orders.keys()])
                sell_order_volume = sum(
                    [-order_depth.sell_orders[i] for i in order_depth.sell_orders.keys()])
                mid_price = (avg_sell_price * buy_order_volume + avg_buy_price *
                             sell_order_volume)/(buy_order_volume + sell_order_volume)

            elif len(order_depth.sell_orders) == 0 and len(order_depth.buy_orders) != 0:  # 只有买单
                best_ask = 0
                best_ask_volume = 0
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                mid_price = self.last_mid_price[product]
            elif len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) == 0:  # 只有卖单
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
            self.current_position[product] = current_position

        # C vs PC pair trading
        etf_coco_pina_ask = max(
            self.best_ask_volume['COCONUTS']/2, -self.best_bid_volume['PINA_COLADAS'])
        etf_coco_pina_bid = min(
            self.best_bid_volume['COCONUTS']/2, -self.best_ask_volume['PINA_COLADAS'])
        self.best_ask_volume['COCONUTS'] = etf_coco_pina_ask * 2
        self.best_bid_volume['COCONUTS'] = etf_coco_pina_bid * 2
        self.best_ask_volume['PINA_COLADAS'] = -etf_coco_pina_bid
        self.best_bid_volume['PINA_COLADAS'] = -etf_coco_pina_ask

        # PB vs BDU pair trading
        etf_picnic_ask = max(self.best_ask_volume['BAGUETTE']/2, self.best_ask_volume['DIP']/4,
                             self.best_ask_volume['UKULELE'], -self.best_bid_volume['PICNIC_BASKET'])
        etf_picnic_bid = min(self.best_bid_volume['BAGUETTE']/2, self.best_bid_volume['DIP']/4,
                             self.best_bid_volume['UKULELE'], -self.best_ask_volume['PICNIC_BASKET'])
        self.best_ask_volume['BAGUETTE'] = etf_picnic_ask * 2
        self.best_bid_volume['BAGUETTE'] = etf_picnic_bid * 2
        self.best_ask_volume['DIP'] = etf_picnic_ask * 4
        self.best_bid_volume['DIP'] = etf_picnic_bid * 4
        self.best_ask_volume['UKULELE'] = etf_picnic_ask
        self.best_bid_volume['UKULELE'] = etf_picnic_bid
        self.best_ask_volume['PICNIC_BASKET'] = -etf_picnic_bid
        self.best_bid_volume['PICNIC_BASKET'] = -etf_picnic_ask

        # for each product, we calculate the acceptable price,
        for product in state.order_depths.keys():
            # the relationship between coconut and pina colada linear with intercept, 2*coconut = pina colada+1000

            if product == 'PEARLS':
                market_status = self.market_status(product)
                self.acceptable_price[product] = self.last_mid_price[product] + \
                    2*market_status
            elif product == 'BANANAS':
                market_status = self.market_status(product)
                self.acceptable_price[product] = self.last_mid_price[product] + \
                    1*market_status
            elif product == 'BERRIES':
                market_status = self.market_status(product)
                self.acceptable_price[product] = self.last_mid_price[product] + \
                    0.5 * market_status

            elif product == 'COCONUTS':
                self.acceptable_price[product] = (
                    self.last_mid_price['PINA_COLADAS']+1000)
            elif product == 'PINA_COLADAS':
                self.acceptable_price[product] = (
                    (self.last_mid_price['COCONUTS']*2-1000))
            elif product == 'DIVING_GEAR':
                self.acceptable_price[product] = self.last_mid_price[product]

            elif product == 'BAGUETTE':
                self.acceptable_price[product] = (self.last_mid_price[product] + (
                    (self.last_mid_price['PICNIC_BASKET'] - self.premium - 4*self.last_mid_price['DIP'] - 1*self.last_mid_price['UKULELE'])/2))/2

            elif product == 'DIP':
                self.acceptable_price[product] = (self.last_mid_price[product] + ((self.last_mid_price['PICNIC_BASKET'] -
                                                  self.premium - 2*self.last_mid_price['BAGUETTE'] - 1*self.last_mid_price['UKULELE'])/4))/2

            elif product == 'UKULELE':
                self.acceptable_price[product] = (self.last_mid_price[product] + (
                    self.last_mid_price['PICNIC_BASKET'] - self.premium - 2*self.last_mid_price['BAGUETTE'] - 4*self.last_mid_price['DIP']))/2

            elif product == 'PICNIC_BASKET':
                market_status = self.market_status(product)
                self.acceptable_price[product] = (self.last_mid_price[product] + (2*self.last_mid_price['BAGUETTE'] +
                                                  4*self.last_mid_price['DIP'] + self.last_mid_price['UKULELE'] + self.premium))/2 + 3 * market_status

            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []

            # get acceptable price, legal buy volume and legal sell volume from the init

            acceptable_price = self.acceptable_price[product]
            legal_buy_vol = self.legal_buy_vol[product]
            legal_sell_vol = self.legal_sell_vol[product]
            
            if product == 'BERRIES':
                if state.timestamp >= 250000 and state.timestamp < 280000:
                    if legal_buy_vol > 0 and self.best_ask_volume[product] != 0:
                        best_ask = self.best_ask[product]
                        best_ask_volume = self.best_ask_volume[product]
                        orders.append(Order(product, best_ask, int(
                            min(-best_ask_volume, legal_buy_vol))))
                        legal_sell_vol = legal_sell_vol - \
                            int(min(-best_ask_volume, legal_buy_vol))
                        legal_buy_vol = legal_buy_vol - \
                            int(min(-best_ask_volume, legal_buy_vol))
                    result[product] = orders
                elif state.timestamp >= 550000 and state.timestamp < 580000:
                    if legal_sell_vol < 0 and self.best_bid_volume[product] != 0:
                        best_bid = self.best_bid[product]
                        best_bid_volume = self.best_bid_volume[product]
                        orders.append(Order(product, best_bid, int(
                            max(-best_bid_volume, legal_sell_vol))))
                        legal_buy_vol = legal_buy_vol - \
                            int(max(-best_bid_volume, legal_sell_vol))
                        legal_sell_vol = legal_sell_vol - \
                            int(max(-best_bid_volume, legal_sell_vol))
                    result[product] = orders
                elif state.timestamp >= 750000 and state.timestamp < 780000:
                    if state.position[product] < 0:
                        best_ask = self.best_ask[product]
                        best_ask_volume = self.best_ask_volume[product]
                        orders.append(Order(product, best_ask, int(
                            min(-best_ask_volume, -state.position[product]))))
                    result[product] = orders

            elif product == 'DIVING_GEAR':
                if self.last_sign == 1:
                    # max long position when the last sign remains positive
                    if legal_buy_vol > 0 and self.best_ask_volume[product] != 0:
                        best_ask = self.best_ask[product]
                        best_ask_volume = self.best_ask_volume[product]
                        orders.append(Order(product, best_ask, int(
                            min(-best_ask_volume, legal_buy_vol))))
                        legal_sell_vol = legal_sell_vol - \
                            int(min(-best_ask_volume, legal_buy_vol))
                        legal_buy_vol = legal_buy_vol - \
                            int(min(-best_ask_volume, legal_buy_vol))
                    result[product] = orders

                elif self.last_sign == -1:
                    # max short position when the last sign remains negative
                    if legal_sell_vol < 0 and self.best_bid_volume[product] != 0:
                        best_bid = self.best_bid[product]
                        best_bid_volume = self.best_bid_volume[product]
                        orders.append(Order(product, best_bid, int(
                            max(-best_bid_volume, legal_sell_vol))))
                        legal_buy_vol = legal_buy_vol - \
                            int(max(-best_bid_volume, legal_sell_vol))
                        legal_sell_vol = legal_sell_vol - \
                            int(max(-best_bid_volume, legal_sell_vol))
                    result[product] = orders

                else:
                    # last signal = 0, 我们的directional 信号已经过期了，需要清仓
                    if self.current_position[product] < 0:
                        best_ask = self.best_ask[product]
                        best_ask_volume = self.best_ask_volume[product]
                        orders.append(Order(product, best_ask, int(
                            min(-best_ask_volume, -state.position[product]))))
                    elif self.current_position[product] > 0:
                        best_bid = self.best_bid[product]
                        best_bid_volume = self.best_bid_volume[product]
                        orders.append(Order(product, best_bid, int(
                            max(-best_bid_volume, -state.position[product]))))
                    else:
                        pass
                    result[product] = orders

            elif product == 'BANANAS' or product =='PEALRS':
                # 双边都有挂单
                if self.best_ask_volume[product] != 0 and self.best_bid_volume[product] != 0:
                    best_ask = self.best_ask[product]
                    best_ask_volume = self.best_ask_volume[product]
                    best_bid = self.best_bid[product]
                    best_bid_volume = self.best_bid_volume[product]
                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    # taker strategy
                    # TODO：两个 buy order 可能同时发单，两个 sell order 也可能同时发单

                    if best_ask <= acceptable_price:  # 卖得低，take the sell order on the orderbook as much as possible
                        orders.append(Order(product, best_ask, int(
                            min(-best_ask_volume, legal_buy_vol))))

                        # 因为我们买了，所以我们可以买的量减少，我们可以卖的量增加
                        
                        legal_sell_vol = legal_sell_vol - \
                            int(min(-best_ask_volume, legal_buy_vol))
                        legal_buy_vol = legal_buy_vol - \
                            int(min(-best_ask_volume, legal_buy_vol))

                    if best_bid >= acceptable_price:  # 买得贵，take the buy order on the orderbook as much as possible
                        orders.append(Order(product, best_bid, int(
                            max(-best_bid_volume, legal_sell_vol))))
                        # 因为我们卖了，所以我们可以卖的量减少，我们可以买的量增加
                        legal_buy_vol = legal_buy_vol - \
                            int(max(-best_bid_volume, legal_sell_vol))
                        legal_sell_vol = legal_sell_vol - \
                            int(max(-best_bid_volume, legal_sell_vol))

                    # maker strategy
                    if best_ask - 1 >= acceptable_price:  # orderbook最优卖单足够贵，我们可以以-1的价格仍然卖出获利
                        # make the market by placing a sell order at a price of 1 below the best ask
                        orders.append(
                            Order(product, best_ask - 1, legal_sell_vol))
                    if best_bid + 1 <= acceptable_price:
                        # make the market by placing a buy order at a price of 1 above the best bid
                        orders.append(
                            Order(product, best_bid + 1, legal_buy_vol))

                # 只有买单
                elif self.best_ask_volume[product] == 0 and self.best_bid_volume[product] != 0:
                    best_bid = self.best_bid[product]
                    best_bid_volume = self.best_bid_volume[product]
                    if best_bid >= acceptable_price:
                        orders.append(Order(product, best_bid, int(
                            max(-best_bid_volume, legal_sell_vol))))

                # 只有卖单
                elif self.best_ask_volume[product] != 0 and self.best_bid_volume[product] == 0:
                    best_ask = self.best_ask[product]
                    best_ask_volume = self.best_ask_volume[product]
                    if best_ask <= acceptable_price:
                        orders.append(Order(product, best_ask, int(
                            min(-best_ask_volume, legal_buy_vol))))
                        
            else:
                # PICNIC BASKETS & INGREIENT
                # C & PC
                # TODO: 每次take 的时候要保证仓位是按比例对齐的，不做making
                pass

            # Add all the above the orders to the result dict
            result[product] = orders


        logger.flush(state, result)
        return result
