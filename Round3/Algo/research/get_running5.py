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
        self.mid_price = {'AMETHYSTS': {0: 10000}, 'STARFRUIT': {0: 5000}}
        self.ma_price = {'AMETHYSTS': {0: 10000}, 'STARFRUIT': {0: 5000}}
        self.ema_price = {'AMETHYSTS': {0: 10000}, 'STARFRUIT': {0: 5000}}
        self.price_history = {'AMETHYSTS': deque(maxlen=20), 'STARFRUIT': deque(maxlen=20)}  # 设置历史长度为 20
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

    def run(self, state: TradingState):
        logger.print("traderData: " + state.traderData)
        logger.print("Observations: " + str(state.observations))


        result = {}
        for product in state.order_depths:
            if product in state.position.keys():
                current_position = state.position[product]
            else:
                current_position = 0

            legal_buy_vol = np.minimum(self.position_limit[product] - current_position, self.position_limit[product])
            legal_sell_vol = np.maximum(-(self.position_limit[product] + current_position),
                                        -self.position_limit[product])

            orders: List[Order] = []
            if product=='AMETHYSTS':
                logger.print('AMETHYSTS')
            elif product=='STARFRUIT':
                logger.print('STARFRUIT')
            elif product=='ORCHIDS':
                logger.print('ORCHIDS')
            elif product=='CHOCOLATE':
                logger.print('CHOCOLATE')
            elif product=='STRAWBERRIES':
                logger.print('STRAWBERRIES')
            elif product=='ROSES':
                logger.print('ROSES')
            elif product=='GIFT_BASKETS':
                logger.print('GIFT_BASKETS')

		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        trader_data = "SAMPLE" 
        
				# Sample conversion request. Check more details below. 
        conversions = 1

        logger.flush(state, result, conversions, trader_data)
        return result, conversions, trader_data
