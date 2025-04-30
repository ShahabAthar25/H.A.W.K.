import os
from datetime import datetime, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

TIINGO_TOKEN = os.environ.get("TIINGO_TOKEN")

symbol = 'eurusd'
end_date = datetime.now()
start_date = end_date - timedelta(days=60)

start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

url = f"https://api.tiingo.com/tiingo/fx/{symbol}/prices"

params = {
    'startDate': start_date_str,
    'endDate': end_date_str,
    'resampleFreq': '15min',
    'format': 'json',
    'token': TIINGO_TOKEN
}
headers = {"Content-Type": "application/json"}

response = requests.get(
    url,
    params=params,
    headers=headers,
)

if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)
    df = df.drop("ticker", axis=1)
    renamed_col = {"date": "timestamp", "open": "Open", "high": "High", "low": "Low", "close": "Close"}
    df = df.rename(columns=renamed_col)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    print(df)
else:
    print(f"Error fetching data: {response.status_code} - {response.text}", response.status_code)
