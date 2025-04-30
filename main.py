from dotenv import load_dotenv

from core.engine import Engine

load_dotenv()

group_config = {
    "Crypto": ["BTC/USD", "ETH/USD", "SOL/USD"],
    "Forex": ["EURUSD", "GBPUSD"]
}

initial_balance = 10_000

engine = Engine(group_config, initial_balance)
engine.run()
