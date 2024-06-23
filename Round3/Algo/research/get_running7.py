import json
from datamodel import Listing, UserId, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any
from typing import List
import string
from collections import deque
import numpy as np

alpha1 = 1.0;alpha2 =  0.1; N1 = 7; N2 = 30

class Logger:
    def __init__(self) -> None:
        self.logs = ""
        self.max_log_length = 3750

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
        base_length = len(self.to_json([
            self.compress_state(state, ""),
            self.compress_orders(orders),
            conversions,
            "",
            "",
        ]))

        # We truncate state.traderData, trader_data, and self.logs to the same max. length to fit the log limit
        max_item_length = (self.max_log_length - base_length) // 3

        print(self.to_json([
            self.compress_state(state, self.truncate(state.traderData, max_item_length)),
            self.compress_orders(orders),
            conversions,
            self.truncate(trader_data, max_item_length),
            self.truncate(self.logs, max_item_length),
        ]))

        self.logs = ""

    def compress_state(self, state: TradingState, trader_data: str) -> list[Any]:
        return [
            state.timestamp,
            trader_data,
            self.compress_listings(state.listings),
            self.compress_order_depths(state.order_depths),
            self.compress_trades(state.own_trades),
            self.compress_trades(state.market_trades),
            state.position,
            self.compress_observations(state.observations),
        ]

    def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
        compressed = []
        for listing in listings.values():
            compressed.append([listing["symbol"], listing["product"], listing["denomination"]])

        return compressed

    def compress_order_depths(self, order_depths: dict[Symbol, OrderDepth]) -> dict[Symbol, list[Any]]:
        compressed = {}
        for symbol, order_depth in order_depths.items():
            compressed[symbol] = [order_depth.buy_orders, order_depth.sell_orders]

        return compressed

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append([
                    trade.symbol,
                    trade.price,
                    trade.quantity,
                    trade.buyer,
                    trade.seller,
                    trade.timestamp,
                ])

        return compressed

    def compress_observations(self, observations: Observation) -> list[Any]:
        conversion_observations = {}
        for product, observation in observations.conversionObservations.items():
            conversion_observations[product] = [
                observation.bidPrice,
                observation.askPrice,
                observation.transportFees,
                observation.exportTariff,
                observation.importTariff,
                observation.sunlight,
                observation.humidity,
            ]

        return [observations.plainValueObservations, conversion_observations]

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])

        return compressed

    def to_json(self, value: Any) -> str:
        return json.dumps(value, cls=ProsperityEncoder, separators=(",", ":"))

    def truncate(self, value: str, max_length: int) -> str:
        if len(value) <= max_length:
            return value

        return value[:max_length - 3] + "..."

logger = Logger()

