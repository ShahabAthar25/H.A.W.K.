import requests
import lzma
import struct
import pandas as pd
from datetime import datetime, timedelta

BASE_URL = "https://datafeed.dukascopy.com/datafeed/{symbol}/{year}/{month}/{day}/{hour}h_ticks.bi5"

def download_bi5(symbol: str, date: datetime) -> bytes:
    url = BASE_URL.format(
        symbol=symbol.upper(),
        year=date.year,
        month=f"{date.month - 1:02d}",  # zero-based month
        day=f"{date.day:02d}",
        hour=date.hour
    )
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return lzma.decompress(response.content)
    return None

def parse_bi5(data: bytes) -> pd.DataFrame:
    records = []
    record_size = 20
    for i in range(0, len(data), record_size):
        chunk = data[i:i+record_size]
        if len(chunk) < 20:
            continue
        millis, ask, bid, ask_vol, bid_vol = struct.unpack('>Qffff', chunk)
        timestamp = pd.to_datetime(millis / 1000.0, unit='s')
        price = (ask + bid) / 2  # Mid price
        volume = ask_vol + bid_vol
        records.append((timestamp, price, volume))
    return pd.DataFrame(records, columns=["datetime", "price", "volume"])

def fetch_ticks(symbol: str, start: datetime, end: datetime) -> pd.DataFrame:
    current = start.replace(minute=0, second=0, microsecond=0)
    all_data = []

    while current <= end:
        raw_data = download_bi5(symbol, current)
        if raw_data:
            df = parse_bi5(raw_data)
            df = df[(df["datetime"] >= start) & (df["datetime"] <= end)]
            all_data.append(df)
        current += timedelta(hours=1)

    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

def to_ohlcv(df: pd.DataFrame, interval: str = "1T") -> pd.DataFrame:
    df = df.set_index("datetime")
    ohlcv = df.resample(interval).agg({
        "price": ["first", "max", "min", "last"],
        "volume": "sum"
    })
    ohlcv.columns = ["open", "high", "low", "close", "volume"]
    return ohlcv.dropna()

# Example usage
if __name__ == "__main__":
    symbol = "EURUSD"
    start = datetime(2024, 4, 25, 9, 0)
    end = datetime(2024, 4, 25, 11, 0)

    ticks_df = fetch_ticks(symbol, start, end)
    ohlcv_df = to_ohlcv(ticks_df, interval="1T")  # 1-minute OHLCV
    print(ohlcv_df.head())
