from datamodel import OrderDepth, UserId, TradingState, Order, Observation, ConversionObservation
from typing import List
import string

class Trader:
    
    def run(self, state: TradingState):
        conversions = 1
        # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        observations = state.observations
        result = {}
        product = "ORCHIDS"
        #for product in state.order_depths:
        order_depth: OrderDepth = state.order_depths[product]
        bidPrice = observations.conversionObservations[product].bidPrice
        """ 
        bidPrice = state.observations.conversionObservations[product].bidPrice
        askPrice = state.observations.conversionObservations[product].askPrice
        transportFees = state.observations.conversionObservations[product].transportFees
        exportTariff = state.observations.conversionObservations[product].exportTariff
        importTariff = state.observations.conversionObservations[product].importTariff
        sunlight = state.observations.conversionObservations[product].sunlight
        humidity = state.observations.conversionObservations[product].humidity
        """
        orders: List[Order] = []
        acceptable_price = 10;  # Participant should calculate this value
        print("Acceptable price : " + str(acceptable_price))
        print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

        if len(order_depth.sell_orders) != 0:
            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            if int(best_ask) < acceptable_price:
                print("BUY", str(-best_ask_amount) + "x", best_ask)
                orders.append(Order(product, best_ask, -best_ask_amount))

        if len(order_depth.buy_orders) != 0:
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            if int(best_bid) > acceptable_price:
                print("SELL", str(best_bid_amount) + "x", best_bid)
                orders.append(Order(product, best_bid, -best_bid_amount))
        
        result[product] = orders
    
    
        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        

        return result, conversions, traderData