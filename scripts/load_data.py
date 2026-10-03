import requests
import boto3
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import time

ENV_PATH = os.path.join(os.path.dirname(__file__), "../.env")

load_dotenv(ENV_PATH)

# Config
ALPHA_VANTAGE_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
AWS_BUCKET = os.getenv("AWS_BUCKET")
SYMBOL = ["AAPL", "MSFT", "GOOGL", "JPM", "TSLA"]

def fetch_stock_data(symbol):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "compact",
        "apikey": ALPHA_VANTAGE_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if "Time Series (Daily)" not in data:
        raise ValueError(f"Unexpected response for {symbol}: {data}")
    
    return data

def land_to_s3(data, symbol):
    if not data or "Time Series (Daily)" not in data:
        raise ValueError("Refusing to land invalid/empty data to S3")
    s3 = boto3.client("s3")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    key = f"raw/{symbol}/{timestamp}.json"
    
    s3.put_object(
        Bucket=AWS_BUCKET,
        Key=key,
        Body=json.dumps(data),
        ContentType="application/json"
    )
    print(f"Landed: s3://{AWS_BUCKET}/{key}")
    return key

def main():
    for symbol in SYMBOL:
        print(f"Fetching {symbol}...")
        try:
            data = fetch_stock_data(symbol)
            print(f"Got {len(data['Time Series (Daily)'])} days of data")
            land_to_s3(data, symbol)
        except ValueError as e:
            print(f"Skipping {symbol} due to error: {e}")
            continue

        time.sleep(12)
        
    print("\nAll symbols processed.")
    # Print first 3 days so you can see the schema
    days = list(data["Time Series (Daily)"].items())[:3]
    for date, values in days:
        print(f"\n{date}: {values}")

if __name__ == "__main__":
    main()