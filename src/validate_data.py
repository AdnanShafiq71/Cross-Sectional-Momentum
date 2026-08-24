import pandas as pd

tickers = pd.read_csv("data/tickers.csv")

data = pd.read_csv("data/market_data.csv")

print("Number of rows:", len(data))
print("Number of stocks:", data["Ticker"].nunique())

print("\nMissing values:")
print(data.isnull().sum())

print("\nDuplicate rows:", data.duplicated().sum())

print("\nDuplicate Date-Ticker combinations:",
      data.duplicated(subset=["Date", "Ticker"]).sum())

expected_tickers = set(tickers["Ticker"])
actual_tickers = set(data["Ticker"])

missing_tickers = expected_tickers - actual_tickers

print("\nMissing tickers:")
print(missing_tickers)

print("\nDuplicate tickers in input:")
print(tickers[tickers["Ticker"].duplicated(keep=False)])