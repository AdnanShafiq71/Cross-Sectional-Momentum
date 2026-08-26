import yfinance as yf
import pandas as pd


START_DATE = "2021-01-01"
END_DATE = "2026-01-01"

tickers = pd.read_csv("data/tickers.csv")

all_data = []

for ticker in tickers["Ticker"]:
    print(f"Downloading {ticker}...")

    data = yf.download(
        ticker,
        start=START_DATE,
        end=END_DATE,
        auto_adjust=True,
        progress=False
    )

    if data.empty:
        print(f"WARNING: No data returned for {ticker}")
        continue

    data.columns = data.columns.get_level_values(0)
    data = data.reset_index()

    data["Ticker"] = ticker

    data = data[
        ["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]
    ]

    all_data.append(data)


combined_data = pd.concat(all_data, ignore_index=True)

combined_data = combined_data.sort_values(
    ["Ticker", "Date"]
).reset_index(drop=True)

combined_data.to_csv(
    "data/market_data.csv",
    index=False
)

print("\nData download complete.")
print(f"Rows: {len(combined_data)}")
print(f"Stocks: {combined_data['Ticker'].nunique()}")

print("\nDownloading SPY (S&P 500 benchmark)...")

spy_data = yf.download(
    "SPY",
    start=START_DATE,
    end=END_DATE,
    auto_adjust=True,
    progress=False
)

spy_data.columns = spy_data.columns.get_level_values(0)
spy_data = spy_data.reset_index()
spy_data = spy_data[["Date", "Close"]]
spy_data = spy_data.rename(columns={"Close": "SPY_Close"})

spy_data.to_csv("data/spy_data.csv", index=False)

print("SPY benchmark data saved to data/spy_data.csv")