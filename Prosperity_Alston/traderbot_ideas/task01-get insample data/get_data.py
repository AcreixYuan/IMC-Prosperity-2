from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


class Trader:
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}
        for sym in state.market_trades.keys():
            for i in range(len(state.market_trades[sym])):
                timestamp = state.timestamp
                symbol = sym
                price = state.market_trades[sym][i].price
                size = state.market_trades[sym][i].quantity
                buyer = state.market_trades[sym][i].buyer
                seller = state.market_trades[sym][i].seller
                bid = state.order_depths[sym].buy_orders
                ask = state.order_depths[sym].sell_orders
                print(timestamp, symbol, price, size, buyer, seller, bid, ask)
        return result
            