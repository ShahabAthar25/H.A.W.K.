import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit

load_dotenv()

API_KEY = os.environ.get("APCA_API_KEY_ID")
API_SECRET = os.environ.get("APCA_API_SECRET_KEY")
LIVE_BASE_URL = "https://paper-api.alpaca.markets/v2"

api = REST(API_KEY, API_SECRET, base_url=LIVE_BASE_URL)

# Define the symbol and timeframe
symbol = "AAPL"
timeframe = TimeFrame(5, TimeFrameUnit.Minute)

# Calculate the start date (7 years ago from today)
end_date = datetime.now() - timedelta(days=1)
start_date = end_date - timedelta(
    days=6
)  # Approximation, doesn't account for leap years precisely

print(
    f"Attempting to fetch 5-minute historical data for {symbol} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
)

all_bars = []
limit_per_request = 10000  # Maximum limit per API call

try:
    for bar in api.get_bars(
        symbol, timeframe, start=start_date.date(), end=end_date.date()
    )._raw:
        all_bars.append(bar)

        if len(all_bars) % limit_per_request == 0:
            print(f"Fetched {len(all_bars)} bars so far...")

    import pandas as pd

    df = pd.DataFrame(all_bars)
    print("\nDataFrame Head:")
    print(df.head())

except Exception as e:
    print(f"An error occurred: {e}")
    print(
        "Please check your API keys, base URL, symbol, and ensure you have the necessary data subscription."
    )
