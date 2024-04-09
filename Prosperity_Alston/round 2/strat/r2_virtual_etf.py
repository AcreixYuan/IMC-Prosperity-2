from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


class Trader:
    # define data members
    def __init__(self):
        self.position_limit = {"PEARLS": 20, "BANANAS": 20,"COCONUTS":600,"PINA_COLADAS": 300}
        self.last_mid_price = {'PEARLS': 10000, 'BANANAS': 5000,'COCONUT':8000, 'PINA_COLADAS': 15000}
    # ETF = 2COCONUT-1PINACOLADA = 1000

    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        # Initialize the method output dict as an empty dict
        result = {}
        # Iterate over all the keys (the available products) contained in the order dephts
        for product in state.order_depths.keys():
            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':

                # initilize temp variables
                best_ask, best_ask_volume, best_bid, best_bid_volume = 0, 0, 0, 0

                # retrieve current position from state.positions
                current_position = 0 if product not in state.position else state.position[product]

                legal_buy_vol = min(
                    self.position_limit[product] - current_position, self.position_limit[product])
                legal_sell_vol = max(
                    -(self.position_limit[product] + current_position), -self.position_limit[product])

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Calculate the fair price: weighted average price of the orderbook
                if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    # calculate the weighted average price for each side
                    avg_buy_price = sum([order_depth.buy_orders[i] * i for i in order_depth.buy_orders.keys()])/sum(
                        [order_depth.buy_orders[i] for i in order_depth.buy_orders.keys()])
                    avg_sell_price = sum([-order_depth.sell_orders[i] * i for i in order_depth.sell_orders.keys()])/sum(
                        [-order_depth.sell_orders[i] for i in order_depth.sell_orders.keys()])
                    mid_price = (avg_sell_price + avg_buy_price)/2
                elif len(order_depth.sell_orders) == 0 and len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    mid_price = self.last_mid_price[product]
                elif len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) == 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    mid_price = self.last_mid_price[product]
                else:
                    mid_price = self.last_mid_price[product]

                # update last mid price
                self.last_mid_price[product] = mid_price

                # market status
                market_status = 0 if (best_ask_volume < 15 and best_bid_volume < 15) else 1 if (
                    best_ask_volume <= 15 and best_bid_volume > 15) else -1 if (best_ask_volume > 15 and best_bid_volume <= 15) else 0

                # Define a fair value for the PEARLS.
                acceptable_price = mid_price+2*market_status

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                if best_ask_volume >0 and best_bid_volume >0: # 有买单有卖单
                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    # taker strategy
                    if best_ask <= acceptable_price:  # 卖得低，take the sell order on the orderbook as much as possible
                        orders.append(Order(product, best_ask, int(
                            min(-best_ask_volume, legal_buy_vol))))

                        legal_buy_vol = legal_buy_vol - \
                            int(min(-best_ask_volume, legal_buy_vol))
                    if best_bid >= acceptable_price:  # 买得贵，take the buy order on the orderbook as much as possible
                        orders.append(Order(product, best_bid, int(
                            max(-best_bid_volume, legal_sell_vol))))

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

                elif best_ask_volume ==0:  # 只有买单
                    if best_bid >= acceptable_price:
                        orders.append(Order(product, best_bid, int(
                            max(-best_bid_volume, legal_sell_vol))))

                elif best_bid_volume==0:  # 只有卖单
                    if best_ask <= acceptable_price:
                        orders.append(Order(product, best_ask, int(
                            min(-best_ask_volume, legal_buy_vol))))
                # Add all the above the orders to the result dict
                result[product] = orders

            if product == 'BANANAS':

                # initilize temp variables
                best_ask, best_ask_volume, best_bid, best_bid_volume = 0, 0, 0, 0

                # retrieve current position from state.positions
                current_position = 0 if product not in state.position else state.position[product]

                legal_buy_vol = min(
                    self.position_limit[product] - current_position, self.position_limit[product])
                legal_sell_vol = max(
                    -(self.position_limit[product] + current_position), -self.position_limit[product])

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Calculate the fair price: weighted average price of the orderbook
                if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    # calculate the weighted average price for each side
                    avg_buy_price = sum([order_depth.buy_orders[i] * i for i in order_depth.buy_orders.keys()])/sum(
                        [order_depth.buy_orders[i] for i in order_depth.buy_orders.keys()])
                    avg_sell_price = sum([-order_depth.sell_orders[i] * i for i in order_depth.sell_orders.keys()])/sum(
                        [-order_depth.sell_orders[i] for i in order_depth.sell_orders.keys()])
                    mid_price = (avg_sell_price + avg_buy_price)/2
                elif len(order_depth.sell_orders) == 0 and len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    mid_price = self.last_mid_price[product]
                elif len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) == 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    mid_price = self.last_mid_price[product]
                else:
                    mid_price = self.last_mid_price[product]

                # update last mid price
                self.last_mid_price[product] = mid_price

                # market status
                market_status = 0 if (best_ask_volume < 15 and best_bid_volume < 15) else 1 if (
                    best_ask_volume <= 15 and best_bid_volume > 15) else -1 if (best_ask_volume > 15 and best_bid_volume <= 15) else 0

                # Define a fair value for the PEARLS.
                acceptable_price = mid_price+2*market_status

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                if best_ask_volume >0 and best_bid_volume >0: # 有买单有卖单
                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    # taker strategy
                    if best_ask <= acceptable_price:  # 卖得低，take the sell order on the orderbook as much as possible
                        orders.append(Order(product, best_ask, int(
                            min(-best_ask_volume, legal_buy_vol))))

                        legal_buy_vol = legal_buy_vol - \
                            int(min(-best_ask_volume, legal_buy_vol))
                    if best_bid >= acceptable_price:  # 买得贵，take the buy order on the orderbook as much as possible
                        orders.append(Order(product, best_bid, int(
                            max(-best_bid_volume, legal_sell_vol))))

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

                elif best_ask_volume ==0:  # 只有买单
                    if best_bid >= acceptable_price:
                        orders.append(Order(product, best_bid, int(
                            max(-best_bid_volume, legal_sell_vol))))

                elif best_bid_volume==0:  # 只有卖单
                    if best_ask <= acceptable_price:
                        orders.append(Order(product, best_ask, int(
                            min(-best_ask_volume, legal_buy_vol))))
                # Add all the above the orders to the result dict
                result[product] = orders
        # build ETF based on coconut and pina colada orderbook

        # # initilize temp variables
        # etf_best_ask, etf_best_ask_volume, etf_best_bid, etf_best_bid_volume = 0, 0, 0, 0
        # # quote volume limit
        # coconut_current_position = 0 if 'COCONUTS' not in state.position else state.position[
        #     'COCONUTS']
        # pina_colada_current_position = 0 if 'PINA_COLADAS' not in state.position else state.position[
        #     'PINA_COLADAS']
        # # the current position of ETF is the round of the half of the coconut current position
        # etf_current_position = round(coconut_current_position/2)
        
        # # Retrieve the Order Depth containing all the market BUY and SELL orders for COCONUTS and PINA_COLADAS
        # coconut_order_depth: OrderDepth = state.order_depths['COCONUTS']
        # pina_colada_order_depth: OrderDepth = state.order_depths['PINA_COLADAS']

        # if len(coconut_order_depth.sell_orders) != 0 and len(coconut_order_depth.buy_orders) != 0:
        #     coconut_best_ask = min(coconut_order_depth.sell_orders.keys())
        #     coconut_best_ask_volume = coconut_order_depth.sell_orders[coconut_best_ask]
        #     coconut_best_bid = max(coconut_order_depth.buy_orders.keys())
        #     coconut_best_bid_volume = coconut_order_depth.buy_orders[coconut_best_bid]
        #     coconut_avg_buy_price = sum([coconut_order_depth.buy_orders[i] * i for i in coconut_order_depth.buy_orders.keys()])/sum(
        #         [coconut_order_depth.buy_orders[i] for i in coconut_order_depth.buy_orders.keys()])
        #     coconut_avg_sell_price = sum([-coconut_order_depth.sell_orders[i] * i for i in coconut_order_depth.sell_orders.keys()])/sum(
        #         [-coconut_order_depth.sell_orders[i] for i in coconut_order_depth.sell_orders.keys()])
        #     coconut_mid_price = (coconut_avg_sell_price + coconut_avg_buy_price)/2
        # else:
        #     coconut_mid_price = self.last_mid_price['COCONUTS']
        # self.last_mid_price['COCONUTS'] = coconut_mid_price

        # if len(pina_colada_order_depth.sell_orders) != 0 and len(pina_colada_order_depth.buy_orders) != 0:
        #     pina_colada_best_ask = min(pina_colada_order_depth.sell_orders.keys())
        #     pina_colada_best_ask_volume = pina_colada_order_depth.sell_orders[pina_colada_best_ask]
        #     pina_colada_best_bid = max(pina_colada_order_depth.buy_orders.keys())
        #     pina_colada_best_bid_volume = pina_colada_order_depth.buy_orders[pina_colada_best_bid]
        #     pina_colada_avg_buy_price = sum([pina_colada_order_depth.buy_orders[i] * i for i in pina_colada_order_depth.buy_orders.keys()])/sum(
        #         [pina_colada_order_depth.buy_orders[i] for i in pina_colada_order_depth.buy_orders.keys()])
        #     pina_colada_avg_sell_price = sum([-pina_colada_order_depth.sell_orders[i] * i for i in pina_colada_order_depth.sell_orders.keys()])/sum(
        #         [-pina_colada_order_depth.sell_orders[i] for i in pina_colada_order_depth.sell_orders.keys()])
        #     pina_colada_mid_price = (pina_colada_avg_sell_price + pina_colada_avg_buy_price)/2
        # else:
        #     pina_colada_mid_price = self.last_mid_price['PINA_COLADAS']

        # # build the orderbook of ETF based on these 2 products
        # # ETF = 2*COCONUTS - PINA_COLADAS





        # Return the result
        return result
