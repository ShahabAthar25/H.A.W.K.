from core.engine import Engine

group_config = {
    "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD"],
    "Forex": ["EURUSD=X", "GBPUSD=X"],
    "Stocks": ["AAPL", "MSFT", "META", "GOOG"],
    "Index": ["^SPX", "^IXIC"]
}

symbols = ["BTC-USD", "ETH-USD", "SOL-USD", "EURUSD=X", "GBPUSD=X", "AAPL", "MSFT", "META", "GOOG", "^SPX", "^IXIC"]
initial_balance = 10_000

engine = Engine(symbols, group_config, initial_balance)
engine.run()
