from datamodel import Order, OrderDepth, Product, TradingState, UserId, Listing, Observation, ProsperityEncoder, Symbol, Trade, Position
from typing import List, Any
import jsonpickle
import math
import json

class Logger:
    def __init__(self) -> None:
        self.logs = ""
        self.max_log_length = 3750

        self.prices = {
            "Spread":pd.Series(),
            "SPREAD_PICNIC": pd.Series(),
        }

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

class Trader:
        
    def __init__(self):
        self.POSITION_LIMIT = {'AMETHYSTS': 20, 'STARFRUIT': 20, "ORCHIDS": 100, "CHOCOLATE": 250,
         "STRAWBERRIES": 350, "ROSE":60, "GIFT_BASKET": 60}

        self.prices = {
            "Spread":pd.Series(),
            "SPREAD_PICNIC": pd.Series(),
        }

    
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
        orders.append(Order('ORCHIDS', int(round((ask_tilt)))+1, -self.POSITION_LIMIT['ORCHIDS']))
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
    
    def get_mid_price(self, state, product):
        best_ask, best_bid, best_ask_volume, best_bid_volume = self.get_info_product(state, product)
        return (best_ask + best_bid) / 2
    
    """
    def self_compute_orders_basket(self, state: TradingState):
        '''
            Pair Trading Strategy
            :param state: TradingState
            :return orders: list[Order]
        '''
        orders_basket: list[Order] = []
        orders_chocolate: list[Order] = []
        orders_roses: list[Order] = []
        orders_strawberries: list[Order] = []

        logger.print('GIFT_BASKET')
        price_basket = self.get_mid_price(state, 'GIFT_BASKET')
        price_chocolate = self.get_mid_price(state, 'CHOCOLATE')
        price_roses = self.get_mid_price(state, 'ROSES')
        price_strawberries = self.get_mid_price(state, 'STRAWBERRIES')

        # get current position of the basket
        position_basket = self.get_position(state, 'GIFT_BASKET')
        position_chocolate = self.get_position(state, 'CHOCOLATE')
        position_roses = self.get_position(state, 'ROSES')
        position_strawberries = self.get_position(state, 'STRAWBERRIES')

        spread = price_basket - 4*price_chocolate - 6*price_strawberries- price_roses - 380

        # if the spread is positive by 30, full short position of gift basket, full long position of roses, chocolate, strawberries
        if spread > 30:
            orders_basket.append(Order('GIFT_BASKET', best_ask_gift_basket+1, -self.POSITION_LIMIT['GIFT_BASKET'] + position_basket))
            orders_roses.append(Order('ROSES', best_bid_roses-1, self.POSITION_LIMIT['ROSES'] - position_roses))
            orders_chocolate.append(Order('CHOCOLATE', best_bid_chocolate-1, self.POSITION_LIMIT['CHOCOLATE'] - position_chocolate))
            orders_strawberries.append(Order('STRAWBERRIES', best_ask_strawberries-1, self.POSITION_LIMIT['STRAWBERRIES'] - position_strawberries))

        
        # if the spread is negative by 30, full long position of gift basket, full short position of roses, chocolate, strawberries
        elif spread < 30:
            orders_basket.append(Order('GIFT_BASKET', best_bid_gift_basket-1, self.POSITION_LIMIT['GIFT_BASKET'] + position_basket))
            orders_roses.append(Order('ROSES', best_ask_roses+1, -self.POSITION_LIMIT['ROSES'] - position_roses))
            orders_chocolate.append(Order('CHOCOLATE', best_ask_chocolate+1, -self.POSITION_LIMIT['CHOCOLATE'] - position_chocolate))
            orders_strawberries.append(Order('STRAWBERRIES', best_bid_strawberries+1, -self.POSITION_LIMIT['STRAWBERRIES'] - position_strawberries))

        return orders_basket, orders_chocolate, orders_roses, orders_strawberries
    """

    def save_prices_product(
        self, 
        product, 
        state: TradingState,
        price: Union[float, int, None] = None, 
    ):
        if not price:
            price = self.get_mid_price(product, state)

        self.prices[product] = pd.concat([
            self.prices[product],
            pd.Series({state.timestamp: price})
        ])

    def basket_strategy(self, state: TradingState)-> List[Order]:
        """Picnic strategy. Trades on spread between basket and
        1*rose + 6*strawberries + 4*chocolate

        Args:
            state (TradingState): state

        Returns:
            List[Order]: chocolate, strawberries, roses and basket orders
        """        

        orders_chocolate = []
        orders_strawberries = []
        orders_roses = []
        orders_basket = []
        
        def create_orders(buy_basket: bool)-> List[List[Order]]:

            if buy_basket:
                sign = 1
                price_basket = 1e7
                price_others = 1
            else:
                sign = -1
                price_basket = 1
                price_others = 1e7
            
            orders_basket.append(
                Order('GIFT_BASKET', price_basket, sign*VOLUME_BASKET)
            )
            orders_roses.append(
                Order('ROSES', price_others, -sign*VOLUME_BASKET)
            )
            orders_chocolate.append(
                Order('CHOCOLATE', price_others, -sign*4*VOLUME_BASKET)
            )
            orders_strawberries.append(
                Order('STRAWBERRIES', price_others, -sign*2*VOLUME_BASKET)
            )
 
        

        price_basket = self.get_mid_price('BASKET', state)
        price_roses = self.get_mid_price('ROSES', state)
        price_strawberries = self.get_mid_price('STRAWBERRIES', state)
        price_chocolate = self.get_mid_price('CHOCOLATE', state)

        position_basket = self.get_position('GIFT_BASKET', state)
        # position_dip = self.get_position(DIP, state)
        # position_ukulele = self.get_position(UKULELE, state)
        # position_baguette = self.get_position(BAGUETTE, state)

        spread = price_basket - (1*price_rose + 6*price_strawberries + 4*price_chocolate)
        self.save_prices_product(
            "SPREAD_BASKET",
            state,
            spread
        )

        avg_spread = self.prices["SPREAD_BASKET"].rolling(20).mean()
        std_spread = self.prices["SPREAD_BASKET"].rolling(20).std()
        spread_5 = self.prices["SPREAD_BASKET"].rolling(5).mean()

        if not np.isnan(avg_spread.iloc[-1]):
            avg_spread = avg_spread.iloc[-1]
            std_spread = std_spread.iloc[-1]
            spread_5 = spread_5.iloc[-1]
            print(f"Average spread: {avg_spread}, Spread5: {spread_5}, Std: {std_spread}")


            if abs(position_basket) <= self.POSITION_LIMIT['GIFT_BASKET']-2:
                if spread_5 < avg_spread - 2*std_spread:  # buy basket
                    buy_basket = True
                    create_orders(buy_basket)

                elif spread_5 > avg_spread + 2*std_spread: # sell basket
                    buy_basket = False 
                    create_orders(buy_basket)

            else: # abs(position_basket) >= POSITION_LIMITS[PICNIC_BASKET]-10
                if position_basket >0 : # sell basket
                    if spread_5 > avg_spread + 2*std_spread:
                        buy_basket = False
                        create_orders(buy_basket)

                else: # buy basket
                    if spread_5 < avg_spread - 2*std_spread:
                        buy_basket = True
                        create_orders(buy_basket)

        return orders_basket, orders_chocolate, orders_roses, orders_strawberries


            
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
        else:
            trader_data = jsonpickle.decode(state.traderData)
        
        result = {}

        for product in state.order_depths.keys():
            # print(f'{product} position: {self.get_position(state, product)}')
            
            if product == 'AMETHYSTS':
                try:
                    result[product] = self.compute_orders_ameth(state)
                except Exception as e:
                    logger.print(f'AMETHYSTS error: {e}')
                
            if product == 'STARFRUIT':
                try:
                    result[product], trader_data = self.compute_orders_star(state, trader_data)
                except Exception as e:
                    logger.print(f'STARFRUIT error: {e}')
                
            if product == 'ORCHIDS':
                try:
                    result[product], conversion = self.self_compute_orders_orch(state)
                except Exception as e:
                    logger.print(f'ORCHIDS error: {e}')
            
            if product == 'GIFT_BASKET':
                try:
                    result['GIFT_BASKET'], result['CHOCOLATE'], result['ROSES'], result['STRAWBERRIES'] = self.basket_strategy(state)
                except Exception as e:
                    logger.print(f'GIFT_BASKET error: {e}')
                
                
        traderData = jsonpickle.encode(trader_data)
        logger.flush(state, result, conversion, traderData)
        return result, conversion, traderData

logger = Logger()