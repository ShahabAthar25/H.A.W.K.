from core.data_handler import DataHandler

data_handler = DataHandler(symbols=["AAPL", "MSFT", "EURUSD=X", "BTC-USD", "ETH-USD"])

while data_handler.has_next():
    next_row = data_handler.get_next()
