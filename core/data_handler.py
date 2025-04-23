from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import yfinance as yf

CURRENT_DIR = Path(__file__).parent.parent.resolve()


class DataHandler:
    def __init__(self, symbols: List[str]) -> None:
        self.symbols = symbols
        self.data: Dict[str, pd.DataFrame] = {}
        self.index = 0
        self.max_index = 0
        self.total = {}

        self.init_data()

    def fetch_data(self, symbol, interval="1h") -> pd.DataFrame:
        symbol_path = f"{CURRENT_DIR}/data/{symbol}-{interval}.csv"

        if Path(symbol_path).exists():
            return pd.read_csv(symbol_path, index_col=0, parse_dates=True)

        else:
            print(f"Downloading symbol: {symbol}")
            now = datetime.now()
            start = now - timedelta(days=730)
            ticker = yf.Ticker(symbol)
            data = ticker.history(interval="1h", start=start)
            data.to_csv(symbol_path)
            return data

    def init_data(self):
        for symbol in self.symbols:
            self.data[symbol] = self.fetch_data(symbol)
            self.total[symbol] = len(self.data[symbol])

    def get_next(self):
        next_data: Dict[str, Optional[pd.Series]] = {}

        for symbol, df in self.data.items():
            if self.index < self.total[symbol]:
                next_data[symbol] = df.iloc[self.index]

            else:
                next_data[symbol] = None

        self.index += 1
        return next_data

    def has_next(self):
        return self.index <= self.max_index
