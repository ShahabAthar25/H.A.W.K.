from dotenv import load_dotenv

from core import data_handler
from core.data_handler import DataHandler
from core.portfolio import Portfolio

load_dotenv()

group_config = {
    "Forex": ["GBPUSD"],
}

portfolio = Portfolio(10_000, group_config)

symbols = portfolio.get_symbols_data_format()

data_handler = DataHandler(symbols)
print(data_handler.data)
