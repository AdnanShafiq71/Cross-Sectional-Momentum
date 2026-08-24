import yfinance as yf
import pandas as pd

tickers = pd.read_csv("data/tickers.csv")

all_data = []

for ticker in tickers["Ticker"]:
    print(f"Downloading {ticker}...")

    data = yf.download(
        ticker,
        start="2021-01-01",
        end="2026-01-01",
        auto_adjust=True
    )

    data.columns = data.columns.get_level_values(0)
    data = data.reset_index()
    data["Ticker"] = ticker

    data = data[
        ["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]
    ]

    all_data.append(data)

    combined_data = pd.concat(all_data, ignore_index=True)

    combined_data.to_csv("data/market_data.csv", index=False)