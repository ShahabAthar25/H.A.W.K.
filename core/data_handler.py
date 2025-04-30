import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import requests
from alpaca.data.historical import (CryptoHistoricalDataClient,
                                    StockHistoricalDataClient)
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

CURRENT_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = CURRENT_DIR / "data"


class DataHandler:
    def __init__(self, symbols: Dict[str, List], interval: str = "15m") -> None:
        self.symbols = symbols
        self.interval = interval
        self.data: Dict[str, pd.DataFrame] = {}
        self.index = 0
        self.max_index = 0
        self.total = {}

        self.ALPACA_API_KEY = os.environ.get("APCA_API_KEY")
        self.ALPACA_API_SECRET = os.environ.get("APCA_API_SECRET")
        self.TIINGO_TOKEN = os.environ.get("TIINGO_TOKEN")

        self.stock_client = StockHistoricalDataClient(
            self.ALPACA_API_KEY, self.ALPACA_API_SECRET
        )
        self.crypto_client = CryptoHistoricalDataClient()

        DATA_DIR.mkdir(parents=True, exist_ok=True)

        self.init_data()

    def map_interval(self) -> TimeFrame:
        if self.interval == "15m":
            return TimeFrame(15, TimeFrameUnit.Minute)
        elif self.interval == "1h":
            return TimeFrame(1, TimeFrameUnit.Hour)
        elif self.interval == "1d":
            return TimeFrame(1, TimeFrameUnit.Day)
        else:
            raise ValueError(f"Unsupported interval: {self.interval}")

    def fetch_data(self, symbol: str, asset_type: str) -> pd.DataFrame:
        filename = DATA_DIR / f"{symbol.replace("/", "-")}-{self.interval}.csv"
        if filename.exists():
            return pd.read_csv(
                filename, parse_dates=["timestamp"], index_col="timestamp"
            )

        print(f"Fetching {asset_type} data for {symbol}...")
        tf = self.map_interval()

        end_date = datetime.now() - timedelta(days=5)

        if asset_type == "crypto":
            request = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=tf,
                end=end_date.date(),
                start="2021-04-01",
            )
            bars = self.crypto_client.get_crypto_bars(request).df
        elif asset_type == "equities":
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=tf,
                end=end_date.date(),
                start="2018-04-01",
            )
            bars = self.stock_client.get_stock_bars(request).df
        elif asset_type == "forex":
            df = self.fetch_forex_data(symbol)
            df.to_csv(filename)
            return df
        else:
            raise ValueError(f"Unknown asset type: {asset_type}")

        bars = bars.copy()
        bars = bars.reset_index()
        bars = bars[["timestamp", "open", "high", "low", "close", "volume"]]
        bars = bars.set_index("timestamp")
        bars.to_csv(filename)

        return bars

    def fetch_forex_data(self, symbol: str, max_lookbacks: int = 3) -> pd.DataFrame:
        end_date = datetime.now()
        lookback_days = 50
        start_date = end_date - timedelta(days=lookback_days)

        max_lookback_date = end_date - timedelta(days=365 * max_lookbacks)

        url = f"https://api.tiingo.com/tiingo/fx/{symbol}/prices"
        headers = {"Content-Type": "application/json"}

        all_data = []

        while start_date >= max_lookback_date:
            print(f"Fetching data from {start_date.date()} to {end_date.date()}")

            params = {
                "startDate": start_date.date(),
                "endDate": end_date.date(),
                "resampleFreq": "15min",
                "format": "json",
                "token": self.TIINGO_TOKEN,
            }

            response = requests.get(url, params=params, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if not data:
                    print(
                        f"No data returned for {start_date.date()} to {end_date.date()}"
                    )
                    break

                df = pd.DataFrame(data).drop("ticker", axis=1)
                df = df.rename(
                    columns={
                        "date": "timestamp",
                    }
                )
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df.set_index("timestamp", inplace=True)
                all_data.append(df)

                end_date = start_date
                start_date = end_date - timedelta(days=lookback_days)
            else:
                print(f"Error fetching data: {response.status_code} - {response.text}")
                time.sleep(1)
                continue

        if all_data:
            return pd.concat(all_data).sort_index()
        else:
            raise Exception("Failed to fetch any forex data after multiple attempts.")

    def init_data(self) -> None:
        for group, symbols in self.symbols.items():
            asset_type = group.lower()
            for symbol in symbols:
                df = self.fetch_data(symbol, asset_type)
                df = df.sort_index()
                self.data[symbol] = df
                self.total[symbol] = len(df)

        self.max_index = max(self.total.values())

    def get_next(self):
        next_data: Dict[str, Optional[pd.Series]] = {}

        for symbol, df in self.data.items():
            if self.index < self.total[symbol]:
                next_data[symbol] = df.iloc[self.index]

            else:
                next_data[symbol] = None

        self.index += 1
        return next_data

    def reset(self):
        self.index = 0

    def has_next(self):
        return self.index <= self.max_index
