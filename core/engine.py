from core.data_handler import DataHandler
from core.portfolio import Portfolio
from core.executor import TradeExecutor

class Engine:
    def __init__(self, group_config, initial_balance):
        self.portfolio = Portfolio(balance=initial_balance, group_config=group_config)
        self.data_handler = DataHandler([symbol for symbol in self.portfolio.get_flat_allocations().keys()])
        self.executor = TradeExecutor()
        self.starting_balance = initial_balance

    def run(self):
        allocation = self.portfolio.get_flat_allocations()
        first = True

        while self.data_handler.has_next():
            data = self.data_handler.get_next()

            for symbol, row in data.items():
                if row is None:
                    continue

                if first:
                    price = data[symbol]["Close"]
                    qty = allocation[symbol] / price
                    self.executor.execute(symbol, price, qty, timestamp=row.name)

                else:
                    self.executor.mark_market_price(symbol, data[symbol]["Close"])

            first = False

        self.executor.summary()
        print(f"Final Portfolio Value: {self.current_value():.2f}, Starting Balance: {self.starting_balance:.2f}")

    def current_value(self):
        total = 0.0
        for symbol, pos in self.executor.positions.items():
            total += pos.value() + pos.realized_pnl + pos.unrealized_pnl()
        return total
