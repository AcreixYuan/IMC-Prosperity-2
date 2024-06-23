from datamodel import Order, OrderDepth, Product, TradingState, UserId
from typing import List
import jsonpickle
import math

class Trader:
        
    def __init__(self):
        self.POSITION_LIMIT = {'AMETHYSTS': 20, 'STARFRUIT': 20, "ORCHIDS": 100, 'CHOCOLATE': 250, 'STRAWBERRIES': 350,
                               'ROSES':1, 'GIFT_BASKET':60 }
        self.long = False
    
    def get_position(self, state: TradingState, product: Product):
        return 0 if product not in state.position else state.position[product]
    

    def compute_orders_ameth(self, state: TradingState) -> List[Order]:
        """
        Market making strategy
        :param state: TradingState
        :param product: Product
        :return orders: list[Order]
        """
        p = self.get_position(state, 'AMETHYSTS')
        bid_volume = - max(p, 0) + self.POSITION_LIMIT['AMETHYSTS']
        ask_volume = max(-p, 0) - self.POSITION_LIMIT['AMETHYSTS']

        order_depth: OrderDepth = state.order_depths['AMETHYSTS']
        sell_dict = order_depth.sell_orders
        buy_dict = order_depth.buy_orders
        orders: list[Order] = []

        if len(sell_dict) > 0:
            best_ask = min(sell_dict.keys())
            best_ask_volume = sell_dict[best_ask]
        else:
            best_ask = 10002
            best_ask_volume = 0

        if len(buy_dict) > 0:
            best_bid = max(buy_dict.keys())
            best_bid_volume = buy_dict[best_bid]
        else:
            best_bid = 9998
            best_bid_volume = 0
            

        while (best_ask < 10000 or (best_ask==10000 and p < 0)) and bid_volume != 0:
            bid_vol_cross = min(bid_volume, - best_ask_volume)
            orders.append(Order('AMETHYSTS', best_ask, bid_vol_cross))
            bid_volume -= bid_vol_cross
            p += bid_vol_cross

            del sell_dict[best_ask]
            if len(sell_dict) == 0:
                best_ask = 10001
            else:
                best_ask = min(sell_dict.keys())
                best_ask_volume = sell_dict[best_ask]

        while (best_bid > 10000 or (best_bid==10000 and p > 0)) and ask_volume != 0:
            ask_vol_cross = max(ask_volume, - best_bid_volume)
            orders.append(Order('AMETHYSTS', best_bid, ask_vol_cross))
            ask_volume -= ask_vol_cross
            p += ask_vol_cross

            del buy_dict[best_bid]
            if len(buy_dict) == 0:
                best_bid = 9999
            else:
                best_bid = max(buy_dict.keys())
                best_bid_volume = buy_dict[best_bid]

        if bid_volume != 0:
            if p < 0:
                orders.append(Order('AMETHYSTS', min(best_bid + 1, 10000), bid_volume))
            elif p > 15:
                orders.append(Order('AMETHYSTS', min(best_bid - 1, 10000), bid_volume))
            else:
                orders.append(Order('AMETHYSTS', min(best_bid, 10000), bid_volume))
        
        p += bid_volume

        if ask_volume != 0:
            if p > 0:
                orders.append(Order('AMETHYSTS', max(best_ask - 1, 10000), ask_volume))
            elif p < -15:
                orders.append(Order('AMETHYSTS', max(best_ask + 1, 10000), ask_volume))
            else:
                orders.append(Order('AMETHYSTS', max(best_ask, 10000), ask_volume))

        return orders
    
    def compute_orders_star(self, state: TradingState, trader_data):
        """
        Market making strategy
        :param state: TradingState
        :return trader_data: dict
        """
        p = self.get_position(state, 'STARFRUIT')
        bid_volume = - max(p, 0) + self.POSITION_LIMIT['STARFRUIT']
        ask_volume = max(-p, 0) - self.POSITION_LIMIT['STARFRUIT']

        order_depth: OrderDepth = state.order_depths['STARFRUIT']
        sell_dict = order_depth.sell_orders
        buy_dict = order_depth.buy_orders
        orders: list[Order] = []

        # maintain a rolling window
        if len(trader_data['STARFRUIT']) == 4:
            trader_data['STARFRUIT'].pop(0)
            
        # record the mid of the worst bid and ask prices    
        worst_sell_pr = max(sell_dict) if len(sell_dict) > 0 else min(buy_dict)
        worst_buy_pr = min(buy_dict) if len(buy_dict) > 0 else max(sell_dict)
        trader_data['STARFRUIT'].append((worst_buy_pr+worst_sell_pr)/2)
        
        if len(trader_data['STARFRUIT']) < 4:
            return orders, trader_data
        
        theory_price = sum(trader_data['STARFRUIT']) / 4

        if len(sell_dict) > 0:
            best_ask = min(sell_dict.keys())
            best_ask_volume = sell_dict[best_ask]
        else:
            best_ask = int(theory_price) + 2
            best_ask_volume = 0

        if len(buy_dict) > 0:
            best_bid = max(buy_dict.keys())
            best_bid_volume = buy_dict[best_bid]
        else:
            best_bid = int(theory_price) - 2
            best_bid_volume = 0
                
        while (best_ask < theory_price) and bid_volume != 0:
            bid_vol_cross = min(bid_volume, - best_ask_volume)
            orders.append(Order('STARFRUIT', best_ask, bid_vol_cross))
            bid_volume -= bid_vol_cross
            p += bid_vol_cross

            del sell_dict[best_ask]
            if len(sell_dict) == 0:
                best_ask = int(round(theory_price))+1
            else:
                best_ask = min(sell_dict.keys())
                best_ask_volume = sell_dict[best_ask]

        while (best_bid > theory_price) and ask_volume != 0:
            ask_vol_cross = max(ask_volume, - best_bid_volume)
            orders.append(Order('STARFRUIT', best_bid, ask_vol_cross))
            ask_volume -= ask_vol_cross
            p += ask_vol_cross

            del buy_dict[best_bid]
            if len(buy_dict) == 0:
                best_bid = int(round(theory_price))-1
            else:
                best_bid = max(buy_dict.keys())
                best_bid_volume = buy_dict[best_bid]

        if bid_volume != 0:
            orders.append(Order('STARFRUIT', min(best_bid+1, int(round(theory_price))), bid_volume))

        if ask_volume != 0:
            orders.append(Order('STARFRUIT', max(best_ask-1, int(round(theory_price))), ask_volume))

        return orders, trader_data    
            
    def self_compute_orders_orch(self, state: TradingState):        
        orders: list[Order] = []
                
        # get information related to the conversion
        ask_cvt = state.observations.conversionObservations['ORCHIDS'].askPrice
        # bid_cvt = state.observations.conversionObservations['ORCHIDS'].bidPrice
        fee = state.observations.conversionObservations['ORCHIDS'].transportFees
        # export_tariff = state.observations.conversionObservations['ORCHIDS'].exportTariff
        import_tariff = state.observations.conversionObservations['ORCHIDS'].importTariff
        # sunlight = state.observations.conversionObservations['ORCHIDS'].sunlight
        # humidity = state.observations.conversionObservations['ORCHIDS'].humidity
        
        max_conversion = -self.get_position(state, 'ORCHIDS')
        
        # define the sunlight and humidity impact as a penalty to theoretical price
        # sunlight = max(0, math.ceil((7*60-sunlight/6.944)/10) * 0.04)    
        # if humidity > 80:
        #     humidity = max(0, math.ceil((humidity-80)/5)*0.02)
        # elif humidity < 60:
        #     humidity = max(0, math.ceil((60-humidity)/5)*0.02)
        # else:
        #     humidity = 0
            
        # since export tariff is extremely high, this "arbitrage" strategy is only feasible for import side, 
        # i.e. limit sell order on the market and buy back through conversion at the "dark pool"
        ask_tilt = ask_cvt + import_tariff + fee
        # ask_tilt = ask_cvt + import_tariff + fee + sunlight + humidity
                
        # place a limit order with maximum amount every timestamp
        orders.append(Order('ORCHIDS', int(round((ask_tilt)))+2, -self.POSITION_LIMIT['ORCHIDS']))
        # orders.append(Order('ORCHIDS', math.ceil(ask_tilt)+1, -self.POSITION_LIMIT['ORCHIDS']))
            
        return orders, max_conversion
    
    def get_info_product(self, state, product):

        order_depth: OrderDepth = state.order_depths[product]
        sell_dict = order_depth.sell_orders
        buy_dict = order_depth.buy_orders

        best_ask = min(sell_dict.keys())
        best_ask_volume = sell_dict[best_ask]
        
        best_bid = max(buy_dict.keys())
        best_bid_volume = buy_dict[best_bid]
        
        return best_ask, best_bid, best_ask_volume, best_bid_volume

            
    def run(self, state: TradingState):
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        
        # print("traderData: " + state.traderData)
        # print("Observations: " + str(state.observations))
        
        conversion = 0
        
        if not state.traderData:
            trader_data = {}
            for product in self.POSITION_LIMIT.keys():
                if product == 'STARFRUIT':
                    trader_data[product] = []
                if product == 'GIFT_BASKET':
                    trader_data[product] = []
                    trader_data["SPREAD"] = []
        else:
            trader_data = jsonpickle.decode(state.traderData)
        
        result = {}

        for product in state.order_depths.keys():
            # print(f'{product} position: {self.get_position(state, product)}')
            
            if product == 'AMETHYSTS':
                try:
                    result[product] = self.compute_orders_ameth(state)
                except Exception as e:
                    print(f'AMETHYSTS error: {e}')
                
            if product == 'STARFRUIT':
                try:
                    result[product], trader_data = self.compute_orders_star(state, trader_data)
                except Exception as e:
                    print(f'STARFRUIT error: {e}')
                
            if product == 'ORCHIDS':
                try:
                    result[product], conversion = self.self_compute_orders_orch(state)
                except Exception as e:
                    print(f'ORCHIDS error: {e}')
            
            
            if product == 'GIFT_BASKET':
                #this can not be done in a nice wrapper function, as several other results components for other elements need to be loaded in.
                print('GIFT_BASKET')
                best_ask_roses, best_bid_roses, best_ask_volume_roses, best_bid_volume_roses = self.get_info_product(state, 'ROSES')

                # Fetching trading data for strawberries
                best_ask_strawberries, best_bid_strawberries, best_ask_volume_strawberries, best_bid_volume_strawberries = self.get_info_product(state, 'STRAWBERRIES')

                # Fetching trading data for chocolate
                best_ask_chocolate, best_bid_chocolate, best_ask_volume_chocolate, best_bid_volume_chocolate = self.get_info_product(state, 'CHOCOLATE')

                # Fetching trading data for gift baskets
                best_ask_gift_basket, best_bid_gift_basket, best_ask_volume_gift_basket, best_bid_volume_gift_basket = self.get_info_product(state, 'GIFT_BASKET')

                trader_data["SPREAD"] = best_ask_gift_basket - best_bid_roses - 4* best_bid_chocolate - 6* best_ask_strawberries
                
                #if spread is more than 450 we sell
                #if spred is less than 350 we buy
                if trader_data["SPREAD"] < 350 and self.long==False:
                    #but the ETF and go short the underlyings
                    result["GIFT_BASKET"] = [Order("GIFT_BASKET", trader_data["SPREAD"] + 1,1 )]
                    result["ROSES"] = [Order("ROSES", best_bid_roses - 1, - 1 )]
                    result["CHOCOLATE"] = [Order("CHOCOLATE", best_bid_chocolate - 1, - 4 )]
                    result["STRAWBERRIES"] = [Order("STRAWBERRIES", best_bid_strawberries - 1, - 6 )]
                    self.long=True
                    
                if trader_data["SPREAD"] > 450 and self.long==True:
                    #sell the ETF and purchase the underlyings
                    result["GIFT_BASKET"] = [Order("GIFT_BASKET", trader_data["SPREAD"] - 1, - 1 )]
                    result["ROSES"] = [Order("ROSES", best_ask_roses + 1,1 )]
                    result["CHOCOLATE"] = [Order("CHOCOLATE", best_ask_chocolate + 1,4 )]
                    result["STRAWBERRIES"] = [Order("STRAWBERRIES", best_ask_strawberries + 1,6 )]
                    self.long=False
                    
                
                    
                
                
        traderData = jsonpickle.encode(trader_data)

        return result, conversion, traderData
