from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any, List
import jsonpickle as json

class Trader:
    def __init__(self):
        self.position_limit = {"ORCHIDS": 100}  # Maximum position limit for ORCHIDS
        self.positions = {"ORCHIDS": 0}  # Current position in ORCHIDS

    def run(self, state: TradingState):
        result = {}
        orders = []
        conversions = 0  # This will be used to indicate how much we want to convert (sell) to the other island
        print(f"Current state: {state}")
        
        # Current state updates
        order_depth = state.order_depths["ORCHIDS"]
        self.buy_orders = order_depth.buy_orders
        self.sell_orders = order_depth.sell_orders
        self.bidPrice = max(order_depth.buy_orders.keys(), default=0)
        self.askPrice = min(order_depth.sell_orders.keys(), default=float('inf'))
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
        print(f"Local ask price: {self.askPrice}, Other island's adjusted bid price: {adjusted_conversion_bid}")
        print(f"Local bid price: {self.bidPrice}, Other island's adjusted ask price: {adjusted_conversion_ask}")

        # check position
        print(f"Current position: {self.positions['ORCHIDS']}")

        # maintaining position to avoid position limits
        conversions = -(self.positions['ORCHIDS'] + 1)

        # arbitrage opportunity
        if self.bidPrice > adjusted_conversion_ask + 0.5:
            # Calculate quantity to buy based on position limits
            print(f"Arbitrage opportunity found! Selling on Local island")

            quantity_to_sell = min(self.position_limit['ORCHIDS'] + self.positions['ORCHIDS'], order_depth.buy_orders[self.bidPrice])
            if quantity_to_sell> 0:
                orders.append(Order("ORCHIDS", self.bidPrice, -quantity_to_sell))
                print(f"Sellinging {quantity_to_sell} ORCHIDS at price {self.bidPrice}")
                self.positions['ORCHIDS'] -= quantity_to_sell

                conversions = quantity_to_sell




        result["ORCHIDS"] = orders
        traderData = "Updated trader data to maintain state across runs"  # Store any state data if needed
        # update position information
        self.positions['ORCHIDS'] += conversions
        print(f"Result: {result}, Conversions: {conversions}, Trader Data: {traderData}")

        return result, conversions, traderData