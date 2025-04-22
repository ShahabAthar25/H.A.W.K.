from core.data_handler import DataHandler

data_handler = DataHandler(symbols=["AAPL", "EURUSD=X", "BTC-USD", "ETH-USD"])

k = 1
print(data_handler.has_next())
while data_handler.has_next() and k <= 100:
    next_row = data_handler.get_next()

    print(next_row)

    k += 1
