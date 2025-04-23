# from core.data_handler import DataHandler
#
# data_handler = DataHandler(symbols=["AAPL", "MSFT", "EURUSD=X", "BTC-USD", "ETH-USD"])
#
# while data_handler.has_next():
#     next_row = data_handler.get_next()

# from core.portfolio import Portfolio
#
# group_config = {
#     "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD"],
#     "Forex": ["EURUSD=X", "GBPUSD=X", "JPY=X"],
#     "Equities": ["AAPL", "MSFT"],
#     "Derivatives": {
#             "Index Futures": ["ES=F"],
#             "Commodities Futures": ["GC=F"]
#         }
# }
#
# portfolio = Portfolio(balance=10000, group_config=group_config)
# flat_weigths = portfolio.get_flat_allocations()
#
# print(flat_weigths)

from core.executor import TradeExecutor

executor = TradeExecutor()

executor.execute("BTC-USD", 30000, 1.0)  # Long
executor.mark_market_price("BTC-USD", 32000)
executor.execute("BTC-USD", 32000, -1.0)  # Long

executor.execute("ETH-USD", 2000, -1.0)  # Short
executor.mark_market_price("ETH-USD", 1800)

executor.summary()

executor.close("BTC-USD", 33000)
executor.close("ETH-USD", 1900)

executor.summary()
