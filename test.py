from core.data_handler import DataHandler

symbols = ["BTC-USD"]
data_handler = DataHandler(symbols)

data = data_handler.get_next()
print(data_handler.head())
