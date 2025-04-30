from dotenv import load_dotenv

from core.engine import Engine

load_dotenv()

group_config = {
    "Crypto": ["BTC/USD"],
}

symbols = ["BTC/USD"]
initial_balance = 10_000

engine = Engine(symbols, group_config, initial_balance)
engine.run()
