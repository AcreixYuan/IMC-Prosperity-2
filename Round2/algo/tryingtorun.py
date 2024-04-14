from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

class Trader:
    def __init__(self):
        self.position_limit = {"ORCHIDS": 100}
        self.last_mid_price = {'ORCHIDS': 1100}
        self.mid_price = {'ORCHIDS': {0: 1100}}
        self.buy_orders = {}
        self.sell_orders = {}
        self.bidPrice = 0
        self.askPrice = 0
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
    
    def run(self, state: TradingState):
        # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
        #print("traderData: " + state.traderData)
        #print("Observations: " + str(state.observations))
        result = {}
        
        #update the current state
        self.buy_orders = state.order_depths["ORCHIDS"].buy_orders
        self.sell_orders = state.order_depths["ORCHIDS"].sell_orders
        self.bidPrice = state.observations.conversionObservations.bidPrice
        self.askPrice = state.observations.conversionObservations.askPrice
        self.transportFees = state.observations.conversionObservations.transportFees
        self.exportTariff = state.observations.conversionObservations.exportTariff
        self.importTariff = state.observations.conversionObservations.importTariff
        self.sunlight = state.observations.conversionObservations.sunlight
        self.humidity = state.observations.conversionObservations.humidity

        #we need to look into an arbitrage opportunity fo
 
 
        self.fair_bid = self.bidPrice - self.transportFees + self.exportTariff  
        self.fair_ask = self.askPrice + self.transportFees - self.importTariff
        
        order_depth: OrderDepth = state.order_depths["ORCHIDS"]
        orders: List[Order] = []
        product = "ORCHIDS"
        if len(order_depth.sell_orders) != 0:
            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            if int(best_ask) < self.fair_bid:
                print("BUY", str(-best_ask_amount) + "x", best_ask)
                orders.append(Order("ORCHIDS", best_ask, -best_ask_amount))
        conversions = best_ask_amount
        
        """

        Returns:
            _type_: _description_
        
        if len(order_depth.buy_orders) != 0:
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            if int(best_bid) > self.fair_ask:
                print("SELL", str(best_bid_amount) + "x", best_bid)
                orders.append(Order(product, best_bid, -best_bid_amount))
        """
        result[product] = orders
        

    
    
        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        
        #by setting conversions equal to whatever amount you want to convert
        return result, conversions, traderData
