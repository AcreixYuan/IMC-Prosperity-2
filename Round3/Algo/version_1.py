# score 2.639k
# quick description: we are using the ema for the am, and we are using an 90 10 split for the parameters, varying the N parameter to 20 
# market status added for both, one at 2, one at 1

alpha1 = 1.0;alpha2 =  0.1; N1 = 7; N2 = 30

from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState, UserId, Position, Product
from typing import List, Dict, Any
import numpy as np
import jsonpickle
from collections import deque


import json


from typing import Any

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




    
    


# import parameter_list

class Trader:
    # define data members
    def __init__(self):
        self.position_limit = {"AMETHYSTS": 20, "STARFRUIT": 20,"ORCHIDS": 100, "CHOCOLATE": 250, "STRAWBERRIES" : 350, "ROSES":60, "GIFT_BASKETS":60}
        self.last_mid_price = {'AMETHYSTS': 10000, 'STARFRUIT': 5000}
        self.mid_price = {'AMETHYSTS': {0: 10000}, 'STARFRUIT': {0: 5000}}
        self.ma_price = {'AMETHYSTS': {0: 10000}, 'STARFRUIT': {0: 5000}}
        self.ema_price = {'AMETHYSTS': {0: 10000}, 'STARFRUIT': {0: 5000}}
        self.price_history = {'AMETHYSTS': deque(maxlen=20), 'STARFRUIT': deque(maxlen=20)}  # 设置历史长度为 20
        self.positions = {"ORCHIDS": 0}  # Current position in ORCHIDS
        
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


    def run(self, state: TradingState) -> tuple[dict[Symbol, list[Order]], int, str]: 
        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
            order_depth: OrderDepth = state.order_depths[product]

            if product in state.position.keys():
                current_position = state.position[product]
            else:
                current_position = 0

            legal_buy_vol = np.minimum(self.position_limit[product] - current_position, self.position_limit[product])
            legal_sell_vol = np.maximum(-(self.position_limit[product] + current_position), -self.position_limit[product])

            orders: List[Order] = []
            if product == 'AMETHYSTS':
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                mid_price = (best_ask * np.abs(best_ask_volume) + best_bid * np.abs(best_bid_volume)) / (np.abs(best_ask_volume) + np.abs(best_bid_volume))
                ma_price = self.simple_moving_average(product, mid_price)
                ema_price = (2 * mid_price + (N1 - 1) * self.ema_price[product][list(self.ema_price[product].keys())[-1]]) / (N1 + 1)
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
            elif product == 'STARFRUIT':
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
        
            elif product == 'ORCHIDS':
                conversions = 0  # This will be used to indicate how much we want to convert (sell) to the other island
                logger.print(f"Current state: {state}")
                
                self.buy_orders = order_depth.buy_orders
                self.sell_orders = order_depth.sell_orders

                sorted_bid_prices = sorted(order_depth.buy_orders.keys(), reverse=True)
                sorted_ask_prices = sorted(order_depth.sell_orders.keys())

                self.bidPrice = sorted_bid_prices[0] if len(sorted_bid_prices) > 0 else 0
                self.secondbidPrice = sorted_bid_prices[1] if len(sorted_bid_prices) > 1 else 0
                self.thirdbidPrice = sorted_bid_prices[2] if len(sorted_bid_prices) > 2 else 0

                self.askPrice = sorted_ask_prices[0] if len(sorted_ask_prices) > 0 else float('inf')
                self.secondaskPrice = sorted_ask_prices[1] if len(sorted_ask_prices) > 1 else float('inf')
                self.thirdaskPrice = sorted_ask_prices[2] if len(sorted_ask_prices) > 2 else float('inf')

                self.conversionbid = state.observations.conversionObservations['ORCHIDS'].bidPrice
                self.conversionask = state.observations.conversionObservations['ORCHIDS'].askPrice
                self.transportFees = state.observations.conversionObservations['ORCHIDS'].transportFees
                self.exportTariff = state.observations.conversionObservations['ORCHIDS'].exportTariff
                self.importTariff = state.observations.conversionObservations['ORCHIDS'].importTariff

                # Adjusted conversion prices after accounting for fees and tariffs
                adjusted_conversion_bid = self.conversionbid - (self.transportFees + self.exportTariff) - 0.1
                adjusted_conversion_ask = self.conversionask + (self.transportFees + self.importTariff) + 0.1

                # Finding arbitrage opportunities
                # Buy on local island if local ask price < other island's adjusted bid price
                logger.print(f"Local ask price: {self.askPrice}, Other island's adjusted bid price: {adjusted_conversion_bid}")
                logger.print(f"Local bid price: {self.bidPrice}, Other island's adjusted ask price: {adjusted_conversion_ask}")

                # check position
                logger.print(f"Current position: {self.positions['ORCHIDS']}")

                # maintaining position to avoid position limits
                conversions = -self.positions['ORCHIDS']


                # One-side market making
                self.worst_bidPrice = sorted_bid_prices[-1] if len(sorted_bid_prices) > 0 else 0
                if adjusted_conversion_ask + 2.5 >= self.worst_bidPrice and adjusted_conversion_ask + 2.5 <= self.askPrice:
                    logger.print(f"Market making opportunity found! Selling on Local island. ")
                    # set sell price at adjusted_conversion_ask + 3, place sell order and clear the market above this price
                    # list all the prices above adjusted_conversion_ask + 3
                    prices_above_threshold = self.list_prices_above_threshold(order_depth.buy_orders, adjusted_conversion_ask + 2.5)
                    logger.print(f"Prices above threshold: {prices_above_threshold}")
                    quantity_to_sell = 0
                    if len(prices_above_threshold) > 0:
                        for price in prices_above_threshold:
                            logger.print(f"Selling Price: {price}")
                            quantity_to_sell += order_depth.buy_orders[int(round(price))]
                    if quantity_to_sell > 0:
                        orders.append(Order("ORCHIDS", int(round(adjusted_conversion_ask+2.5)), -quantity_to_sell))
                        logger.print(f"Sellinging {quantity_to_sell} ORCHIDS at price {int(adjusted_conversion_ask+2.5)}")
                        self.positions['ORCHIDS'] -= quantity_to_sell
                        conversions = quantity_to_sell
                        self.positions['ORCHIDS'] += conversions
                
                # the other side of the trade
                self.worst_askPrice = sorted_ask_prices[-1] if len(sorted_ask_prices) > 0 else float('inf')
                if adjusted_conversion_bid - 2 <= self.worst_askPrice and adjusted_conversion_bid - 2 >= self.askPrice:
                    logger.print(f"Market making opportunity found! Buying on Local island. ")
                    # set buy price at adjusted_conversion_bid - 3, place buy order and clear the market below this price
                    # list all the prices below adjusted_conversion_bid - 3
                    prices_below_threshold = self.list_prices_below_threshold(order_depth.sell_orders, adjusted_conversion_bid - 2)
                    logger.print(f"Prices below threshold: {prices_below_threshold}")
                    quantity_to_buy = 0
                    if len(prices_below_threshold) > 0:
                        for price in prices_below_threshold:
                            logger.print(f"Buying Price: {price}")
                            quantity_to_buy += order_depth.sell_orders[int(round(price))]
                    if quantity_to_buy > 0:
                        orders.append(Order("ORCHIDS", int(round(adjusted_conversion_bid-2)), quantity_to_buy))
                        logger.print(f"Buying {quantity_to_buy} ORCHIDS at price {int(adjusted_conversion_bid-2)}")
                        self.positions['ORCHIDS'] += quantity_to_buy
                        conversions = -quantity_to_buy
                        self.positions['ORCHIDS'] -= conversions
                
                '''
                # arbitrage opportunity
                # being more ambitious with three levels of bid prices
                if self.bidPrice > adjusted_conversion_ask + 2:
                    # Calculate quantity to buy based on position limits
                    logger.print(f"Arbitrage opportunity found! Selling on Local island. ")

                    quantity_to_sell = min(self.position_limit['ORCHIDS'] + self.positions['ORCHIDS'], order_depth.buy_orders[self.bidPrice])

                    if self.secondbidPrice > adjusted_conversion_ask + 0.5:
                        quantity_to_sell += min(self.position_limit['ORCHIDS'] + self.positions['ORCHIDS'], order_depth.buy_orders[self.secondbidPrice])
                    
                        if self.thirdbidPrice > adjusted_conversion_ask + 0.25:
                            quantity_to_sell += min(self.position_limit['ORCHIDS'] + self.positions['ORCHIDS'], order_depth.buy_orders[self.thirdbidPrice])

                    if quantity_to_sell> 0:
                        orders.append(Order("ORCHIDS", self.bidPrice, -quantity_to_sell))
                        logger.print(f"Sellinging {quantity_to_sell} ORCHIDS at price {self.bidPrice}")
                        self.positions['ORCHIDS'] -= quantity_to_sell

                        conversions = -quantity_to_sell
                        self.positions['ORCHIDS'] += conversions
                
                # other side of the trade
                if self.askPrice < adjusted_conversion_bid - 1:
                    # Calculate quantity to buy based on position limits
                    logger.print(f"Arbitrage opportunity found! Buying on Local island. ")

                    quantity_to_buy = min(self.position_limit['ORCHIDS'] + self.positions['ORCHIDS'], order_depth.sell_orders[self.askPrice])

                    if self.secondaskPrice < adjusted_conversion_bid - 0.5:
                        quantity_to_buy += min(self.position_limit['ORCHIDS'] + self.positions['ORCHIDS'], order_depth.sell_orders[self.secondaskPrice])
                    
                        if self.thirdaskPrice < adjusted_conversion_bid - 0.25:
                            quantity_to_buy += min(self.position_limit['ORCHIDS'] + self.positions['ORCHIDS'], order_depth.sell_orders[self.thirdaskPrice])

                    if quantity_to_buy> 0:
                        orders.append(Order("ORCHIDS", self.askPrice, quantity_to_buy))
                        logger.print(f"Buying {quantity_to_buy} ORCHIDS at price {self.askPrice}")
                        self.positions['ORCHIDS'] += quantity_to_buy

                        conversions = quantity_to_buy
                        self.positions['ORCHIDS'] -= conversions
                '''



                result[product] = orders
                traderData = "Updated trader data to maintain state across runs"  # Store any state data if needed
                # update position information
                self.positions[product] += conversions
                logger.print(f"Result: {result}, Conversions: {conversions}, Trader Data: {traderData}")
            elif product == 'STRAWBERRIES':
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []
                acceptable_price = 10  # Participant should calculate this value
                logger.print("Acceptable price : " + str(acceptable_price))
                logger.print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
        
                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    if int(best_ask) < acceptable_price:
                        logger.print("BUY", str(-best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_amount))
        
                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    if int(best_bid) > acceptable_price:
                        logger.print("SELL", str(best_bid_amount) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_amount))
                
                result[product] = orders
            elif product == 'CHOCOLATE':
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []
                acceptable_price = 10  # Participant should calculate this value
                logger.print("Acceptable price : " + str(acceptable_price))
                logger.print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
        
                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    if int(best_ask) < acceptable_price:
                        logger.print("BUY", str(-best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_amount))
        
                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    if int(best_bid) > acceptable_price:
                        logger.print("SELL", str(best_bid_amount) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_amount))
                
                result[product] = orders
            elif product == 'ROSES':
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []
                acceptable_price = 10  # Participant should calculate this value
                logger.print("Acceptable price : " + str(acceptable_price))
                logger.print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
        
                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    if int(best_ask) < acceptable_price:
                        logger.print("BUY", str(-best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_amount))
        
                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    if int(best_bid) > acceptable_price:
                        logger.print("SELL", str(best_bid_amount) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_amount))
                
                result[product] = orders
            elif product == 'GIFT_BASKETS':
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []
                acceptable_price = 10  # Participant should calculate this value
                logger.print("Acceptable price : " + str(acceptable_price))
                logger.print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
        
                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    if int(best_ask) < acceptable_price:
                        logger.print("BUY", str(-best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_amount))
        
                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    if int(best_bid) > acceptable_price:
                        logger.print("SELL", str(best_bid_amount) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_amount))
                
                result[product] = orders
                
        self.last_mid_price = {'AMETHYSTS': 10000, 'STARFRUIT': 5000}
        # String value holding Trader state data required.
        # It will be delivered as TradingState.traderData on next execution.
        traderData = ""

        # = 1
        logger.flush(state, result, conversions, traderData)
        return result, conversions, traderData


logger = Logger()