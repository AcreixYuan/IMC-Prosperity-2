from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

class Trader:
    def __init__(self):
        self.position_limit = {"ORCHIDS": 100}
        self.last_mid_price = {'ORCHIDS': 1100}
        self.mid_price = {'ORCHIDS': {0: 1100}}
        self.transportFees = 0
        self.exportTariff = 0
        self.importTariff = 0
        self.sunlight = 0
        self.humidity = 0

#read in through state.conversionObservation and then get the dictionary from the datamodel class
#get positions in the orderbook
#conversions happens from the conversation observation

#buy low on the book
#sell high on the conversion

#state.orderdepths[product]

#300 k is a descent amount
    def run(self, state: TradingState) -> Tuple[Dict[str, List[Order]], int, str]:
        # Initialization of local variables
        orchid_data = state.observations.conversionObservations['ORCHIDS']
        order_depth: OrderDepth = state.order_depths['ORCHIDS']
        orders: List[Order] = []

        # Update internal state with current market and environmental data
        self.transportFees = orchid_data.transportFees
        self.exportTariff = orchid_data.exportTariff
        self.importTariff = orchid_data.importTariff
        self.sunlight = orchid_data.sunlight
        self.humidity = orchid_data.humidity

        # Calculate fair bid and ask prices based on observed conversion rates and fees/tariffs
        fair_bid = orchid_data.bidPrice - self.transportFees + self.exportTariff
        fair_ask = orchid_data.askPrice + self.transportFees - self.importTariff

        # Determine appropriate buy orders based on the market depth and fair prices
        for price, quantity in order_depth.sell_orders.items():
            if price < fair_bid:
                orders.append(Order("ORCHIDS", price, -quantity))
                print(f"BUY {quantity}x at {price}")

        # Determine appropriate sell orders based on the market depth and fair prices
        for price, quantity in order_depth.buy_orders.items():
            if price > fair_ask:
                orders.append(Order("ORCHIDS", price, quantity))
                print(f"SELL {quantity}x at {price}")

        result = {"ORCHIDS": orders}
        conversions = len(orders)  # example of tracking conversions

        traderData = "SAMPLE"  # Placeholder for trader state data

        return result, conversions, traderData