class Trader:
    def __init__(self):
        self.position_limit = {"AMETHYSTS": 20, "STARFRUIT": 20, "ORCHIDS": 100, "CHOCOLATE": 250, "STRAWBERRIES": 350, "ROSES": 60, "GIFT_BASKET": 60}
        self.last_mid_price = {'AMETHYSTS': 10000, 'STARFRUIT': 5000}
        self.mid_price = {'AMETHYSTS': {0: 10000}, 'STARFRUIT': {0: 5000}, 'CHOCOLATE':{0: 8000},
                          'STRAWBERRIES': {0: 4000},'ROSES': {0: 15000},'GIFT_BASKET':{0: 71350}}
        self.ma_price = {'AMETHYSTS': {0: 10000}, 'STARFRUIT': {0: 5000}}
        self.ema_price = {'AMETHYSTS': {0: 10000}, 'STARFRUIT': {0: 5000}}
        self.price_history = {'AMETHYSTS': deque(maxlen=20), 'STARFRUIT': deque(maxlen=20),
                              'CHOCOLATE':deque(maxlen=200), "STRAWBERRIES": deque(maxlen=200),
                              "ROSES": deque(maxlen=200), "GIFT_BASKET": deque(maxlen=200) }  # 设置历史长度为 20
        self.positions = {"ORCHIDS": 0, "AMETHYSTS": 0, "STARFRUIT": 0,  "CHOCOLATE": 0, "STRAWBERRIES": 0, "ROSES": 0, "GIFT_BASKET": 0}

    def market_status(self, state: TradingState, product) -> int:
        order_depth: OrderDepth = state.order_depths[product]
        if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
            best_ask_volume = order_depth.sell_orders[min(order_depth.sell_orders.keys())]
            best_bid_volume = order_depth.buy_orders[max(order_depth.buy_orders.keys())]
            if best_ask_volume >= 15 and best_bid_volume <15:
                return -1
            elif best_ask_volume < 15 and best_bid_volume >=15:
                return 1
            else:
                return 0

    def simple_moving_average(self, product, price):
        self.price_history[product].append(price)
        if len(self.price_history[product]) > 0:
            return sum(self.price_history[product]) / len(self.price_history[product])
        return price

    def list_prices_above_threshold(self, price_dict, threshold):
        """ Returns a list of prices that are above the specified threshold """
        return [price for price in sorted(price_dict.keys()) if price >= threshold]

    def list_prices_below_threshold(self, price_dict, threshold):
        """ Returns a list of prices that are below the specified threshold """
        return [price for price in sorted(price_dict.keys(), reverse=True) if price <= threshold]

    def run(self, state: TradingState):
        logger.print("traderData: " + state.traderData)
        logger.print("Observations: " + str(state.observations))


        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            if product in state.position.keys():
                current_position = state.position[product]
            else:
                current_position = 0

            legal_buy_vol = np.minimum(self.position_limit[product] - current_position, self.position_limit[product])
            legal_sell_vol = np.maximum(-(self.position_limit[product] + current_position),
                                        -self.position_limit[product])

            orders: List[Order] = []
            if product=='AMETHYSTS':
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                mid_price = (best_ask * np.abs(best_ask_volume) + best_bid * np.abs(best_bid_volume)) / (
                            np.abs(best_ask_volume) + np.abs(best_bid_volume))
                ma_price = self.simple_moving_average(product, mid_price)
                ema_price = (2 * mid_price + (N1 - 1) * self.ema_price[product][
                    list(self.ema_price[product].keys())[-1]]) / (N1 + 1)
                self.mid_price[product][state.timestamp] = mid_price
                self.ma_price[product][state.timestamp] = ma_price
                self.ema_price[product][state.timestamp] = ema_price

                # market status
                market_status = self.market_status(state, product)

                acceptable_price = ema_price + 2 * market_status

                if len(order_depth.sell_orders) > 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    if best_ask <= acceptable_price:
                        logger.print("BUY", str(-best_ask_volume) + "x", best_ask)
                        orders.append(Order(product, best_ask, int(np.minimum(-best_ask_volume, legal_buy_vol))))
                    if best_bid + 1 <= acceptable_price:
                        logger.print("BUY", str(-best_ask_volume) + "x", best_bid + 1)
                        orders.append(Order(product, best_bid + 1, int(np.minimum(-best_ask_volume, legal_buy_vol))))

                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid >= acceptable_price:
                        logger.print("SELL", str(best_bid_volume) + "x", best_bid)
                        orders.append(Order(product, best_bid, int(np.maximum(-best_bid_volume, legal_sell_vol))))
                    if best_ask - 1 >= acceptable_price:
                        logger.print("SELL", str(-best_bid_volume) + "x", best_ask - 1)
                        orders.append(Order(product, best_ask - 1, int(np.minimum(-best_bid_volume, legal_sell_vol))))

                result[product] = orders
            elif product=='STARFRUIT':
                #logger.print('STARFRUIT')
                if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    avg_buy_price = sum([np.abs(order_depth.buy_orders[i]) * i for i in order_depth.buy_orders.keys()])/sum([np.abs(order_depth.buy_orders[i]) for i in order_depth.buy_orders.keys()])
                    avg_sell_price = sum([np.abs(order_depth.sell_orders[i]) * i for i in order_depth.sell_orders.keys()])/sum([np.abs(order_depth.sell_orders[i]) for i in order_depth.sell_orders.keys()])
                    mid_price = (avg_sell_price + avg_buy_price)/2
                    ma_price = self.simple_moving_average(product, mid_price)
                    ema_price = (2 * mid_price + (N2 - 1) * self.ema_price[product][list(self.ema_price[product].keys())[-1]]) / (N2 + 1)
                    self.ma_price[product][state.timestamp] = ma_price
                    self.ema_price[product][state.timestamp] = ema_price
                else:
                    mid_price = self.last_mid_price[product]
                self.last_mid_price[product] = mid_price
                acceptable_price = alpha2 * ema_price + (1 - alpha2)*mid_price + market_status

                if len(order_depth.sell_orders) > 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    if best_ask <= acceptable_price:
                        logger.print("BUY", str(-best_ask_volume) + "x", best_ask)
                        orders.append(Order(product, best_ask, int(np.minimum(-best_ask_volume, legal_buy_vol))))
                    if best_bid + 1 <= acceptable_price:
                        logger.print("BUY", str(-best_ask_volume) + "x", best_bid + 1)
                        orders.append(Order(product, best_bid + 1, int(np.minimum(-best_ask_volume, legal_buy_vol))))

                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid >= acceptable_price:
                        logger.print("SELL", str(best_bid_volume) + "x", best_bid)
                        orders.append(Order(product, best_bid, int(np.maximum(-best_bid_volume, legal_sell_vol))))
                    if best_ask - 1 >= acceptable_price:
                        logger.print("SELL", str(-best_bid_volume) + "x", best_ask - 1)
                        orders.append(Order(product, best_ask - 1, int(np.minimum(-best_bid_volume, legal_sell_vol))))

                result[product] = orders
            elif product=='ORCHIDS':
                #TODO: fill out this part later with Suyang's Cptimal Code
                logger.print('ORCHIDS')
            elif product=='CHOCOLATE':
                #get the logging started, print when you get arbitrage opportunities
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                mid_price = (best_ask * np.abs(best_ask_volume) + best_bid * np.abs(best_bid_volume)) / (
                            np.abs(best_ask_volume) + np.abs(best_bid_volume))
                self.mid_price[product][state.timestamp] = mid_price

            elif product=='STRAWBERRIES':
                #get the logging started, print when you get arbitrage opportunities
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                mid_price = (best_ask * np.abs(best_ask_volume) + best_bid * np.abs(best_bid_volume)) / (
                            np.abs(best_ask_volume) + np.abs(best_bid_volume))
                self.mid_price[product][state.timestamp] = mid_price
            elif product=='ROSES':
                #get the logging started, print when you get arbitrage opportunities
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                mid_price = (best_ask * np.abs(best_ask_volume) + best_bid * np.abs(best_bid_volume)) / (
                            np.abs(best_ask_volume) + np.abs(best_bid_volume))
                self.mid_price[product][state.timestamp] = mid_price
            elif product=='GIFT_BASKETS':
                # get the logging started, print when you get arbitrage opportunities
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                mid_price = (best_ask * np.abs(best_ask_volume) + best_bid * np.abs(best_bid_volume)) / (
                        np.abs(best_ask_volume) + np.abs(best_bid_volume))
                acceptable_price =
                self.mid_price[product][state.timestamp] = mid_price

		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        trader_data = "SAMPLE" 
        
				# Sample conversion request. Check more details below. 
        conversions = 1

        logger.flush(state, result, conversions, trader_data)
        return result, conversions, trader_data
